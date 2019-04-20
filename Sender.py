# Team Members: Jonathan Lapham, Vusal Pasha, Huiyi Chen
# Phase 5
# Reference taken from the textbook: Computer Networking: A Top Down Approach 7th ed

from socket import *
import UDP
import Packet
import time
import _thread
from Timer import Timer


# This is the host's IP address
serverName = '127.0.0.1'
clientName = '127.0.0.1'
clientPort = 12500  # This is an arbitrary clientPort, could be changed
serverPort = 12000  # This is an arbitrary serverPort, could be changed
serverAddress = ('127.0.0.1', serverPort)
clientAddress = ('127.0.0.1', clientPort)

# Generates a client socket
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(('', clientPort))  # Assigns the client port to the client's socket

print("This program takes an image and sends it to the server.")
fileSend = open("fruit.jpg", 'br')

print("Please input same probability as Server.")
cor_prob = int(input("What is the probability of packet corruption?: "))
loss_prob = int(input("What is the probability of packet loss?: "))

global BASE

SLEEP_TIME = 0.005
TIMEOUT_INTERVAL = 0.05
WINDOW_SIZE = int(input("What is the window size?: "))

# Data shared amongst the threads
# Set BASE to 1, becaue the response from server might equal to BASE - 1
# To avoid negative number that might cause exception
BASE = 1
Mutex = _thread.allocate_lock()
send_timer = Timer(TIMEOUT_INTERVAL)


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
    return not verify_checksum(data, chk)


def is_ack(pkt, sequence):
    """
    Indicates what the current sequence number is and compares it with
    the packet's sequence number.
    """
    seq = pkt[0]
    print('is_ack is ' + str(sequence))
    if seq == sequence:
        return True
    else:
        return False


def get_ack(pkt):
    return pkt[0]


def set_window(packet_num):
    global BASE
    return min(WINDOW_SIZE, packet_num - BASE)


# Sending thread, sends packets to the server
def sending(sock, file):
    global Mutex
    global BASE
    global send_timer

    packets = []
    seq_number = 1

    # Generates all the packets from the picture
    while True:
        packet = Packet.make_packet(file, seq_number)
        if not packet:
            break
        packets.append(packet)
        seq_number += 1

    total_packets = len(packets)
    print("Packet total is ", total_packets)
    win_size = set_window(total_packets)
    next_packet_num = 0

    print('\nBeginning Receiving Thread')

    _thread.start_new_thread(receiving, (clientSocket, ))

    while BASE < total_packets:
        # Comment below as we don't want to lock the whole sending process
        # Mutex will be used on object-level
        # Mutex.acquire()

        win_size = set_window(total_packets)

        # Comment below debug logs
        # print("BASE=" + str(BASE) + " ,next_packet_num=" + str(next_packet_num))
        # print("win_size=" + str(win_size))

        # Send packets within the window
        if not send_timer.timeout() and next_packet_num < BASE + win_size:
            print('Sending packet', next_packet_num)
            UDP.send(packets[next_packet_num - 1], sock, serverAddress, loss_prob, cor_prob)
            Mutex.acquire()
            next_packet_num += 1
            Mutex.release()

            if next_packet_num == BASE:
                if not send_timer.running():
                    print('Starting Timer')
                    Mutex.acquire()
                    send_timer.start()
                    Mutex.release()
        else:
            if not send_timer.running():
                Mutex.acquire()
                send_timer.start()
                Mutex.release()

        while send_timer.running() and not send_timer.timeout():
            print('Sending thread going to sleep')
            time.sleep(SLEEP_TIME)

        # Handle the timeout case
        if send_timer.timeout():
            print('Timeout has occurred\n')
            send_timer.stop()
            next_packet_num = BASE



    # All packets have been sent, send a empty packet
    print("File has been sent!!")
    UDP.send(bytes(), sock, serverAddress, 0, 0)
    fileSend.close()


def receiving(sckt):
    global Mutex
    global BASE
    global send_timer

    while True:
        pkt, addr = sckt.recvfrom(4096)
        if not pkt:
            break
        print("Control Packet was Received!")
        if not corrupted(pkt) and get_ack(pkt) >= BASE:
            Mutex.acquire()
            BASE = get_ack(pkt) + 1
            send_timer.stop()
            Mutex.release()

    _thread.exit_thread()


print('Beginning Sender')
sending(clientSocket, fileSend)
# comment below to avoid thread exception
#clientSocket.close()
