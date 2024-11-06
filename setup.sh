#!/bin/bash

# Update the system
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install pip and venv if not installed
echo "Checking if pip and venv are installed..."
sudo apt install python3-pip python3-venv -y

# Create a virtual environment with access to system-wide packages
VENV_DIR="$HOME/rpi_mqtt_venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR with access to system packages..."
    python3 -m venv $VENV_DIR --system-site-packages
else
    echo "Virtual environment already exists at $VENV_DIR"
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_DIR/bin/activate

# Install paho-mqtt in the virtual environment
echo "Installing paho-mqtt and spidev in the virtual environment..."
pip install paho-mqtt spidev

# Check if RPi.GPIO is available from the system packages
if python3 -c "import RPi.GPIO" &> /dev/null; then
    echo "RPi.GPIO is already available from the system site packages."
else
    # Install RPi.GPIO only if not available
    echo "RPi.GPIO not found, installing RPi.GPIO..."
    pip install RPi.GPIO
fi

# Confirmation message
echo "Setup complete. MQTT and GPIO libraries are installed!"

# Deactivate the virtual environment
deactivate
