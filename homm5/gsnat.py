import socket
from srp import Segment

SERVER_ADDRESS = ('localhost', 7781)
RESPONSE_DATA = bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09])
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SERVER_ADDRESS)

print(f"GSNAT server is listening on port {SERVER_ADDRESS[1]}")

while True:
    data, address = sock.recvfrom(1024)
    req = Segment(data)
    print(req)
    sock.sendto(RESPONSE_DATA, address)
    print(f"Sent response to {address}")
