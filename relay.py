import logging
import tornado.httpserver
import tornado.websocket
from tornado import gen
from tornado.websocket import websocket_connect

"""Configuration"""
SERVER_PORT = 1414
DASHBOARD_PORT = 8889
REQUEST_TYPES = ["time"]
LOG_FILE = "relay.log"


class StreamerHandler(tornado.web.RequestHandler):
	"""Streamers

	Handles requests from streamers for relay
	"""
	buff = {} #: Message buffer

	@tornado.web.asynchronous
	def get(self, channel):
		"""Request a relay

		:param channel: Register relay to this channel
		"""
		logging.info("Streamer {0} relaying to {1}".format(self.request.remote_ip, channel))
		self.buff[channel] = []
		self.consume(self.request.remote_ip, channel)
		self.finish("Relaying")

	@gen.coroutine
	def consume(self, ip, channel):
		"""Consume dashboard message stream

		:param channel: Messages belong to this channel
		"""
		url = "ws://{0}:{1}/game/1/{2}".format(ip, DASHBOARD_PORT, ",".join(REQUEST_TYPES))
		logging.info("Connecting to {0}".format(url))
		conn = yield websocket_connect(url)
		while True:
			message = yield conn.read_message()
			if message is None: break
			self.buff[channel].append(message)

			# Broadcast message to viewers
			if channel in ViewerHandler.viewers.keys():
				for viewer in ViewerHandler.viewers[channel]:
					viewer.write_message(message, binary = False)


class ViewerHandler(tornado.websocket.WebSocketHandler):
	"""Viewers

	Handles requests from viewers
	"""
	viewers = {} #: Viewers on each channel

	def check_origin(self, origin):
		return True

	def open(self, channel):
		"""Connection opened

		:param channel: Subscribe to messages from this channel
		"""
		self.channel = channel
		logging.info("Viewer requested {0}".format(channel))

		# Record viewer
		if channel not in self.viewers.keys():
			self.viewers[channel] = []
		self.viewers[channel].append(self)

		# Send channel buffer to viewer
		if channel in StreamerHandler.buff.keys():
			for message in StreamerHandler.buff[channel]:
				self.write_message(message, binary = False)

	def on_close(self):
		"""Connection closed"""
		logging.info("Viewer disconnected from {0}".format(self.channel))
		if self in ViewerHandler.viewers[self.channel]:
			ViewerHandler.viewers[self.channel].remove(self)


"""App Entry"""
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

application = tornado.web.Application([
		(r"/streamer/([a-z]+)", StreamerHandler),
		(r"/viewer/([a-z]+)", ViewerHandler)
	]
)

logging.info("Listening on port {0}".format(SERVER_PORT))
application.listen(SERVER_PORT)
tornado.ioloop.IOLoop.instance().start()