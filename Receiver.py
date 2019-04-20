# Team Members: Jonathan Lapham, Vusal Pasha, Huiyi Chen
# Phase 5

from socket import *
import UDP
import Packet

serverPort = 12000  # Create the server socket with an appropriate port number
serverSocket = socket(AF_INET, SOCK_DGRAM)  # Dictate destination of control packets
clientPort = 12500
clientName = '127.0.0.1'
serverSocket.bind(('', serverPort))  # Assigns the server port to the server's pocket

# The server ip and port are tupled into the serverAddress tuple
serverAddress = ('127.0.0.1', serverPort)
clientAddress = ('127.0.0.1', clientPort)

# Creates a blank file, which shall be written by received data
outputFile = open("JPG_FILE_OUTPUT.jpg", "bw+")

# The packet size of 1024 bytes
packet_size = 1024

print("Beginning on %s port %s" % serverAddress)

# initialize state and packet, also ask for probability.
state = 0
packet = bytearray()

print("Please input same probability as Client.")
cor_prob = int(input("What is the probability of packet corruption?: "))
loss_prob = int(input("What is the probability of packet loss?: "))
expected_seq = 1


def verify_checksum(data, checksum, byteorder='little'):
    """
    Makes a checksum and compares with the received checksum
    """
    length = len(data)
    sum = 0
    for i in range(0, length):
        x = int.from_bytes(data[i:i + 2], byteorder, signed=False)
        sum += x
        while sum > 0xFFFF:
            remain = sum & 0xFFFF
            overflow = (sum & 0x00) >> 16
            sum = remain + overflow
    sum += checksum
    return sum == 0xFFFF


def corrupted(pkt):
    """
    Checks if the packet has been corrupted, which is done by checking the checksum
    """
    chk_arr = pkt[1:3]
    data = pkt[3:]
    chk = int.from_bytes(chk_arr, 'little', signed=False)
    isCorrupted = not verify_checksum(data, chk)
    if isCorrupted:
        print("***ERROR: package is corrupted")
    return isCorrupted


def has_seq_num(pkt, sequence):
    """
    Indicates what the current sequence number is and compares it with
    the packet's sequence number.
    """
    seq = pkt[0]
    has_seq = seq == sequence
    if not has_seq:
        print("***ERROR: seq number is wrong")
        print("***ERROR: pkt seq = " + str(seq) + " ,expected sequence = " + str(sequence))
    if has_seq:
        return True
    else:
        return False


def extract_deliver(pkt):
    """
    Extracts the message from the packet and writes it to the file.
    """
    message = pkt[3:]
    outputFile.write(message)
    if len(message) < 1024:
        outputFile.close()
    return


print('Receiver Beginning')


while True:
    rcvpacket, addr = UDP.recv(serverSocket)
    if not rcvpacket:
        print("End of Transmission")
        UDP.send(bytes(), serverSocket, clientAddress, 0, 0)
        break
    print("\nReceiving from client!")
    if corrupted(rcvpacket) or not has_seq_num(rcvpacket, expected_seq):
        packet.clear()
        print("***ERROR: Packet corrupted or with wrong sequence")
        Packet.make_ack(packet, expected_seq - 1)
        # Even receiving bad packet, Server still need to respond
        # because when data was good, that response might lost but the client doesn't know
        UDP.send(packet, serverSocket, clientAddress, loss_prob, cor_prob)
    elif not corrupted(rcvpacket) and has_seq_num(rcvpacket, expected_seq):
        print("Got expected packet ", expected_seq)
        extract_deliver(rcvpacket)
        packet.clear()
        Packet.make_ack(packet, expected_seq)
        print("Sending cumulative ACK")
        UDP.send(packet, serverSocket, clientAddress, loss_prob, cor_prob)
        expected_seq += 1
    packet.clear()


print("\nClosing Output File and Closing Server Socket")
outputFile.close()
serverSocket.close()




