import time
import RPi.GPIO as GPIO

class ActuateDriver:
    def __init__(self):
        GPIO.cleanup()  # Reset any previous configurations
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(20, GPIO.OUT)
        GPIO.setup(21, GPIO.OUT)

    def raiseFlag(self):
        GPIO.output(20, GPIO.HIGH)
        GPIO.output(21, GPIO.LOW)
    
    def lowerFlag(self):
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.HIGH)

actuator = ActuateDriver()

def main():
    while(1):
        print("Raising flag")
        actuator.raiseFlag()
        time.sleep(5)
        print("Lowering flag")
        actuator.lowerFlag()
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
