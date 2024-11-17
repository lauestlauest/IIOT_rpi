import spidev
import RPi.GPIO as GPIO
import time


spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0 (CE0)
spi.max_speed_hz = 1000000  # Set speed for the SPI bus

try:
    while True:
        spi.writebytes([0x3A])
        time.sleep(1)

except KeyboardInterrupt:
    print("Transmission stopped by user.")

finally:
    spi.close()