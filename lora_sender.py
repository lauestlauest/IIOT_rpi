from SX127x.LoRa import LoRa
from SX127x.board_config import BOARD
import time

# Initialize the board
BOARD.setup()

class LoRaSender(LoRa):
    def __init__(self, verbose=False):
        super(LoRaSender, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([1, 0, 0, 0, 0, 0])

    def start(self):
        self.set_mode(MODE.STDBY)
        self.set_pa_config(pa_select=1)
        self.set_freq(433)
        self.set_spreading_factor(7)
        self.set_bw(7)  # 125 kHz bandwidth
        self.set_coding_rate(CODING_RATE.CR4_5)
        self.set_preamble(8)
        self.set_sync_word(0x12)
        self.write_payload(b'Hello, LoRa!')
        print("Sending message...")
        self.set_mode(MODE.TX)
        time.sleep(1)  # Give time for transmission
        self.set_mode(MODE.SLEEP)

# Instantiate and start sending
lora = LoRaSender(verbose=False)
lora.start()

try:
    while True:
        lora.write_payload(b'Hello, LoRa!')
        print(f"Message sent: {'Hello, LoRa!'}")
        time.sleep(20)  # Wait for 20 seconds before sending the next message
except KeyboardInterrupt:
    print("Stopping...")

# Cleanup
BOARD.teardown()