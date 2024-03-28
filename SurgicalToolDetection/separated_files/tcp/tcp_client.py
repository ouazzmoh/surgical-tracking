import socket
import threading
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Initialize lists to store received data for x, y, z coordinates
x_values = [100]  # Initial x-coordinate
y_values = [100]  # Initial y-coordinate
z_values = [100]  # Initial z-coordinate

# Create a lock to synchronize access to the shared data
data_lock = threading.Lock()

# Create a flag to signal disconnection
disconnected = False

# Create a figure and axis for 3D plotting
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the initial point
ax.scatter(x_values, y_values, zs=z_values, s=20, c='b', marker='o')
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')
ax.set_zlabel('Z Coordinate')
ax.set_title('3D Data Over Time')
ax.grid(True)

# Function to update the 3D plot in the animation
def update_plot(frame):
    global disconnected
    with data_lock:
        if disconnected:
            ani.event_source.stop()
            plt.close()
            return
        ax.clear()
        ax.scatter(x_values, y_values, zs=z_values, s=20, c='b', marker='o')
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_zlabel('Z Coordinate')
        ax.set_title('3D Data Over Time')
        ax.grid(True)

# Wait for incoming data from the server
def receive(socket, signal):
    global disconnected
    while signal:
        try:
            data = socket.recv(32)
            decoded_data = data.decode("utf-8")
            print(decoded_data)

            with data_lock:
                x, y, z = map(float, decoded_data.split())
                x_values.append(x)
                y_values.append(y)
                z_values.append(z)

        except:
            print("You have been disconnected from the server")
            disconnected = True
            signal = False
            break

# Get host and port
host = "127.0.0.1"
port = 5555

# Attempt connection to the server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
except:
    print("Could not make a connection to the server")
    input("Press enter to quit")
    sys.exit(0)

# Create a new thread to wait for data
receiveThread = threading.Thread(target=receive, args=(sock, True))
receiveThread.start()

# Create an animation to update the 3D plot
ani = FuncAnimation(fig, update_plot, interval=1000)

# Show the 3D plot
plt.show()

# Send data to the server
while True:
    message = input()
    sock.sendall(str.encode(message))
