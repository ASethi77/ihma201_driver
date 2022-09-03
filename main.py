import time
import spidev
import ctypes
from ctypes import c_ubyte, c_uint32, c_uint16

spi_ch = 0

# Enable SPI
spi = spidev.SpiDev()
spi.open(0, spi_ch)

# 5 MHz for L6470
spi.max_speed_hz = 100000
spi.mode = 3
spi.bits_per_word = 8
# spi.cshigh = False
# spi.lsbfirst = True

class CommandHeaders(object):
    SetParam = 0b000
    GetParam = 0b001
    MoveRel =  0b010
    GetStatus = 0b110

class ParamRegisters(object):
    ABS_POS = 0x01
    ACCEL = 0x05
    MAX_SPEED = 0x07
    CONFIG = 0x18
    STATUS = 0x19

def MoveCommand(direction=0, stepcount=0):
    msg = c_uint32(CommandHeaders.MoveRel)
    msg.value <<= 5
    msg.value |= direction
    msg.value <<= 24

    stepcount3 = c_uint32(stepcount)
    stepcount3.value &= 0x3FFFFF

    msg.value |= stepcount3.value

    return [(msg.value >> 24) & 0xFF,
            (msg.value >> 16) & 0xFF,
            (msg.value >> 8) & 0xFF,
            msg.value & 0xFF]

def GetParamCommand(paramRegister, numBytes=1):
    msg = c_ubyte(CommandHeaders.GetParam)
    msg.value <<= 5
    msg.value |= paramRegister

    return [msg.value] + [0 for b in range(numBytes - 1)]

def SetParamCommand(paramRegister, byteValues):
    msg = c_ubyte(CommandHeaders.SetParam)
    msg.value <<= 5
    msg.value |= paramRegister

    return [msg.value] + byteValues

def HandleCommand(cmdBytes, numBytesBack):
    print(f"Command: {[hex(a) for a in cmdBytes]}")
    spi.writebytes(cmdBytes)
    spi.readbytes(1)
    resp = spi.readbytes(numBytesBack)
    print(f"Response: {[hex(a) for a in resp]}")
    return resp


def read_adc(adc_ch, vref = 3.3):
    # msg = MoveCommand(1, 20)
    # print(f"Move command response: {spi.xfer(MoveCommand(1, 100))}")
    # for byteSize in range(1):
    stsCmd = GetParamCommand(ParamRegisters.ACCEL)
    HandleCommand(stsCmd, 2)
    #     # stsCmd = SetParamCommand(ParamRegisters.CONFIG, [0x2e, 0x88])
    # print(f"Command: {[hex(a) for a in stsCmd]}")
    # print(f"Response: {[hex(a) for a in spi.xfer2(stsCmd)]}")
    # print(spi.readbytes(1))
    # print(spi.readbytes(1))
    # print(spi.xfer2([0]))
# read_adc(0)
# Report the channel 0 and channel 1 voltages to the terminal
try:
    while True:
        adc_0 = read_adc(0)
        # adc_1 = read_adc(1)
        # print("Ch 0:", round(adc_0, 2), "V Ch 1:", round(adc_1, 2), "V")
        time.sleep(0.05)

finally:
    spi.close()
    # GPIO.cleanup()
