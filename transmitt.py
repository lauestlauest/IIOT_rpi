import spidev
import RPi.GPIO as GPIO
import time

spi = spidev.SpiDev()

class LoraTransmitter():

    def __init__(self):
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(25, GPIO.OUT)  # NSS pin for SX1278

        # Initialize SPI
        spi.open(0, 0)  # Open SPI bus 0, device 0
        spi.max_speed_hz = 5000000  # Set SPI speed to 5 MHz

        self.sx1278_init()

    # Function to write to a register
    def write_register(self, register, value):
        GPIO.output(25, GPIO.LOW)  # Select the SX1278
        spi.xfer2([register | 0x80, value])  # Write to register
        GPIO.output(25, GPIO.HIGH)  # Deselect the SX1278

    # Function to read from a register
    def read_register(self, register):
        GPIO.output(25, GPIO.LOW)  # Select the SX1278
        response = spi.xfer2([register & 0x7F, 0x00])  # Read from register
        GPIO.output(25, GPIO.HIGH)  # Deselect the SX1278
        return response[1]

    # SX1278 Initialization
    def sx1278_init(self):
        self.write_register(0x01, 0x80 | 0x00)  # Set to sleep mode
        self.write_register(0x06, 0x6C)  # Set frequency to 433 MHz
        self.write_register(0x07, 0x80)
        self.write_register(0x08, 0x00)

        # Set base addresses
        self.write_register(0x0E, 0x00)  # FIFO Tx base address
        self.write_register(0x0F, 0x00)  # FIFO Rx base address

        # Set LNA boost
        self.write_register(0x0C, self.read_register(0x0C) | 0x03)

        # Set auto AGC
        self.write_register(0x26, 0x04)

        self.write_register(0x4D, 0x84)  # PA ramp-up time
        self.write_register(0x09, 0x80 | 0x0F)  # Maximum output power

        self.write_register(0x01, 0x80 | 0x01)  # Set to standby mode

    # Function to send a packet
    def send_packet(self, payload):
        self.write_register(0x01, 0x80 | 0x01)  # Set to standby mode
        self.write_register(0x0D, 0x00)  # Set FIFO address pointer

        #payload = [value]  # Payload to transmit
        payload_length = len(payload)
        self.write_register(0x22, payload_length)  # Set payload length

        # Write payload to FIFO
        for byte in payload:
            self.write_register(0x00, byte)
            print(f"Sent: {byte}")

        # Set to transmit mode
        self.write_register(0x01, 0x80 | 0x03)

        # Wait for transmission to complete
        while (self.read_register(0x12) & 0x08) == 0:
            time.sleep(0.01)  # Check for the TxDone flag

        self.write_register(0x12, 0x08)  # Clear the TxDone flag
        self.write_register(0x01, 0x80 | 0x01)  # Set back to standby mode

    def __del__(self):
        spi.close()
        GPIO.cleanup()

