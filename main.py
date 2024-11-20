import paho.mqtt.client as mqtt
import time
from receive import LoraReceiver

# Define the MQTT broker details
BROKER = "test.mosquitto.org"  # You can replace this with your broker address
PORT = 1883  # Default port for non-TLS connections
TOPIC = "Co2/123"  # The MQTT topic you want to publish to

# Create an MQTT client object
client = mqtt.Client()

# Function to handle connection to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed with code", rc)

# Attach the on_connect function to the client
client.on_connect = on_connect

# Connect to the broker
client.connect(BROKER, PORT, 60)

# Start the loop to maintain connection with the broker
client.loop_start()

lora = LoraReceiver()
# Loop to send messages every 20 seconds
try:
    while True:
        #packet, rssi = lora.read_packet()
        packet = [49, 59, 57, 56, 54, 59, 50, 53, 59, 51, 50]
        if packet:
            decoded_packet = ''.join([chr(byte) for byte in packet])
            parts = decoded_packet.split(";")
            message = f'[{{"name":"{str(parts[0])}","temperature":{int(parts[2])},"co2":{int(parts[1])},"humidity":{int(parts[3])}}}]'
            client.publish(TOPIC, message)
            print(f"Message sent: {message}")
            time.sleep(20)  # Wait for 20 seconds before sending the next message
except KeyboardInterrupt:
    print("Stopping...")
    # lora.close()

# Stop the loop and disconnect from the broker
client.loop_stop()
client.disconnect()
