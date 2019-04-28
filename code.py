"""
PyPortal Weather Comparision
==============================================
Uses open weather map API https://openweathermap.org
To display weather information for two locations side by side

Author: Rosie Hamilton
"""
import time
import board
import neopixel
import busio
from digitalio import DigitalInOut
from analogio import AnalogIn
import adafruit_adt7410

from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
from adafruit_io.adafruit_io import RESTClient, AdafruitIO_RequestError
import adafruit_esp32spi.adafruit_esp32spi_requests as requests

# thermometer graphics helper
import thermometer_helper

# rate at which to refresh the pyportal screen, in seconds
PYPORTAL_REFRESH = 2

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# PyPortal ESP32 Setup
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
try:
    ADAFRUIT_IO_USER = secrets['aio_username']
    ADAFRUIT_IO_KEY = secrets['aio_key']
    OPEN_WEATHER_KEY = secrets['open_weather_key']
except KeyError:
    raise KeyError('To use this code, you need to include your Adafruit IO username \
and password in a secrets.py file on the CIRCUITPY drive.')

# use https://openweathermap.org/find?q= to get city IDs
# then set both city IDs below
CITY_1_ID = '2641673'
CITY_2_ID = '658225'

# Create an instance of the Adafruit IO REST client
io = RESTClient(ADAFRUIT_IO_USER, ADAFRUIT_IO_KEY, wifi)


# init. graphics helper
gfx = thermometer_helper.Thermometer_GFX(celsius=True)

# init. adt7410
i2c_bus = busio.I2C(board.SCL, board.SDA)
adt = adafruit_adt7410.ADT7410(i2c_bus, address=0x48)
adt.high_resolution = True

# init. the light sensor
light_sensor = AnalogIn(board.LIGHT)


def set_backlight(val):
    """Adjust the TFT backlight.
    :param val: The backlight brightness. Use a value between ``0`` and ``1``, where ``0`` is
                off, and ``1`` is 100% brightness.
    """
    val = max(0, min(1.0, val))
    board.DISPLAY.auto_brightness = False
    board.DISPLAY.brightness = val

while True:

    
    try: # WiFi Connection
        set_backlight(1)

        print('Getting time from Adafruit IO...')
        datetime = io.receive_time()
        print('displaying time...')
        gfx.display_date_time(datetime)

        CITY_1_URL = "http://api.openweathermap.org/data/2.5/weather?id="+CITY_1_ID+"&APPID="+OPEN_WEATHER_KEY
        print("Fetching text from", CITY_1_URL)
        r = requests.get(CITY_1_URL)
        gfx.display_city_name(r.text, 1)
        gfx.display_city_temp(r.text, 1)
        gfx.display_weather_desc(r.text, 1)
        gfx.display_humid(r.text, 1)
        gfx.display_wind(r.text, 1)
        gfx.display_sun(r.text, 1)

        CITY_2_URL = "http://api.openweathermap.org/data/2.5/weather?id="+CITY_2_ID+"&APPID="+OPEN_WEATHER_KEY
        print("Fetching text from", CITY_2_URL)
        r = requests.get(CITY_2_URL)
        gfx.display_city_name(r.text, 2)
        gfx.display_city_temp(r.text, 2)
        gfx.display_weather_desc(r.text, 2)
        gfx.display_humid(r.text, 2)
        gfx.display_wind(r.text, 2)
        gfx.display_sun(r.text, 2)

    except (ValueError, RuntimeError) as e: # WiFi Connection Failure
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue
    time.sleep(PYPORTAL_REFRESH)
