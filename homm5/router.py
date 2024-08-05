import socket

SERVER_ADDRESS = ('localhost', 7777)

def start_server():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  print(f"Router service is listening on port {SERVER_ADDRESS[1]}")
  sock.bind(SERVER_ADDRESS)
  sock.listen(5)
    
  while True:
    connection, client_address = sock.accept()
    print(f"Connection from {client_address}")
    try:
      # Receive the data in chunks and retransmit it
      while True:
        data = connection.recv(4096)
        print(f"Received {len(data)} bytes from {client_address}:")
        print(data.hex(' '))
        if data:
          print("Sending data back to the client")
          connection.sendall(data)
        else:
          print("No more data from", client_address)
          break
    finally:
      connection.close()

if __name__ == "__main__":
    start_server()
