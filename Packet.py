# Packet.py --- Contains functions used for packet generation


def make_packet(file_name, sequence):
    """
    Makes a packet parse, adding sequence number, checksum to the header, then appending data
    """
    pkt = bytearray()
    data = file_name.read(1024)
    if len(data) == 0:
        print("\nNo more data can be read from the file!\n")
        return None
    pkt.append(sequence)
    checksum = generate_checksum(data)
    checksum_bytes = checksum.to_bytes(2, byteorder='little')
    for cb in checksum_bytes:
        pkt.append(cb)
    for d in data:
        pkt.append(d)
    return pkt


def make_ack(pkt, sequence):
    """
    Makes a packet parse, adding sequence number, checksum to the header, then appending data
    """
    data = bytearray()
    data.extend(map(ord, 'ACK'))
    checksum = generate_checksum(data)
    pkt.append(sequence)
    checksum_bytes = checksum.to_bytes(2, 'little')
    for cb in checksum_bytes:
        pkt.append(cb)
    for d in data:
        pkt.append(d)
    return pkt


def generate_checksum(data, byteorder='little'):
    """
    Takes bytes from data and sums them together, with overflows being added to the sum. The result
    is then XORed for 1's compliment.
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
    checksum = sum ^ 0xFFFF
    return checksum


