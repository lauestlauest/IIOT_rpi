# import spidev
# import RPi.GPIO as GPIO
# import time

# # Define LoRa pins
# DIO0 = 24   # LoRa DIO0
# NSS = 8     # SPI Chip Select (CE0)
# RESET = 25  # Reset pin

# # Setup GPIO
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(DIO0, GPIO.IN)
# GPIO.setup(NSS, GPIO.OUT)
# GPIO.setup(RESET, GPIO.OUT)

# # SPI Setup
# spi = spidev.SpiDev()
# spi.open(0, 0)  # Open SPI bus 0, device 0 (CE0)
# spi.max_speed_hz = 5000000  # Set speed for the SPI bus

# # Reset LoRa Module
# GPIO.output(RESET, GPIO.HIGH)
# time.sleep(0.01)
# GPIO.output(RESET, GPIO.LOW)
# time.sleep(0.01)

# # Function to send a message
# def send_message(message):
#     GPIO.output(NSS, GPIO.LOW)  # Activate chip select
#     # Write the message byte-by-byte
#     spi.xfer2([ord(c) for c in message])
#     GPIO.output(NSS, GPIO.HIGH)  # Deactivate chip select
#     print(f"Sent message: {message}")

# try:
#     while True:
#         send_message("Hello, LoRa!")
#         time.sleep(5)

# except KeyboardInterrupt:
#     print("Transmission stopped by user.")

# finally:
#     GPIO.cleanup()
#     spi.close()

import sys
from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD
# import the python libraries
BOARD.setup()
# is used to set the board and LoRa parameters
class LoRaBeacon(LoRa):

    def __init__(self, verbose=False):
        super(LoRaBeacon, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        # sleep to save power
        self.set_dio_mapping([1,0,0,0,0,0])
    def start(self):
        global args
        self.write_payload([])
        self.set_mode(MODE.TX)
        while True:
              sleep(1)
    def on_tx_done(self):
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        sys.stdout.flush()
        sleep(2)
        data=input('>>> ')
        a=[int(hex(ord(m)), 0) for m in data]
        #set format array data in 1 byte 
        print(a)
        self.write_payload(a)
        self.set_mode(MODE.TX)


lora = LoRaBeacon(verbose=False)

lora.set_pa_config(pa_select=1)

assert(lora.get_agc_auto_on() == 1)

try: sleep(0.001)
except: pass

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    sys.stderr.write("KeyboardInterrupt\n")
 #print the transmitted values on the console and terminate the program using a keyboard interrupt   
finally:
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
