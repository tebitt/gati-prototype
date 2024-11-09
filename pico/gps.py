from machine import Pin, UART
import utime

# Setup UART on RX = GP5 and TX = GP4 for the Neo-6M GPS module
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

def validate_nmea(line):
    """Validate NMEA sentence using checksum"""
    try:
        if line.startswith('$'):
            # Split sentence into data and checksum
            if '*' in line:
                sentence, checksum = line.split('*')
                # Calculate checksum
                calculated_checksum = 0
                for char in sentence[1:]:  # Skip the '$'
                    calculated_checksum ^= ord(char)
                # Compare with received checksum
                return int(checksum.strip(), 16) == calculated_checksum
    except:
        pass
    return False

def parse_gps():
    while True:
        if uart.any():
            try:
                line = uart.readline()
                if line is None:
                    continue
                
                # Handle the line whether it's bytes or string
                try:
                    if isinstance(line, bytes):
                        line = line.decode('utf-8')
                except:
                    continue
                
                # At this point, line is a string
                line = line.strip()
                
                # Validate NMEA sentence
                if not validate_nmea(line):
                    continue
                
                print(f"Raw NMEA: {line}")
                
                # Parse GPGGA sentence for fix and satellite info
                if line.startswith('$GPGGA'):
                    parts = line.split(',')
                    if len(parts) >= 15:  # GPGGA should have 15 parts
                        try:
                            fix_quality = int(parts[6])
                            num_satellites = int(parts[7])
                            
                            print(f"Fix Quality: {fix_quality} (0=No fix, 1=GPS fix)")
                            print(f"Satellites in view: {num_satellites}")
                            
                            # Only process if we have a valid fix
                            if fix_quality == 1 and parts[2] and parts[4]:
                                lat = convert_to_degrees(parts[2])
                                lon = convert_to_degrees(parts[4])
                                lat_dir = parts[3]
                                lon_dir = parts[5]
                                
                                if lat_dir == 'S':
                                    lat = -lat
                                if lon_dir == 'W':
                                    lon = -lon
                                    
                                print(f"Coordinates: {lat:.6f}, {lon:.6f}")
                                return lat, lon
                        except ValueError:
                            print("Invalid data format in GPGGA sentence")
                            continue
                
                # Parse GPRMC sentence for status
                elif line.startswith('$GPRMC'):
                    parts = line.split(',')
                    if len(parts) >= 12:  # GPRMC should have 12 parts
                        status = parts[2]
                        print(f"GPS Status: {'Valid' if status == 'A' else 'No Fix'}")
                        
            except Exception as e:
                print(f"Error processing line: {e}")
                continue
                
        utime.sleep(0.1)  # Reduced sleep time for better responsiveness

def convert_to_degrees(raw_value):
    """Convert NMEA coordinate format to decimal degrees"""
    try:
        if not raw_value:
            raise ValueError("Empty coordinate value")
            
        # Ensure the value is in the expected format
        if '.' not in raw_value:
            raise ValueError("Invalid coordinate format")
            
        decimal_point_position = raw_value.find('.') - 2
        if decimal_point_position < 0:
            raise ValueError("Invalid coordinate format")
            
        degrees = float(raw_value[:decimal_point_position])
        minutes = float(raw_value[decimal_point_position:])
        return degrees + (minutes / 60)
    except ValueError as e:
        raise ValueError(f"Error converting {raw_value}: {str(e)}")

print("GPS Module starting...")
print("Waiting for satellite fix...")
print("Make sure you have a clear view of the sky")
print("First fix can take up to 5 minutes...")

while True:
    try:
        coordinates = parse_gps()
        if coordinates:
            lat, lon = coordinates
            print("-" * 50)
            print(f"Valid Fix Obtained!")
            print(f"Latitude: {lat:.6f}")
            print(f"Longitude: {lon:.6f}")
            print("-" * 50)
    except Exception as e:
        print(f"Main loop error: {e}")
    utime.sleep(0.1)  # Reduced sleep time for better responsiveness