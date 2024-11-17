import spidev
import RPi.GPIO as GPIO
import time

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)  # Change 25 to your SX1278 NSS pin

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 5000000  # Set SPI speed to 5 MHz

# SX1278 Register Configuration
def write_register(register, value):
    GPIO.output(25, GPIO.LOW)  # Select the SX1278
    spi.xfer2([register | 0x80, value])  # Write to register
    GPIO.output(25, GPIO.HIGH)  # Deselect the SX1278

def read_register(register):
    GPIO.output(25, GPIO.LOW)  # Select the SX1278
    response = spi.xfer2([register & 0x7F, 0x00])  # Read from register
    GPIO.output(25, GPIO.HIGH)  # Deselect the SX1278
    return response[1]

# SX1278 Initialization
def sx1278_init():
    write_register(0x01, 0x81)  # Set to sleep mode to configure
    write_register(0x06, 0x6C)  # Set frequency to 433 MHz
    write_register(0x07, 0x80)
    write_register(0x08, 0x00)
    write_register(0x09, 0xFF)  # Maximum output power
    write_register(0x01, 0x83)  # Set to standby mode

def send_packet(value):
    write_register(0x0D, 0x00)  # Set FIFO address
    write_register(0x00, value)  # Write value to FIFO
    write_register(0x22, 1)  # Set payload length to 1 byte
    write_register(0x01, 0x83)  # Set to standby mode
    write_register(0x40, 0x40)  # Set DIO0 to TX done
    write_register(0x01, 0x83 | 0x03)  # Set to transmit mode
    time.sleep(0.05)  # Wait for transmission

# Main Function
def main():
    sx1278_init()
    print("LoRa Transmitter started")
    while True:
        val = 112  # Example of reading a value
        send_packet(val)
        time.sleep(0.05)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        spi.close()
