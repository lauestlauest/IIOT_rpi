IOT-CO2
=======
This guide covers the setup for a Raspberry Pi project that uses LoRa (SX1278) and MQTT to communicate sensor data or other IoT-related data. This setup will allow your Raspberry Pi to send and receive LoRa messages and publish/subscribe to an MQTT broker.

### install git & clone & cd 
```
sudo apt install git
git clone https://github.com/lauestlauest/IIOT_rpi.git
cd IIOT_rpi

```

### Make and run the script 
```
sudo chmod +x setup.sh
./setup.sh
```

### fix serial !Not Done! 
```
sudo raspi-config
```
Navigate to Interfacing Options → SPI and enable it.
now reboot the pi 
```
sudo reboot
```

### Activate the virtual environment
```
source $HOME/rpi_mqtt_venv/bin/activate
```
### Run your Python script
```
python3 your_mqtt_script.py
```
