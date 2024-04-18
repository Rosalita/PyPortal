"""
PyPortal Weather
==============================================
Uses open weather map API https://openweathermap.org
To display weather information

Author: Rosie Hamilton
"""
import time
import board
import neopixel
import busio
from digitalio import DigitalInOut
from analogio import AnalogIn
import adafruit_adt7410
import json
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
from adafruit_io.adafruit_io import RESTClient, AdafruitIO_RequestError
import adafruit_esp32spi.adafruit_esp32spi_requests as requests

# thermometer graphics helper
import thermometer_helper

# rate at which to refresh the pyportal screen, in seconds
PYPORTAL_REFRESH = 300 # 5 mins

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

HOME_LAT = '53.43765'
HOME_LON = '-2.28148'

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

        CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?lat="+HOME_LAT+"&lon="+HOME_LON+"&appid="+OPEN_WEATHER_KEY

        print("Fetching text from", CURRENT_WEATHER_URL)
        r = requests.get(CURRENT_WEATHER_URL)
        payload = json.loads(r.text)
        print(payload)

        gfx.display_weather_icon(payload["weather"][0]["icon"], 120, 24)
        gfx.display_place_name(payload["name"])
        gfx.display_temp(payload["main"]["temp"],payload["main"]["feels_like"])

        first_desc = payload["weather"][0]["description"]

        if len(first_desc) > 18:
            words = first_desc.split(" ", 2)
            if len(words) == 2:
                line1 = words[0]
                gfx.display_weather_desc(line1)
                line2 = words[1]
                gfx.display_weather_additional_desc(line2)
            if len(words) == 3:
                line1 = words[0] + " " + words[1]
                gfx.display_weather_desc(line1)
                line2 = words[2]
                gfx.display_weather_additional_desc(line2)
        else:
            gfx.display_weather_desc(first_desc)

            if len(payload["weather"]) > 1:
                gfx.display_weather_additional_desc(payload["weather"][1]["description"])

        gfx.display_humid(payload["main"]["humidity"])
        gfx.display_wind(payload["wind"]["speed"])
        gfx.display_cloud(payload["clouds"]["all"])
        gfx.display_sunrise_sunset(payload["sys"]["sunrise"],payload["sys"]["sunset"])

    except (ValueError, RuntimeError) as e: # WiFi Connection Failure
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue
    time.sleep(PYPORTAL_REFRESH)
