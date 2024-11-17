import spidev
import RPi.GPIO as GPIO
import time


spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0 (CE0)
spi.max_speed_hz = 5000  # Set speed for the SPI bus
spi.mode = 0b01  # Set SPI mode to 0

to_send = [0x01, 0x02, 0x03]

spi.xfer2(to_send)

try:
    while True:
        spi.xfer2(to_send)
        time.sleep(1)

except KeyboardInterrupt:
    print("Transmission stopped by user.")

finally:
    spi.close()