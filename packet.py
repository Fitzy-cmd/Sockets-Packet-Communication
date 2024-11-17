# Represents a simple network packet for the client and server to communicate with each other with
# This allows a standardised form of communication so that both sides can expect the same message format

from sys import getsizeof as size
import zlib

class Packet():
    #Initialize a new Packet object.
    #[*] Parameters:
    #   -> command (str): The command associated with the packet. Default is an empty string.
    #   -> contents (str): The contents of the packet. Default is an empty string.
    #[*] Returns: None
    def __init__(self, command:str="", contents:str=""):
        self.command = command
        self.contents = contents
        self.size = 0


    #Creates a new packet with the given command and contents.
    #[*] Parameters:
    #   -> command (str): The command associated with the packet.
    #   -> contents (str): The contents of the packet.
    #[*] Returns: None
    def createNewPacket(self, command:str, contents:str):
        self.command = command
        self.contents = contents
        self.calculateSize()


    #Parses a string into a Packet object by splitting it at the first colon.
    #   -> The input string is expected to be in the format "command:contents".
    #   -> The command and contents are then assigned to the Packet object's respective attributes.
    #[*] Parameters:
    #   -> packet (str): The input string to be parsed. It should be in the format "command:contents".
    #[*] Returns: None
    def createPacketFromString(self, packet:bytes):
        if(len(packet) > 0):
            packetString = self.decompress(packet)
            self.command, self.contents = packetString.split("|")
            self.calculateSize()


    #Generates a string representation of the packet in the format "command:contents".
    #[*] Parameters: None
    #[*] Returns:
    #   -> str: A string representation of the packet in the format "command:contents".
    def generatePacket(self) -> str:
        return self.compress(f"{self.command}|{self.contents}")

    #Resets the command and contents of the packet to empty strings.
    #Parameters: None
    #Returns: None
    def emptyPacket(self):
        self.command = ""
        self.contents = ""

    def getCommand(self) -> str:
        return self.command

    def getContents(self) -> str:
        return self.contents
    
    def getSize(self) -> int:
        return self.size

    def compress(self, message) -> bytes:
        compressed = zlib.compress(message.encode("utf-8"))
        return compressed
    
    def decompress(self, message) -> str:
        decompressed = zlib.decompress(message).decode("utf-8")
        return decompressed
    
    def calculateSize(self):
        self.size = size(self.command) + size(self.contents)
