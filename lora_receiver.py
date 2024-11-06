from SX127x.LoRa import *
from SX127x.board_config import BOARD
import time

# Initialize the board
BOARD.setup()

class LoRaReceiver(LoRa):
    def __init__(self, verbose=False):
        super(LoRaReceiver, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0, 0, 0, 0, 0, 0])

    def start(self):
        self.set_mode(MODE.STDBY)
        self.set_pa_config(pa_select=1)
        self.set_freq(433)  # Use the same frequency as the transmitter
        self.set_spreading_factor(7)
        self.set_bw(7)  # 125 kHz bandwidth
        self.set_coding_rate(CODING_RATE.CR4_5)
        self.set_preamble(8)
        self.set_sync_word(0x12)
        
        print("Starting LoRa Receiver...")
        self.set_mode(MODE.RXCONTINUOUS)  # Enter continuous receive mode

    def on_rx_done(self):
        # Called when a message is received
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        print("Received message:", bytes(payload).decode("utf-8", errors="ignore"))

# Instantiate and start receiving
lora = LoRaReceiver(verbose=False)
lora.start()

try:
    # Keep the receiver running
    while True:
        # Checking for interrupt pin
        if BOARD.read_gpio_dio0() == 1:
            lora.on_rx_done()
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("Receiver stopped by user.")
finally:
    BOARD.teardown()
