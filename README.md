# Sockets-Packet-Communication
This project demonstrates a client-server web socket system that sends custom-form packets back and forth to retrieve and display information about a provided city capital.

## How to execute server
With the terminal in the same directory, run the following command (note that the command to run python can vary between operating systems. It can be `py`, `python3`, `python`, etc):
```
py server.py --address <ipAddress> --port <portNumber>
```
Note that you are able to execute without the arguments, and the program will default to port 6000 and localhost. 

Ensure this is run first before you run the client.

## How to execute client
With the terminal in the same directory, run the following command (note that the command to run python can vary between operating systems. It can be `py`, `python3`, `python`, etc):
```
py client.py --address <ipAddress> --port <portNumber> --file <fileName>
```
Note that you are able to execute without the arguments, and the program will default to port 6000, localhost and "countries_capitals.csv". 

Run this after the server.

## Protocol Used
The packet.py file contains a collection of functions dedicated to converting information into a form to transmit between the client and the server. There are two sections to the packet.py file: 
1. Command
2. Content
The command section is a single character used to indicate to the server what the client is requesting. See below for command table. The content section contains all of the information necessary for the server to respond the request acccurately. This information gets bundled into a single string split by a vertical bar ("|"). This gets converted into bytes and compressed using the zlib library in python to minimise the size of the packet being sent to and from the server.

The server responds in a similar way. The client will ignore the command section, and will only process the content section. The server responses are compressed in the same way as the client. Additionally, the server will log the message sizes to demonstrate how much space is saved during compression.

### Command Table
| Command | Details        |
|---------|----------------|
| c       | Get City       |
| p       | Get Population |
| a       | Add New Entry  |
| h       | Heartbeat      |
