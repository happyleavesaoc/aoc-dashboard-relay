# Dashboard Relay Server

- Reads inbound data from streamers
- Broadcasts data to viewers

Streamer workflow:
- Streamer requests relay
- Server requests data
- Streamer sends data

Viewer workflow:
- Viewer requests relay
- Server sends data

### Architecture
The relay server is run on [tornado](https://github.com/tornadoweb/tornado), an asynchronous networking library and web framework. It allows reliable scaling to thousands of long-lived client connections. It also offers load balancing solutions if necessary. Using a relay server offloads the bandwidth requirements of multiple viewer connections to a server, rather than requiring the streamer to handle the connections.

Streamers initiate the relay by a GET request to /streamers/\<channel\>. Upon receipt, the relay server will attempt to connect to the local dashboard instance on the streamer's computer. If the streamer is behind a NAT, port 8889 must be forwarded. The dashboard's websocket server (also tornado-based) will stream messages to the relay (just as to any other client, like the local web page).

Viewers connect to the websocket at /viewers/\<channel\> to receive a message stream. The connection is generally established by client-side Javascript, but any sort of client could connect. This decouples the relay server from the display UI.

For each channel being relayed, the server will store a message buffer. All inbound messages are added to the buffer. New viewer connections will receive the contents of the channel's buffer, plus the remainder of the inbound messages in real-time.

### Bandwidth

Samples from Spectator Dashboard 2.4. Sizes in kb.

Game ID | Game Length | Players | MGZ Size | Stream Size | Message Count | Factor
--------|-------------|---------|----------|-------------|---------------|-------
1 | 00:49:16 | 8 | 2274 | 5772 | 22462 | 2.53
2 | 00:58:08 | 8 | 2841 | 6798 | 25752 | 2.39
3 | 00:44:44 | 2 | 1655 | 2250 | 10776 | 1.36
4 | 01:22:09 | 8 | 3650 | 7986 | 29407 | 2.18
5 | 00:55:25 | 8 | 2685 | 6551 | 25080 | 2.44

### Dependencies
 - [tornado 4.1](https://github.com/tornadoweb/tornado)
 - [jsxcompressor](https://github.com/jsxgraph/jsxgraph/tree/master/JSXCompressor)
