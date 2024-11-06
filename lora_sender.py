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
spi.max_speed_hz = 5000000  # Set speed for the SPI bus

# Reset LoRa Module
GPIO.output(RESET, GPIO.HIGH)
time.sleep(0.01)
GPIO.output(RESET, GPIO.LOW)
time.sleep(0.01)

# Function to send a message
def send_message(message):
    GPIO.output(NSS, GPIO.LOW)  # Activate chip select
    # Write the message byte-by-byte
    spi.xfer2([ord(c) for c in message])
    GPIO.output(NSS, GPIO.HIGH)  # Deactivate chip select
    print(f"Sent message: {message}")

try:
    while True:
        send_message("Hello, LoRa!")
        time.sleep(5)

except KeyboardInterrupt:
    print("Transmission stopped by user.")

finally:
    GPIO.cleanup()
    spi.close()
