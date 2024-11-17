import sys
import socket
from socket import SOL_SOCKET, SO_REUSEADDR
from packet import Packet
from argparse import ArgumentParser


class Client():
    #Initialize a Client instance with a specified port number.
    #[*] Parameters:
    #   -> port (int): The port number to connect to the server. If not provided, defaults to 6000.
    #[*] Returns: None
    def __init__(self, address:str = "127.0.0.1", port:int = 6000):
        # Provides descriptions of all of the commands
        self.commandsList = {"COMMANDS":"Show a list of commands",
                             "GET_CITY":"Provide a country and receive its capital city",
                             "GET_POPULATION":"Provide a country and receive its population",
                             "ADD_NEW_COUNTRY":"Provide a country and its capital city to add to the server's database",
                             "HEART": "Send a heartbeat to the server to verify connection",
                             "STOP": "Stop the program"}

        # Associates inputted commands with their respective functions
        self.commandsExecution = {"COMMANDS":self.printCommands,
                                  "GET_CITY":self.getCity,
                                  "GET_POPULATION":self.getPopulation,
                                  "ADD_NEW_COUNTRY":self.addNewEntry,
                                  "HEART":self.heartbeat,
                                  "STOP":self.stopProgram}

        # Configure port settings with arguments, if one is provided. Otherwise, default to 6000.
        parser = ArgumentParser()
        parser.add_argument("--port")
        parser.add_argument("--address")
        args = parser.parse_args()
        if(args.port):
            self.port = int(args.port)
        else:
            self.port = port
        if(args.address):
            self.address = str(args.address)
        else:
            self.address = str(address)

        self.clientSocket = socket.socket()
        self.bufferSize = 1024

        self.packet = Packet() # serves as a packet template to load and process received and transmitted packets


    #Attempts to establish a socket connection with the server using the provided configuration.
    #   -> If the connection is refused, it calls the stopProgram method with an appropriate error message.
    #   -> If the connection is successful, it prints a success message and enters the main client loop.
    #   -> In the main loop, it prompts the user to enter a command, executes the corresponding function,
    #      or prints an error message if the command is invalid.
    #[*] Parameters: None
    #[*] Returns: None
    def run(self):
        # Attempt a socket connection with provided configuration
        try:
            self.clientSocket.connect(("127.0.0.1", self.port))
        except ConnectionRefusedError as e:
            self.stopProgram("Connection refused. Ensure the server is running and port numbers are matching.", type(e).__name__)
        except OverflowError as e:
            self.stopProgram("Port number may be too high or too low. Ensure the port number is 0-65535", type(e).__name__)
        except OSError as e:
            self.stopProgram("Inputted IP Address is not valid in the current context. Ensure the IP address is correct and try again.", type(e).__name__)
        print("Connection successfully established with server!")

        # Main client loop to receive and execute commands
        self.printCommands()
        while(True):
            userInput = input("Enter command: ")
            self.commandsExecution[userInput.upper()]() if userInput.upper() in self.commandsExecution else print("Invalid command entered")


    #Transmits a message to the server using the established socket connection.
    #   -> This function generates a packet using the current packet template,
    #      sends the encoded message to the server, and handles any ConnectionResetError
    #      exceptions that may occur due to the server being forcibly closed.
    #[*] Parameters: None
    #[*] Returns: None
    def transmitMessage(self):
        message = self.packet.generatePacket()
        self.packet.emptyPacket()
        try:
            self.clientSocket.send(message) # packet is already encoded when compressed
        except ConnectionResetError as e:
            self.stopProgram("Connection was forcibly closed by server. Ensure the server is running before running the client.", type(e).__name__)
        self.receiveMessage()


    #This function receives a message from the server using the established socket connection.
    #   -> If no message is received, it calls the stopProgram method with an appropriate error message.
    #   -> Otherwise, it decodes the received message, creates a new packet from the decoded message,
    #      prints the response from the server, and empties the packet.
    #[*] Parameters: None
    #[*] Returns: None
    def receiveMessage(self):
        try:
            data = self.clientSocket.recv(self.bufferSize) # message is decoded when recieved
        except ConnectionResetError as e:
            self.stopProgram("Connection was forcibly closed by server. Ensure the server is running.", type(e).__name__)
        if(not data):
            self.stopProgram("Not message received from server, server may have been disconnected.")
        self.packet.createPacketFromString(data)
        print("Response from server: " + str(self.packet.getContents()) + "\n")
        self.packet.emptyPacket()


    #Prints a list of available commands for the client.
    #[*] Parameters: None
    #[*] Returns:None
    def printCommands(self) -> None:
        print("\n============")
        for command in self.commandsList:
            print(command + ": " + self.commandsList[command])
        print("============\n")


    #Takes a user input and creates packet, and transmits the packet to the server.
    #[*] Parameters: None
    #[*] Returns:None
    def getCity(self):
        country = input(" -> Enter a country: ")
        self.packet.createNewPacket("c",country)
        self.transmitMessage()


    #Takes a user input and creates packet, and transmits the packet to the server.
    #[*] Parameters: None
    #[*] Returns:None
    def getPopulation(self):
        country = input(" -> Enter a country: ")
        self.packet.createNewPacket("p",country)
        self.transmitMessage()


    #Takes a user input and creates packet, and transmits the packet to the server.
    #[*] Parameters: None
    #[*] Returns:None
    def addNewEntry(self) -> None:
        country = input(" -> Enter a country: ")
        city = input(f" -> Enter {country}'s capital city: ")
        pair = ",".join([country,city])
        self.packet.createNewPacket("a",pair)
        self.transmitMessage()


    #Basic heartbeat function. It sends a simple message to the server to verify connection.
    #[*] Parameters: None
    #[*] Returns:None
    def heartbeat(self) -> None:
        self.packet.createNewPacket("h","")
        self.transmitMessage()


    #This function stops the server and closes the connection. It also prints a shutdown message and exits the program.
    #[*] Parameters:
    #   -> message (str): A custom message to be printed when the server is shut down. Default is "Program terminated."
    #   -> *error (str): Variable length argument list to capture any error messages. This argument is not used in the function's logic.
    #[*] Returns:
    #   -> None: This function does not return any value. It closes the server connection, prints a shutdown message, and exits the program.
    def stopProgram(self, message="Program terminated.", *error:str) -> None:
        if(error):
            sys.exit(f"[!] {error[0]} detected: {message}")
        else:
            sys.exit(f"[!] {message}")

c = Client()
c.run()