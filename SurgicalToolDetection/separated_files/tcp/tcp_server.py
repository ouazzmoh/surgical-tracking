import socket
import threading
import time

# Variables for holding information about connections
connections = []
total_connections = 0

# Client class, new instance created for each connected client
# Each instance has the socket and address that are associated with items
# Along with an assigned ID and a name chosen by the client
class Client(threading.Thread):
    def __init__(self, socket, address, id, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.name = name
        self.signal = signal
    
    def __str__(self):
        return str(self.id) + " " + str(self.address)
    
    def run(self):
        while self.signal:
            try:
                # Send 3D point data (x, y, z) every second
                for num in range(1, 110):
                    # Break the loop if num reaches 10
                    if num == 110:
                        break

                    data = f"{num * 1.1:.1f} {num * 1.1:.1f} {num * 1.1:.1f}".encode("utf-8")
                    self.socket.sendall(data)
                    time.sleep(1)
                    
                # Close the socket and stop the thread after reaching 10
                self.socket.close()
                self.signal = False
                connections.remove(self)
                break

            except:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                connections.remove(self)
                break

# Wait for new connections
def new_connections(socket):
    while True:
        sock, address = socket.accept()
        global total_connections
        connections.append(Client(sock, address, total_connections, "Name", True))
        connections[len(connections) - 1].start()
        print("New connection at ID " + str(connections[len(connections) - 1]))
        total_connections += 1

def main():
    # Get host and port
    host = "127.0.0.1"
    port = 5555

    # Create a new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    # Create a new thread to wait for connections
    new_connections_thread = threading.Thread(target=new_connections, args=(sock,))
    new_connections_thread.start()

main()
