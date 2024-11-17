import csv, socket, sys
from random import randint
from socket import SOL_SOCKET, SO_REUSEADDR
from packet import Packet
from time import time
from argparse import ArgumentParser
from datetime import date, datetime
from sys import getsizeof as size

class Server():
    #Initialises the Server class with a default port number of 6000.
    #If a port number is provided as a command-line argument, it updates the server's port.
    #[*] Parameters:
    #   -> port (int): The port number for the server. Default is 6000.
    #[*] Returns: None
    def __init__(self, address:str = "127.0.0.1", port:int = 6000) -> None:
        # update port
        parser = ArgumentParser()
        parser.add_argument("--port")
        parser.add_argument("--address")
        parser.add_argument("--file")
        args = parser.parse_args()
        if(args.port):
            self.port = int(args.port)
        else:
            self.port = port
        if(args.address):
            self.address = str(args.address)
        else:
            self.address = str(address)
        if(args.file):
            self.countriesFile = str(args.file)
        else:
            self.countriesFile = "countries_capitals.csv"
        self.studentNumber = 3404867

        self.serverSocket = socket.socket()
        self.stopServer = False
        self.bufferSize = 1024

        self.commandsExecution = {"c":self.getCity,
                                "p":self.getPopulation,
                                "a":self.addNewEntry,
                                "h":self.heartbeat}
        self.packet = Packet() # serves as a packet template to load and process received and transmitted packets

    #Preprocesses the 'countries_capitals.csv' file to handle multiple countries in a single line.
    #If a line contains multiple countries separated by " and ", it splits the line into separate entries,
    #each with a shared capital city. The updated file is then written back to disk.
    #[*] Parameters: None
    #[*] Returns:None

    def preprocessCountriesFile(self):
        print("[*] Preprocessing countries file...")
        rows = list()
        with open(self.countriesFile, "r") as csvFile:
            reader = csv.reader(csvFile)
            for index, row in enumerate(reader):
                rows.append(row)
                if(" and " in row[0]):
                    print("[!] Multiple countries in one line found. Fixing...")
                    sharedCapital = row[1]
                    countries = row[0].split(" and ")
                    rows.remove(row)
                    rows.append([countries[0],sharedCapital])
                    rows.append([countries[1],sharedCapital])
                    print("[*] Countries file updated, duplicate capital city fixed!")
        with open(self.countriesFile, 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            for row in rows:
                writer.writerow(row)


    #This function initializes and runs the server. It sets up the server details,
    #waits for a client connection, and handles incoming messages.
    #[*] Parameters: None
    #[*] Returns: None
    def run(self):
        try:
            self.preprocessCountriesFile()
        except FileNotFoundError as e:
            self.stopProgram("Countries file not found. Please make sure it is in the same directory as the server program.", type(e).__name__)

        # initialise server details
        self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.serverSocket.settimeout(30) # 30 second timeout

        # attempt to bind the socket
        try:
            self.serverSocket.bind((self.address, self.port))
        except OverflowError as e:
            self.stopProgram("Port number may be too high or too low. Ensure the port number is 0-65535", type(e).__name__)
        except OSError as e:
            self.stopProgram("Inputted IP Address is not valid in the current context. Ensure the IP address is correct and try again.", type(e).__name__)
        self.serverSocket.listen(2)
        print("Server started on " + self.address + ":" + str(self.port))

        # wait for connection
        print("Waiting for client connection...")
        try:
            self.conn, address = self.serverSocket.accept()
        except TimeoutError as e:
            self.stopProgram("Connection timed out. Ensure client and server have matching IP addresses and port numbers.", type(e).__name__)
        print("Connection established from " + str(address))

        # main server listening loop
        while(not self.stopServer):
            self.receiveMessage()
        self.stopProgram() # realistically the program shouldn't ever arrive here, this is just for redundancy

    #This function receives a message from the connected client, processes it, and responds accordingly.
    #[*] Parameters: None
    #[*] Returns: None
    #[*] Raises:
    #   -> ValueError: If a null packet is received, indicating a disconnection from the client.
    def receiveMessage(self):
        try:
            data = self.conn.recv(self.bufferSize)
            if not (size(data) > self.bufferSize):
                print(f"[*] Received message! {str(size(data))} bytes (compressed)")
            else:
                self.stopProgram("Received message! Exceeded buffer size.", type(Exception).__name__)
        except ConnectionAbortedError as e:
            self.stopProgram("Client disconnected.", type(e).__name__)
            return
        try:
            self.packet.createPacketFromString(data)
            if self.packet.getCommand() in self.commandsExecution:
                print(f"[*] Message Contents\n -> Command: {self.packet.getCommand()}\n -> Contents: {self.packet.getContents()}\n -> Size (uncompressed): {str(self.packet.getSize())} bytes")
                reply = self.commandsExecution[self.packet.getCommand()](self.packet.getContents()) 
                self.packet.emptyPacket()
                self.transmitMessage(self.conn,reply)
            else:
                self.transmitMessage(self.conn,"Invalid command received by server")
        except ValueError as e:
            if(not data) or data == "": 
                self.stopProgram("Null packet received, client may have been disconnected.", type(e).__name__)


    #Transmits a message to the connected client using the provided socket connection.
    #[*] Parameters:
    #   -> conn (socket.socket): The socket connection to the client.
    #   -> message (str): The message to be transmitted.
    #[*] Returns:
    #   -> None: This function does not return any value. It sends the message to the client.
    def transmitMessage(self, conn:socket.socket, message:str):
        self.packet.createNewPacket("",message)
        message = self.packet.generatePacket()
        self.packet.emptyPacket()
        conn.send(message)
        print("[*] Message Transmitted!")


    #Retrieves the capital city of a given country from the 'countries_capitals.csv' file.
    #[*] Parameters:
    #   -> country (str): The name of the country for which the capital city is to be retrieved.
    #[*] Returns:
    #   -> str: The capital city of the given country. If the country is not found in the file,
    #           the function returns "No country found."
    def getCity(self, country:str) -> str:
        print(f"[*] Retrieving capital city for {country}...")
        country = country.capitalize() # normalise the input
        with open(self.countriesFile, "r") as csvFile:
            reader = csv.reader(csvFile)
            next(reader, None) # skip the header [Country, City]
            for index, row in enumerate(reader):
                if(row[0] == country): 
                    print(f"[*] Found capital city {row[1]}")
                    return row[1]
            return "No country found."


    #Retrieves the estimated population of a given country from the 'countries_capitals.csv' file.
    #The population is calculated as a random number between 1 and 10 times the student number.
    #[*] Parameters:
    #   -> country (str): The name of the country for which the population is to be retrieved.
    #[*] Returns:
    #   -> str: The estimated population of the given country. If the country is not found in the file,
    #           the function returns "Country not found."
    def getPopulation(self, country:str) -> str:
        print(f"[*] Retrieving estimated population for {country}...")
        country = country.capitalize() # normalise the input
        with open(self.countriesFile, "r") as csvFile:
            reader = csv.reader(csvFile)
            next(reader, None) # skip the header [Country, City]
            for index, row in enumerate(reader):
                if(row[0] == country): return str(randint(1,10) * self.studentNumber)
        return "No country found"


    #Adds a new entry to the 'countries_capitals.csv' file.
    #[*] Parameters:
    #   -> countryCityPair (str): A string containing the country and city separated by a comma.
    #                             The country and city names are expected to be in lowercase.
    #[*] Returns:
    #   -> str: A message indicating the success or failure of the operation.
    #           If the country does not exist in the file, the new entry is added and a success message is returned.
    #           If the country already exists in the file, a failure message is returned.
    def addNewEntry(self, countryCityPair:str) -> str:
        country,city = countryCityPair.split(",")
        country = country.capitalize() # normalise the input
        city = city.capitalize() # normalise the input
        print(f"[*] Adding new entry for {country} with {city}...")
        if(self.getCity(country) == "No country found."):
            with open(self.countriesFile ,'a', newline='') as csvFile:
                csv.writer(csvFile).writerow([country, city])
                print(f"{country} and {city} successfully added to database")
                return f"{country} and {city} successfully added to database"
        return "Country already exists"


    #This function serves as a heartbeat mechanism for the server. It is called periodically to check the server's status.
    #[*] Parameters:
    #   -> *externalMessage (tuple): This parameter is not used in this function. It is included to maintain consistency with other command execution functions.
    #[*] Returns:
    #   -> str: A string indicating the success of the heartbeat. In this case, it always returns "beat".
    def heartbeat(self, *externalMessage) -> str:
            print("[*] Heart -> beat")
            return "beat"


    #This function stops the server and closes the connection. It also prints a shutdown message and exits the program.
    #[*] Parameters:
    #   -> message (str): A custom message to be printed when the server is shut down. Default is "Server has been shut down successfully."
    #   -> *error (str): Variable length argument list to capture any error messages. This argument is not used in the function's logic.
    #[*] Returns:
    #   -> None: This function does not return any value. It closes the server connection, prints a shutdown message, and exits the program.
    def stopProgram(self, message="Server has been shut down successfully.", *error:str) -> None:
        try:
            self.conn.close()
            print("[!] Server connection closed.")
        except (NameError, AttributeError): # connection was never established or doesn't exist
            pass
        sys.exit(f"[!] {error[0]} detected: {message}")

s = Server()
s.run()