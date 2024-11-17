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

# Setup LoRa transmitter mode
def setup_transmitter():
    # Set to standby mode
    write_register(REG_OP_MODE, 0x01)
    time.sleep(0.1)
    
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
    
    # Wait for transmission to complete
    while GPIO.input(DIO0) == 0:
        time.sleep(0.01)  # Wait until DIO0 goes high

    # Clear IRQ flags again
    write_register(REG_IRQ_FLAGS, 0xFF)

# Initialize and start the transmitter
setup_transmitter()
set_frequency_to_433mhz()

try:
    while True:
        send_message("Hello, LoRa!")
        time.sleep(5)

except KeyboardInterrupt:
    print("Transmission stopped by user.")

finally:
    GPIO.cleanup()
    spi.close()
