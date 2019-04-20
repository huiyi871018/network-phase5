# Corrupt_Loss.py --- Contains all functions for corrupting/losing packets
import random


def make_corrupt(pkt, prob):
    """
    number from 0 to 99 and generates chance of corruption if below probability value.
    ex: prob = 50, then 50 potential values out of 100 could corrupt pkt
    """
    x = random.randint(0, 100)
    if x < int(prob):
        print('\nCurrently corrupting the data!!\n')
        badpkt = bytearray()
        for p in pkt:
            badpkt.append(p)
        badpkt.append(1)
        return badpkt
    return pkt


def make_loss(prob):
    """
    number from 0 to 99 and generates chance of corruption if below probability value.
    ex: prob = 50, then 50 potential values out of 100 could corrupt pkt
    """
    x = random.randint(0, 100)
    if x < int(prob):
        print('\nGoing to Lose Control Packet!!\n')
        return True
    return False

