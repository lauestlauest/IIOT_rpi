import paho.mqtt.client as mqtt
import time

# Define the MQTT broker details
BROKER = "test.mosquitto.org"  # You can replace this with your broker address
PORT = 1883  # Default port for non-TLS connections
TOPIC = "test/olejensen/topic"  # The MQTT topic you want to publish to

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

# Loop to send messages every 20 seconds
try:
    while True:
        message = "Hello, MQTT!"
        client.publish(TOPIC, message)
        print(f"Message sent: {message}")
        time.sleep(20)  # Wait for 20 seconds before sending the next message
except KeyboardInterrupt:
    print("Stopping...")

# Stop the loop and disconnect from the broker
client.loop_stop()
client.disconnect()
