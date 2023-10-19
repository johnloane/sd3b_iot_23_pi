import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

def flash_led():
    for i in range(0, 10):
        GPIO.output(12, True)
        time.sleep(0.5)
        GPIO.output(12, False)
        time.sleep(0.5)
    GPIO.cleanup()


if __name__ == '__main__':
    flash_led()
