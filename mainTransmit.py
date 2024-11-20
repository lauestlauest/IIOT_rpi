import spidev
import RPi.GPIO as GPIO
import time
from ClimateDrive import CO2SensorDriver

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)  # NSS pin for SX1278

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 5000000  # Set SPI speed to 5 MHz

# Function to write to a register
def write_register(register, value):
    GPIO.output(25, GPIO.LOW)  # Select the SX1278
    spi.xfer2([register | 0x80, value])  # Write to register
    GPIO.output(25, GPIO.HIGH)  # Deselect the SX1278

# Function to read from a register
def read_register(register):
    GPIO.output(25, GPIO.LOW)  # Select the SX1278
    response = spi.xfer2([register & 0x7F, 0x00])  # Read from register
    GPIO.output(25, GPIO.HIGH)  # Deselect the SX1278
    return response[1]

# SX1278 Initialization
def sx1278_init():
    write_register(0x01, 0x80 | 0x00)  # Set to sleep mode
    write_register(0x06, 0x6C)  # Set frequency to 433 MHz
    write_register(0x07, 0x80)
    write_register(0x08, 0x00)

    # Set base addresses
    write_register(0x0E, 0x00)  # FIFO Tx base address
    write_register(0x0F, 0x00)  # FIFO Rx base address

    # Set LNA boost
    write_register(0x0C, read_register(0x0C) | 0x03)

    # Set auto AGC
    write_register(0x26, 0x04)

    write_register(0x4D, 0x84)  # PA ramp-up time
    write_register(0x09, 0x80 | 0x0F)  # Maximum output power

    write_register(0x01, 0x80 | 0x01)  # Set to standby mode

# Function to send a packet
def send_packet(payload):
    write_register(0x01, 0x80 | 0x01)  # Set to standby mode
    write_register(0x0D, 0x00)  # Set FIFO address pointer

    #payload = [value]  # Payload to transmit
    payload_length = len(payload)
    write_register(0x22, payload_length)  # Set payload length

    # Write payload to FIFO
    for byte in payload:
        write_register(0x00, byte)
        print(f"Sent: {byte}")

    # Set to transmit mode
    write_register(0x01, 0x80 | 0x03)

    # Wait for transmission to complete
    while (read_register(0x12) & 0x08) == 0:
        time.sleep(0.01)  # Check for the TxDone flag

    write_register(0x12, 0x08)  # Clear the TxDone flag
    write_register(0x01, 0x80 | 0x01)  # Set back to standby mode


# Main Function
# def main():
#     sx1278_init()
#     co2_sensor = CO2SensorDriver()
#     # co2_sensor.get_co2_temp_humidity()

#     ID = 1  # Node

#     message = "Hello suckers!"  # Example value to send / nice
#     payload = [ord(c) for c in message]
#     print("LoRa Transmitter started")
#     while True:
#         # data = co2_sensor.get_co2_temp_humidity()
#         # if data:
#         #     # Combine ID with sensor data, converting each value to its string form
#         #     package = [str(ID)] + [str(int(value)) for value in data]  # Convert to strings
#         #     # Flatten package into characters and get their ASCII values
#         #     payload = [ord(char) for item in package for char in item]
#             send_packet(payload)
#             # print(f"Sent: {package}, Payload: {payload}")
#             time.sleep(1)

# Main Function
def main():
    sx1278_init()
    message = "Hello suckers!"  # Example value to send / nice
    payload = [ord(c) for c in message]
    print("LoRa Transmitter started")
    while True:
        #val += 1  # Example value to send / nice
        send_packet(payload)
        print(f"Sent: {message}")
        time.sleep(1)  # Transmit every 1 second
           

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        spi.close()
