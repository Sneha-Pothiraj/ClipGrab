"""
CN LAB PACKAGE
Code by: SNEHA G
Section: Client
Topic: Downloading from multiple servers using TCP + File Segmentation + File Recombination
"""
# import statements
from socket import *
from threading import *  # Import threading to introduce multiple servers
from time import *  # To calculate the running time of the program
import os


# Class MultipleThread to create multiple threads for multiple servers
class MultipleThread(Thread):
    global ptr
    global fname

    def __init__(self, port, serverNo):

        Thread.__init__(self)
        self.port = port  # Sets the port number to the current port
        self.serverNo = serverNo  # tells the number of the current connected server

    def run(self):

        while True:

            global ptr
            global fname
            global bytes_sent
            global fragment_count
            global path
            global rest
            global total_bytes_sent
            global start
            global start_time
            global download_speed
            global stop
            global total_bytes
            global fragment_time

            threadLock.acquire()
            # Creating socket
            client_socket = socket(AF_INET, SOCK_STREAM)
            try:
                pointer_inner = ptr
                # connecting the socket with the server
                client_socket.connect((serverIP, self.port))
                print(client_socket.recv(1024).decode())
                client_socket.send(fname.encode())  # sending file name to the server
                print(client_socket.recv(1024).decode())

                file_status = (client_socket.recv(1024)).decode()  # recieving the file status whether it is available or not

                # If file is not found
                if file_status == "notfound":
                    print("Disconnecting")
                    exit()  # exiting the program
                    threadLock.release()  # releasing the server threads
                    client_socket.close()  # closing the client socket
                    break

                # printing the total number of fragments into which file is divided
                print("Number of segments into which the file is divided: ", fragment_count)

                # sending the pointer to the server which tells how many bytes of the file have been received
                client_socket.send(str(ptr).encode())

                global file_size
                # Receiving the file size
                file_size = int((client_socket.recv(1024)).decode())
                print("File size = ", file_size)  # printing the file size

                # changing from string to integer
                fragment_count = int(fragment_count)

                # Sending the number of fragments to the server
                client_socket.send(str(fragment_count).encode())
                fragmentSize = file_size // fragment_count  # calculating size of each segment

                if file_size % 3 == 1:
                    total_bytes_sent += 1 / fragment_count
                elif file_size % 3 ==2:
                    total_bytes_sent +=2 / fragment_count

                # sending server number
                client_socket.send(str(self.serverNo).encode())

                # Checking files is greater than 5 MB
                if 5242880 <= file_size:
                    # Sending the file
                    recv_file = open(path, "ab")  # opening the file in the specified path

                    print("\nReceiving...\n")
                    sleep(2)

                    while True:
                        sleep(3)
                        rest += 3
                        start_recv_time = time()
                        if (self.serverNo == 1 and start == False):
                            start_time = start_recv_time

                        # receiving the file from the server
                        data = client_socket.recv(fragmentSize)
                        if not data:
                            break

                        sleep(2)
                        # measuring file/segment transferring time
                        stop_time = time()

                        if (self.serverNo == 1 and start == False):
                            fragment_time = stop_time - start_recv_time
                        else:
                            fragment_time = (stop_time - start_recv_time) - (rest - 3)

                        # writing the received data in the opened file
                        recv_file.write(data)
                        # getting the values stored in the variables
                        bytes_sent[self.serverNo - 1] += len(data)
                        total_bytes_sent += len(data)
                        download_time = stop_time - start_time
                        download_speed[self.serverNo - 1] = round((len(data) / download_time) / 1024, 3)
                        start = True

                    # Closing the file
                    recv_file.close()
                    print("CLosing file")
                    print("The required fragment is received successfully")
                    threadLock.release()

                # If file is less than 5 MB
                else:
                    print("File size less than 5 MB")
                    print("Closing!!!!")
                    sleep(5)
                    threadLock.release()
                    client_socket.close()
                    exit()
                break

            except:
                global server_ports

                # if the client server connection is disrupted
                print("Connection lost to the server " + str(self.serverNo))
                # the program will try to reconnect to the currently available ports
                print("\nReconnecting...\n")
                active_server_ports = []

                # Redistributing among active servers
                active_server_ports = ActiveServersCount(server_ports)
                fragment_count = 0

                # number of fragments will be equal to the aount of servers available
                fragment_count = len(active_server_ports)

                # If no server is active then program exits
                if len(active_server_ports) == 0:
                    print("Connection left: None")
                    print("Exiting...")
                    sleep(5)
                    exit()  # exiting the program
                    threadLock.release()
                    client_socket.close()  # closing the client socket

                # If active servers are present program will start again
                else:
                    ptr = 0
                    total_bytes_sent = 0
                    if os.path.exists(path):
                        os.remove(
                            path)  # if a half downloaded file already exits in that directory it will be deleted and will be redistributed among available servers
                    print("file deleted")
                    threadLock.release()
                    print("Connected to server(s) at port(s): ", *active_server_ports)

                    # Creating threads again
                    BeginThreads(active_server_ports)
                    break


# User defined functions

def ActiveServersCount(total_ports):
    global active_servers
    active_servers = []
    for x in total_ports:
        check_socket = socket(AF_INET, SOCK_STREAM)
        result = check_socket.connect_ex((serverIP, x))  # checking if the port is active
        if result == 0:
            active_servers.append(x)  # appending the active port into the list
        check_socket.close()
    return active_servers  # returning the list of active ports


def CheckPointer(filelocation):
    if os.path.exists(filelocation):
        downloaded_size = os.stat(filelocation).st_size  # getting the size in bytes of the downloaded file
        print(downloaded_size / 1024, " KBs already downloaded")
        return downloaded_size
    else:
        return 0


def BeginThreads(ports_accessible):
    global fragment_count
    fragment_count = 0
    for x in range(0, len(ports_accessible)):
        newThread = MultipleThread(ports_accessible[x], x + 1)
        newThread.start()  # this transfers the action to the run function of the class
        fragment_count += 1  # increasing number of fragments (it will be equal to the number of servers)
        Threads.append(newThread)


def display():
    global total_bytes_sent
    global file_size
    stop = False
    if total_bytes_sent == file_size:
        sleep(1)
        stop = True

    total_bytes_delivered = 0
    os.system('cls')
    fragmentSize = int(file_size) // fragment_count
    for s in range(0, len(ports_accessible)):
        total_bytes[s] = fragmentSize
        total_bytes_delivered += bytes_sent[s]
        # printing format
        print("Server ", s + 1, ": ", "<", bytes_sent[s], ">", "/", "<", total_bytes[s], ">", ", downloading speed: ",
              "<", download_speed[s], ">", "  kb/s\n")
    if start == True:
        complete_file_speed = round((total_bytes_delivered / fragment_time) / 1024, 3)
        # printing format
        print("Total: ", "<", total_bytes_delivered, ">", "/", "<", file_size, ">", " , downloading speed: ", "<",
              complete_file_speed, ">", "  kb/s\n")
    else:
        print("Total: ", "<", total_bytes_delivered, ">", "/", "<", file_size, ">", " , downloading speed: ", "<", 0,
              ">", "  kb/s\n")
    if stop == True:
        print("Download completed")  # exiting program
    else:
        sleep(interval)
        display()  # recursion


# Main program

interval = 3  # the interval for the client
location = "C:\\Users\\Pikachu\\Desktop\\Computer-Networks-main\\client"  # output location of the file received
serverIP = gethostname()  # IP address of the server
server_ports = [9990, 9991, 9992]  # list of server ports
resume = "Y"  # whether to resume the disrupted download or not

fragment_count = 0  # Number of fragments into which the file will be divided initially

total_bytes_sent = 0  # Total number of bytes received
bytes_sent = [0, 0, 0]  # Number of bytes transferred to the client
total_bytes = [0, 0, 0]  # List of bytes for all the servers
download_speed = [0, 0, 0]  # Downlaoding speed
start = False
stop = False
rest = 0
start_time = 0  # starting time of the file transfer

Threads = []  # variable for threads
file_size = "0"  # variable for file size
threadLock = Lock()  # Locking the threads

# Function call to get the list of all active ports/servers
ports_accessible = ActiveServersCount(server_ports)

if len(ports_accessible) < 3:
    print("\nConnection to port(s) ", *(list(set(server_ports) - set(ports_accessible))), "due to unavailability")

print("Connected to server(s) at port(s): ", *ports_accessible)

# Getting the name of the file from the user
fname = input("Enter the name of the MP4 file (with .mp4): ")

# joining the output path and file name to get a full name with extension
path = os.path.join(location, fname)

# calling the ptr check function to check whether a file already exist in the path specified
ptr = CheckPointer(path)

# catering the resumption part
if ptr == 0:
    print("\nStarting download...\n")
if ptr != 0:
    print("\nFile found of size: ", os.stat(path).st_size)
    if resume == "N" or resume == "n":
        os.remove(path)
        ptr = 0
        print("\nFile removed, starting from 0%")
    else:
        print("\nResuming...\n")

# Starting to createthreads
BeginThreads(ports_accessible)

# Creating threads to display the output
displayThread = Thread(target=display())
displayThread.start()

# stopping the execution of the program as long as the threads are running
for i in Threads:
    i.join()
displayThread.join()

# Printing the rest of the statements
if os.path.exists(path):

    if file_size == os.stat(path).st_size - ptr or file_size - 1 == os.stat(
            path).st_size - ptr or file_size - 2 == os.stat(path).st_size - ptr or file_size - 3 == os.stat(
            path).st_size - ptr:
        print("The .mp4 file has been successfully received")

    if file_size != 0:
        print("The location of the received file: ", path)  # location of the receieved file
        print("List of ports connected on this client: ", *ActiveServersCount(server_ports))  # list of connected ports
        print("Your file has been received successfully! Thankyou !")