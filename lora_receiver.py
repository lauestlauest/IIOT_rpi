# import time
# from SX127x.LoRa import *
# #from SX127x.LoRaArgumentParser import LoRaArgumentParser
# from SX127x.board_config import BOARD

# BOARD.setup()
# BOARD.reset()
# #parser = LoRaArgumentParser("Lora tester")


# class mylora(LoRa):
#     def __init__(self, verbose=False):
#         super(mylora, self).__init__(verbose)
#         self.set_mode(MODE.SLEEP)
#         self.set_dio_mapping([0] * 6)

#     def on_rx_done(self):
#         BOARD.led_on()
#         #print("\nRxDone")
#         self.clear_irq_flags(RxDone=1)
#         payload = self.read_payload(nocheck=True )# Receive INF
#         print ("Receive: ")
#         mens=bytes(payload).decode("utf-8",'ignore')
#         mens=mens[2:-1] #to discard \x00\x00 and \x00 at the end
#         print(mens)
#         BOARD.led_off()
#         if mens=="INF":
#             print("Received data request INF")
#             time.sleep(2)
#             print ("Send mens: DATA RASPBERRY PI")
#             self.write_payload([255, 255, 0, 0, 68, 65, 84, 65, 32, 82, 65, 83, 80, 66, 69, 82, 82, 89, 32, 80, 73, 0]) # Send DATA RASPBERRY PI
#             self.set_mode(MODE.TX)
#         time.sleep(2)
#         self.reset_ptr_rx()
#         self.set_mode(MODE.RXCONT)

#     def on_tx_done(self):
#         print("\nTxDone")
#         print(self.get_irq_flags())

#     def on_cad_done(self):
#         print("\non_CadDone")
#         print(self.get_irq_flags())

#     def on_rx_timeout(self):
#         print("\non_RxTimeout")
#         print(self.get_irq_flags())

#     def on_valid_header(self):
#         print("\non_ValidHeader")
#         print(self.get_irq_flags())

#     def on_payload_crc_error(self):
#         print("\non_PayloadCrcError")
#         print(self.get_irq_flags())

#     def on_fhss_change_channel(self):
#         print("\non_FhssChangeChannel")
#         print(self.get_irq_flags())

#     def start(self):          
#         while True:
#             self.reset_ptr_rx()
#             self.set_mode(MODE.RXCONT) # Receiver mode
#             while True:
#                 pass;
            

# lora = mylora(verbose=False)
# #args = parser.parse_args(lora) # configs in LoRaArgumentParser.py

# #     Slow+long range  Bw = 125 kHz, Cr = 4/8, Sf = 4096chips/symbol, CRC on. 13 dBm
# lora.set_pa_config(pa_select=1, max_power=21, output_power=15)
# lora.set_bw(BW.BW125)
# lora.set_coding_rate(CODING_RATE.CR4_8)
# lora.set_spreading_factor(12)
# lora.set_rx_crc(True)
# #lora.set_lna_gain(GAIN.G1)
# #lora.set_implicit_header_mode(False)
# lora.set_low_data_rate_optim(True)

# #  Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on 13 dBm
# #lora.set_pa_config(pa_select=1)



# assert(lora.get_agc_auto_on() == 1)

# try:
#     print("START")
#     lora.start()
# except KeyboardInterrupt:
#     sys.stdout.flush()
#     print("Exit")
#     sys.stderr.write("KeyboardInterrupt\n")
# finally:
#     sys.stdout.flush()
#     print("Exit")
#     lora.set_mode(MODE.SLEEP)
# BOARD.teardown()

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
spi.max_speed_hz = 5000000  # Set speed for the SPI bus

# LoRa Register Addresses (these may need adjusting based on SX1278 configuration)
REG_FIFO = 0x00  # FIFO register for reading received data
REG_OP_MODE = 0x01
REG_IRQ_FLAGS = 0x12
REG_FIFO_RX_CURRENT_ADDR = 0x10
REG_FIFO_ADDR_PTR = 0x0D
REG_PAYLOAD_LENGTH = 0x22

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

# Setup LoRa receiver mode
def setup_receiver():
    # Set to standby mode first
    write_register(REG_OP_MODE, 0x01)
    time.sleep(0.1)
    # Set to LoRa receive continuous mode
    write_register(REG_OP_MODE, 0x85)
    # Clear the IRQ register
    write_register(REG_IRQ_FLAGS, 0xFF)
    print("Receiver mode set.")
    write_register(REG_PAYLOAD_LENGTH, 0xFF)

# Check for incoming message
def check_for_message():
    irq_flags = read_register(REG_IRQ_FLAGS)
    if irq_flags & 0x40:  # Check if RX_DONE flag is set
        print("Message received!")
        
        # Clear the RX_DONE flag
        write_register(REG_IRQ_FLAGS, 0x40)  # Only clear the RX_DONE flag
        
        # Read the RX buffer
        write_register(REG_FIFO_ADDR_PTR, read_register(REG_FIFO_RX_CURRENT_ADDR))
        
        # Retrieve message from FIFO
        payload_length = read_register(REG_PAYLOAD_LENGTH)
        if payload_length > 0:  # Ensure length is greater than zero
            message = []
            for _ in range(payload_length):
                message.append(chr(read_register(REG_FIFO)))
            
            print("Received message: " + ''.join(message))
        else:
            print("Received empty message.")
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
