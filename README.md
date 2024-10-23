IOT-CO2
=======
# install git 
sudo apt install git

# Clone the Git repository
git clone https://github.com/lauestlauest/IIOT_rpi.git

# Navigate into the cloned repository directory
cd IIOT_rpi

# Make the script executable
chmod +x setup.sh

# Run the script
./setup.sh


# Activate the virtual environment
source $HOME/rpi_mqtt_venv/bin/activate

# Run your Python script
python3 your_mqtt_script.py
