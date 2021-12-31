"""
CN LAB PACKAGE
Code by: SNEHA G
Section: Server 3
Topic: Downloading large mp4 file from multiple servers using TCP + File Segmentation + File Recombination
"""
#import statements


from socket import *  #import socket module
from time import *    #import time module 
import os             #import OS

start_time = time()   #Starting time counter.

SERVER_IP = ""        #Connect to localhost
SERVER_PORT = 9992  #Port dedicated to respected servers
location = "C:\\Users\\Pikachu\\Desktop\\Computer-Networks-main\\server"

# Connection And binding of socket
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)

bytePosition = 0
fragmentList = []

while True:
    print('\nThe server3 is ready for the connection...')
    conn, clientAddr = server_socket.accept() #First we test to see if the server is available
    conn.close()
    conn, clientAddress = server_socket.accept() #Connection established with client
    print("\nConnected to the client: ", clientAddress)

    try:
        status = "Connected"
        print("Port No: " + str(SERVER_PORT) + "\nStatus: " + status + "\nEnter CTRL+C to quit\n")        #Print the current state of the server
        sleep(5)

        conn.send("Retrieving the name of file.... ".encode())

        fileName = (conn.recv(1024)).decode() #Recieving filename from the client
        path = os.path.join(location, fileName)
        fileExists = os.path.exists(path) #Checking for the file in directory
        if fileExists == True: #If file exists inform client
            conn.send(("File Found. ").encode())
            conn.send(("found").encode())
        if fileExists == False: #if file does not exist, inform client
            conn.send(("File Not Found, please reconnect and try again.").encode())
            conn.send(("notfound").encode())
            conn.close()
            continue #Restart the loop after closing connection
            

        pointer_position = (conn.recv(1024)).decode() #Recieve pointer from client in case a chunk of file is present

        if pointer_position == "0": #IF FILE DOES NOT ALREADY EXIST AT THE CLIENT END
            #data or information about the filesize
            data = os.stat(path)
            file_size = data.st_size
        else:
            file_size= int(os.stat(path).st_size)-int(pointer_position)#SET NEW POINTER POSITION AND SET NEW FILE SIZE

        conn.send(str(file_size).encode()) #Send file size to the client
        number_of_fragments = int((conn.recv(1024)).decode()) #Recieve Number of Fragments
        fragmentSize = file_size // number_of_fragments #Calculating fragment size by dividing file into fragments of equal size 
        send_file = open(path, 'rb')

        if pointer_position != "0": #IF pointer is not zero....Read the file to catch up to the pointer
            send_file.read(int(pointer_position))

        # dividing the file into a number of fragments
        for seg in range(0, number_of_fragments): #For dividing the file into segments(fragments)
            send_file.seek(bytePosition, 0)
            fragmentList.append(send_file.read(fragmentSize))
            bytePosition = bytePosition + fragmentSize #Update byte position with fragment size
        print("File segmented.\n")

        #conn.send("Enter the required fragment number: ".encode())
        fragment_number = int((conn.recv(1024)).decode()) #recieve fragment number

        print("Currently connected client is connected to ", number_of_fragments, " servers.")
        print("Port on which this server is connected: ", SERVER_PORT)
        path = os.getcwd()
        print("Location of the required file:", path)
        print("\nSending...")
        conn.sendall(fragmentList[fragment_number - 1])
        print("\nThe requested segment has been successfully sent")
        send_file.close()
        conn.close()

        seconds = time() - start_time
        print("Running time of this server:", seconds)

    except KeyboardInterrupt:
        print("Connection closed manually")
        break

    except:
        print("Connection closed due to an error!!!")
        break

status = "Disconnected"
print("Port "+str(SERVER_PORT)+" Status: " +status)
