# Computer Networks

## The OSI Model and TCP/IP Architecture
The Open Systems Interconnection (OSI) model defines 7 conceptual layers:
1. Physical: Transmission of raw bit streams over physical media (Cables, Fiber, Radio).
2. Data Link: Reliable node-to-node framing, MAC addressing, error detection (Ethernet, Wi-Fi).
3. Network: Logical packet routing and host addressing (IP, ICMP, ARP).
4. Transport: End-to-end host communication, segmentation, flow control (TCP, UDP).
5. Session: Dialog and session management.
6. Presentation: Data syntax, translation, compression, and encryption (TLS/SSL).
7. Application: User-facing network protocols (HTTP, DNS, FTP, SMTP).

## TCP vs UDP Protocols
- Transmission Control Protocol (TCP): Connection-oriented, reliable, ordered, byte-stream protocol. Implements error checking, retransmission of lost segments, flow control (sliding window), and congestion control (Slow Start, Congestion Avoidance).
- User Datagram Protocol (UDP): Connectionless, lightweight, unreliable datagram protocol. Low latency overhead, suitable for DNS, real-time gaming, and video streaming.

## TCP Handshakes
- 3-Way Connection Handshake:
  1. Client sends SYN (Synchronize sequence number).
  2. Server responds with SYN-ACK (Acknowledges client and provides server sequence number).
  3. Client replies with ACK. Connection is established.
- 4-Way Connection Teardown:
  1. Client sends FIN.
  2. Server responds with ACK (half-close).
  3. Server sends FIN when finished transmitting.
  4. Client responds with ACK and enters TIME_WAIT state.
