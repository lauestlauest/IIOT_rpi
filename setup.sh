#!/bin/bash

# Update the system
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install pip and venv if not installed
echo "Checking if pip and venv are installed..."
sudo apt install python3-pip python3-venv -y

# Define the virtual environment directory
VENV_DIR="$HOME/rpi_mqtt_venv"

# Check if we can create the virtual environment in the specified directory
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists at $VENV_DIR"
fi

# Ensure the activate script exists
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "Activating the virtual environment..."
    # Activate the virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install necessary Python packages
    echo "Installing paho-mqtt and spidev in the virtual environment..."
    pip install --upgrade pip  # Upgrade pip within the venv
    pip install paho-mqtt spidev
    pip install SX127x

    # Check if RPi.GPIO is available from system packages
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
else
    echo "Error: Unable to activate the virtual environment. Check permissions on $VENV_DIR."
fi
