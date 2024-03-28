#main.py
import subprocess
import time

path = "/Users/hafizenursahbudak/Desktop/TUM 23:24 Winter/Computational Surgineering/tcp/"
def run_server():
    subprocess.run(['python', path + 'tcp_server.py'])

def run_client():
    subprocess.run(['python', path +'tcp_client.py'])

if __name__ == "__main__":
    # Run the server in a separate process
    server_process = subprocess.Popen(['python', path + 'tcp_server.py'])

    # Allow some time for the server to start before running the client
    time.sleep(2)

    # Run the client in a separate process
    client_process = subprocess.Popen(['python', path + '/tcp_client.py'])

    try:
        # Wait for both processes to finish
        server_process.wait()
        client_process.wait()
    except KeyboardInterrupt:
        # If the user interrupts, terminate both processes
        server_process.terminate()
        client_process.terminate()
