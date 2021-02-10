from pyftdi.ftdi import Ftdi
from pyftdi.eeprom import FtdiEeprom
import pyftdi.serialext
import time
from obd.OBDCommand import OBDCommand

Ftdi.add_custom_product(0x0403, 0xcc48, "Future Technology Devices International Limited OpenPort 1.3 Mitsubishi")

url = "ftdi://0x0403:0xcc48/"
eeprom = FtdiEeprom()
eeprom.open(url)
eeprom.dump_config()
eeprom.close()
eeprom = None

def generateCommand(service, pid):
    packet = [
        0x68,
        0x6a,
        0xf1,
        service
    ]
    if pid is not None:
        packet.append(pid)

    checksum = 0
    for data in packet:
        checksum = checksum + data
    packet.append(checksum % 256)

    print ("generated packet : {}".format(packet))
    return packet

def getResponse(serial):
    while True:
    data = serial.read()
    if len(data) > 0:
        for byte in data:
            print(hex(byte))
    else:
        return

with pyftdi.serialext.serial_for_url(url, baudrate=10400, timeout=1) as ser:
    print(ser)
    print('Init 0x33 at 5 baud')

    initKey = 0x33
    ser.rts = 1

    ser.dtr = 1
    time.sleep(0.200)

    for addr in range(0, 8):
        bit = ((initKey >> addr) & 0x01) ^ 0x01
        ser.dtr = bit
        time.sleep(0.200)

    ser.dtr = 0
    ser.rts = 0
    # time.sleep(0.200)

    print('Waiting for sync byte')
    syncByte = 0x00
    while syncByte != b'U':
        syncByte = ser.read(1)
        print(syncByte)
    print('got sync byte')
    print('Waiting for key bytes')
    keyBytes = ser.read(2)

    print("init string {}".format(syncByte + keyBytes))
    response = bytes([keyBytes[1] ^ 0xFF])

    ser.write(response)

    print("init response sent! {}".format(response))

    ecuByte = ser.read(1)
    ecuID = bytes([syncByte[0] ^ 0xFF])
    print("got ECU ID : {}".format(ecuID))

    ser.write(generateCommand(0x01, 0x00))
    getResponse(ser)
    
    ser.write(generateCommand(0x03, None))
    getResponse(ser)
