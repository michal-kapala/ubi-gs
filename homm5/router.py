import socket, sys, os
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
import gsm

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
      while True:
        data = connection.recv(4096)
        if data:
          req = gsm.Message(data)
          print(req)
          connection.sendall(data)
        else:
          print("No more data from", client_address)
          break
    finally:
      connection.close()

if __name__ == "__main__":
    start_server()
