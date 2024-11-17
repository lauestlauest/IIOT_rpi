import spidev
import RPi.GPIO as GPIO
import time

# Define LoRa pins
DIO0 = 24   # LoRa DIO0 for interrupt handling (message received)
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
spi.max_speed_hz = 1000000  # Set speed for the SPI bus
spi.mode = 0  # Set SPI mode to 0

# LoRa Register Addresses
REG_FIFO = 0x00
REG_OP_MODE = 0x01
REG_FIFO_RX_BASE_ADDR = 0x0F
REG_FIFO_ADDR_PTR = 0x0D
REG_PAYLOAD_LENGTH = 0x22
REG_IRQ_FLAGS = 0x12
REG_IRQ_FLAGS_MASK = 0x11
REG_FRF_MSB = 0x06
REG_FRF_MID = 0x07
REG_FRF_LSB = 0x08
REG_MODEM_CONFIG_2 = 0x1E
REG_MODEM_CONFIG_1 = 0x1D
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

# Function to set sync word
def set_sync_word(sync_word):
    write_register(REG_SYNC_WORD, sync_word)
    print(f"Sync Word set to {hex(sync_word)}")

# Setup LoRa receiver mode
def setup_receiver():
    # Set to standby mode first
    write_register(REG_OP_MODE, 0x01)
    time.sleep(0.1)
    
    set_frequency_to_433mhz()
    set_sync_word(0x30)
    
    # Set the receiver in continuous mode
    write_register(REG_OP_MODE, 0x85)  # LoRa mode, receiver continuous
    
    # Clear any IRQ flags
    write_register(REG_IRQ_FLAGS, 0xFF)
    print("Receiver mode set.")

def set_frequency_to_433mhz():
    # FRF value for 433 MHz: 0x6C4000
    write_register(REG_FRF_MSB, 0x6C)  # MSB
    write_register(REG_FRF_MID, 0x40)  # MID
    write_register(REG_FRF_LSB, 0x00)  # LSB
    print("Frequency set to 433 MHz")

# Function to check and read a received message
def check_for_message():
    irq_flags = read_register(REG_IRQ_FLAGS)
    print("irq flags = ")
    print(irq_flags)
    
    if irq_flags & 0x40:  # Check if RX_DONE flag is set
        print("Message received!")
        # Clear IRQ flags
        write_register(REG_IRQ_FLAGS, 0xFF)
        
        # Set the FIFO pointer to the current RX address
        write_register(REG_FIFO_ADDR_PTR, read_register(REG_FIFO_RX_BASE_ADDR))
        
        # Retrieve message from FIFO
        payload_length = read_register(REG_PAYLOAD_LENGTH)
        message = []
        
        for i in range(payload_length):
            message.append(chr(read_register(REG_FIFO)))
        
        print("Received message: " + ''.join(message))
    else:
        print("No message received.")

# Initialize and start the receiver
setup_receiver()

try:
    while True:
        check_for_message()
        time.sleep(1)  # Check every second

except KeyboardInterrupt:
    print("Receiver stopped by user.")

finally:
    GPIO.cleanup()
    spi.close()
