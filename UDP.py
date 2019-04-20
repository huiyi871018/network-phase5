# UDP.py - Unreliable data transfer

import Corrupt_Loss


# Send a packet across the unreliable channel
# Packet may be lost
def send(packet, sock, addr, loss_prob, cor_prob):
    loss = Corrupt_Loss.make_loss(loss_prob)
    packet = Corrupt_Loss.make_corrupt(packet, cor_prob)
    if not loss:
        sock.sendto(packet, addr)
    return


# Receive a packet from the unreliable channel
def recv(sock):
    packet, addr = sock.recvfrom(4096)
    return packet, addr


