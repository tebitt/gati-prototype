import time
import ujson
import re
from machine import UART, Pin

uart = UART(0, baudrate=115200, tx=Pin(16), rx=Pin(17))

def send_cmd(cmd, delay=2000):
    """Send a command to the ESP-01 and wait for a response."""
    uart.write(cmd + '\r\n')
    time.sleep_ms(delay)
    response = uart.read()
    if response:
        print(response.decode())
    return response

# Connect to WiFi and check connection status
def connect_to_wifi(ssid, password):
    send_cmd('AT+CWMODE=1')  # Set WiFi mode to Station
    response = send_cmd(f'AT+CWJAP="{ssid}","{password}"', delay=5000)  # Connect to WiFi
    if response and b"WIFI CONNECTED" in response:
        print("Connected to WiFi successfully.")
        return True
    else:
        print("Failed to connect to WiFi.")
        return False

# Replace with your WiFi credentials
ssid = "your_wifi_ssid"
password = "your_wifi_password"

if connect_to_wifi(ssid, password):
    # Get the public IP by making a request to ifconfig.me
    send_cmd('AT+CIPSTART="TCP","ifconfig.me",80')  # Connect to ifconfig.me
    time.sleep(1)

    # Send GET request to ifconfig.me to retrieve the public IP
    request = 'GET /ip HTTP/1.1\r\nHost: ifconfig.me\r\n\r\n'
    send_cmd(f'AT+CIPSEND={len(request)}')
    time.sleep(1)

    # Send the actual request
    uart.write(request)
    time.sleep(2)

    # Read the response to get the public IP address
    response = uart.read()
    public_ip = None
    if response:
        response_text = response.decode()
        print("Public IP Response:", response_text)  # Debugging print
        # Use regex to extract the IP address
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', response_text)
        if ip_match:
            public_ip = ip_match.group(1)
            print("Public IP Address:", public_ip)
        else:
            print("Failed to parse public IP address.")
    
    if public_ip:
        # Connect to ipinfo.io to get geolocation data using the public IP address
        send_cmd(f'AT+CIPSTART="TCP","ipinfo.io",80')
        time.sleep(1)

        # Send HTTP GET request to ipinfo.io with the public IP and token
        api_token = "your_ipinfo_io_api_token" 
        request = f'GET /json?token={api_token} HTTP/1.1\r\nHost: ipinfo.io\r\n\r\n'
        send_cmd(f'AT+CIPSEND={len(request)}')
        time.sleep(1)

        # Send the actual geolocation request
        uart.write(request)
        time.sleep(2)

        # Read and parse the JSON response for geolocation data
        response = uart.read()
        if response:
            response_text = response.decode()
            print("Geolocation Response:", response_text)  # Debugging print

            # Parse the JSON part of the response
            try:
                json_start = response_text.find('{')
                json_data = response_text[json_start:]
                data = ujson.loads(json_data)
                print(data)
            except Exception as e:
                print("Error parsing JSON:", e)
        else:
            print("No response received from ipinfo.io.")
    else:
        print("Failed to retrieve public IP address.")
else:
    print("WiFi connection failed. Please check your credentials and try again.")
