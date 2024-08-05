import socket

SERVER_ADDRESS = ('localhost', 7780)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SERVER_ADDRESS)
print(f"CD Key server is listening on port {SERVER_ADDRESS[1]}")

while True:
  data, address = sock.recvfrom(1024)
  print(f"Received {len(data)} bytes from {address}:")
  print(data.hex(' '))
