import spidev
import RPi.GPIO as GPIO
import time

# Define LoRa pins
DIO0 = 24   # LoRa DIO0
NSS = 8     # SPI Chip Select (CE0)
RESET = 25  # Reset pin

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIO0, GPIO.IN)
GPIO.setup(NSS, GPIO.OUT)
GPIO.setup(RESET, GPIO.OUT)

# SPI Setup
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0 (CE0)
spi.max_speed_hz = 1000000    # Set speed for the SPI bus

# LoRa Register Addresses
REG_FIFO = 0x00
REG_OP_MODE = 0x01
REG_FIFO_TX_BASE_ADDR = 0x0E
REG_PAYLOAD_LENGTH = 0x22
REG_IRQ_FLAGS = 0x12
REG_DIO_MAPPING_1 = 0x40
REG_IRQ_FLAGS_MASK = 0x11
REG_FRF_MSB = 0x06
REG_FRF_MID = 0x07
REG_FRF_LSB = 0x08
REG_MODEM_CONFIG_2 = 0x1E
REG_MODEM_CONFIG_1 = 0x1D
REG_MODEM_CONFIG_2 = 0x1E
REG_SYNC_WORD = 0x39
REG_INVERT_IQ = 0x33

# Reset LoRa Module
GPIO.output(RESET, GPIO.HIGH)
time.sleep(0.01)
GPIO.output(RESET, GPIO.LOW)
time.sleep(0.01)

# Write to LoRa register
def write_register(register, value):
    GPIO.output(NSS, GPIO.LOW)
    spi.xfer2([register | 0x80, value])
    GPIO.output(NSS, GPIO.HIGH)

# Read from LoRa register
def read_register(register):
    GPIO.output(NSS, GPIO.LOW)
    response = spi.xfer2([register & 0x7F, 0x00])
    GPIO.output(NSS, GPIO.HIGH)
    return response[1]

def set_spreading_factor(sf):
    if sf < 6 or sf > 12:
        raise ValueError("Spreading factor must be between 6 and 12")
    config = read_register(REG_MODEM_CONFIG_2) & 0x0F  # Clear bits 7-4
    config |= (sf << 4)  # Set spreading factor
    write_register(REG_MODEM_CONFIG_2, config)
    print(f"Spreading Factor set to {sf}")

# Function to set bandwidth
def set_bandwidth(bw):
    bw_values = {125000: 0x70, 250000: 0x80, 500000: 0x90}
    if bw not in bw_values:
        raise ValueError("Invalid bandwidth. Use 125000, 250000, or 500000 Hz")
    config = read_register(REG_MODEM_CONFIG_1) & 0x0F  # Clear bits 7-4
    config |= bw_values[bw]  # Set bandwidth
    write_register(REG_MODEM_CONFIG_1, config)
    print(f"Bandwidth set to {bw} Hz")

# Function to set sync word
def set_sync_word(sync_word):
    write_register(REG_SYNC_WORD, sync_word)
    print(f"Sync Word set to {hex(sync_word)}")

def enable_crc():
    config = read_register(REG_MODEM_CONFIG_2)
    config |= (1 << 2)  # Set bit 2 to 1
    write_register(REG_MODEM_CONFIG_2, config)
    print("CRC enabled")

# Setup LoRa transmitter mode
def setup_transmitter():
    # Set to standby mode
    write_register(REG_OP_MODE, 0x01)
    time.sleep(0.1)
    
    set_frequency_to_433mhz()
    enable_crc()
    set_spreading_factor(7)  # Set SF to 7
    set_bandwidth(125000)    # Set bandwidth to 125 kHz
    set_sync_word(0x30)
    # Set FIFO base address for TX
    write_register(REG_FIFO_TX_BASE_ADDR, 0x00)
    write_register(REG_PAYLOAD_LENGTH, 0x00)  # Initialize payload length
    print("Transmitter mode set.")

def set_frequency_to_433mhz():
    # FRF value for 433 MHz: 0x6C4000
    write_register(REG_FRF_MSB, 0x6C)  # MSB
    write_register(REG_FRF_MID, 0x40)  # MID
    write_register(REG_FRF_LSB, 0x00)  # LSB
    print("Frequency set to 433 MHz")

# Function to send a message
def send_message(message):
    # Clear IRQ flags
    write_register(REG_IRQ_FLAGS, 0xFF)
    
    # Set payload length
    write_register(REG_PAYLOAD_LENGTH, len(message))
    
    # Set FIFO pointer to base address
    write_register(REG_FIFO, 0x00)
    
    # Write message to FIFO
    GPIO.output(NSS, GPIO.LOW)
    spi.xfer2([REG_FIFO | 0x80] + [ord(c) for c in message])
    GPIO.output(NSS, GPIO.HIGH)
    
    # Set to transmit mode
    write_register(REG_OP_MODE, 0x83)  # TX mode
    print(f"Sent message: {message}")
    
    # Clear IRQ flags again
    write_register(REG_IRQ_FLAGS, 0xFF)

# Initialize and start the transmitter
setup_transmitter()

try:
    while True:
        send_message("Hello, LoRa!")
        time.sleep(5)

except KeyboardInterrupt:
    print("Transmission stopped by user.")

finally:
    GPIO.cleanup()
    spi.close()
