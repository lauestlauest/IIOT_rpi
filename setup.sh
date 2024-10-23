#!/bin/bash

# Update the system
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install pip if not installed
echo "Checking if pip is installed..."
if ! command -v pip3 &> /dev/null
then
    echo "pip not found. Installing pip..."
    sudo apt install python3-pip -y
else
    echo "pip is already installed."
fi

# Install paho-mqtt library for MQTT
echo "Installing paho-mqtt..."
pip3 install paho-mqtt

# Install RPi.GPIO for GPIO access
echo "Installing RPi.GPIO for GPIO access..."
pip3 install RPi.GPIO

# Confirmation message
echo "Setup complete. MQTT and GPIO libraries are installed!"