import smbus2
from smbus2 import i2c_msg
import time
import struct

class CO2SensorDriver:
    def __init__(self, i2c_bus=1, device_address=0x61):
        self.bus = smbus2.SMBus(i2c_bus)
        self.device_address = device_address

    def check_data_ready_status(self):
        try:
            # Send command to check data status
            self.bus.write_i2c_block_data(self.device_address, 0x02, [0x02])

            time.sleep(0.012)  # Allow clock stretching

            read = i2c_msg.read(self.device_address, 3)
            self.bus.i2c_rdwr(read)
            data = list(read)

            status = (data[0] << 8) | data[1]

            print(f"Status : {status}")
                        
            return status
        
        except Exception as e:
            print(f"Error checking data status: {e}")
            return 0

    def get_i2c_data(self):
        try:
            # Send command to request data
            self.bus.write_i2c_block_data(self.device_address, 0x03, [0x00])
            time.sleep(0.12)  # Allow clock stretching
            
            read = i2c_msg.read(self.device_address, 18)
            self.bus.i2c_rdwr(read)
            data = list(read)
            
            # Parse the data into three 32-bit integers
            package = []
            for i in range(3):
                if len(data) >= (6 * (i + 1)):
                    value = (data[i * 6 + 0] << 24) | (data[i * 6 + 1] << 16) | (data[i * 6 + 3] << 8) | data[i * 6 + 4]
                    package.append(value)
                else:
                    print("Error: Not enough data available")
            
            return package
        except Exception as e:
            print(f"Error getting I2C data: {e}")
            return []

    def get_co2_temp_humidity(self):
        while self.check_data_ready_status() != 1:
            print("Waiting for data to be ready...")
            time.sleep(0.5)

        raw_data = self.get_i2c_data()

        if len(raw_data) != 3:
            print("Error: Failed to read sensor data")
            return None, None, None

        # Convert the raw data (uint32) to float using struct.unpack
        co2 = struct.unpack('>f', raw_data[0].to_bytes(4, 'big'))[0]
        temp = struct.unpack('>f', raw_data[1].to_bytes(4, 'big'))[0]
        humidity = struct.unpack('>f', raw_data[2].to_bytes(4, 'big'))[0]

        return co2, temp, humidity