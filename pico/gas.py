from machine import Pin, PWM, ADC, UART
import time

# Define pins
mq2_pin = ADC(Pin(26))  # Connect MQ-2 analog output to ADC pin 26
buzzer = PWM(Pin(18))  # Use PWM for the piezo buzzer on GPIO 18
gps = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))


# Threshold for gas detection
gas_threshold = 30000

def buzz():
    # Set PWM frequency for a loud buzzing sound
    buzzer.freq(1000)  # Set frequency to 1000 Hz
    buzzer.duty_u16(30000)  # Set duty cycle to 50% for loudness
    time.sleep(0.5)  # Buzz duration (adjust as needed)
    buzzer.duty_u16(0)  # Stop the buzzer

def detect_gas():
    # Read the analog value from the MQ-2 sensor
    gas_level = mq2_pin.read_u16()  # 16-bit resolution (0 to 65535)
    print("Gas level:", gas_level)
    # Check if gas level exceeds threshold
    if gas_level > gas_threshold:
        buzz()  # Trigger buzzing sound
        print("Gas leak detected!")
    else:
        buzzer.duty_u16(0)  # Ensure buzzer is off when below threshold

# Main loop
while True:
    detect_gas()
    response = gps.read()
    if response:
        response_text = response.decode()
        print(response_text)
    time.sleep(1)
