from transmitt import LoraTransmitter
import time
import spidev
import RPi.GPIO as GPIO

# Initialize the SX1278
lora = LoraTransmitter()

# Main Function
def main():
    lora.sx1278_init()
    message = "Hello suckers!"  # Example value to send / nice
    payload = [ord(c) for c in message]
    print("LoRa Transmitter started")
    while True:
        #val += 1  # Example value to send / nice
        lora.send_packet(payload)
        print(f"Sent: {message}")
        time.sleep(1)  # Transmit every 1 second

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        lora.__del__()