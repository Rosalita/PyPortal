"""
GFX helper file for
thermometer.py
"""
import board
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font


cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)

# Fonts within /fonts folder
info_font = cwd+"/fonts/Nunito-Black-17.bdf"
temperature_font = cwd+"/fonts/Nunito-Light-75.bdf"
small_font = cwd+"/fonts/gohufont-14.bdf"
glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.:%'


class Thermometer_GFX(displayio.Group):
    def __init__(self, celsius=True, usa_date=False):
        """Creates a Thermometer_GFX object.
        :param bool celsius: Temperature displayed as F or C
        :param bool usa_date: Use mon/day/year date-time formatting.
        """
        # root displayio group
        root_group = displayio.Group(max_size=20)
        board.DISPLAY.show(root_group)
        super().__init__(max_size=20)

        self._celsius = celsius
        self._usa_date = usa_date
     

        # create background icon group
        self._icon_group = displayio.Group(max_size=1)
        self.append(self._icon_group)
        board.DISPLAY.show(self._icon_group)

        # create text object group
        self._text_group = displayio.Group(max_size=20)
        self.append(self._text_group)

        self._icon_sprite = None
        self._icon_file = None
        self._cwd = cwd
        self.set_icon(self._cwd+"/icons/pyportal_splash.bmp")
  

        print('loading fonts...')
        self.info_font = bitmap_font.load_font(info_font)
        self.info_font.load_glyphs(glyphs)

        self.small_font = bitmap_font.load_font(small_font)
        self.small_font.load_glyphs(glyphs)

        self.c_font = bitmap_font.load_font(temperature_font)
        self.c_font.load_glyphs(glyphs)
        self.c_font.load_glyphs(('°',)) # extra glyph for temperature font

        print('setting up labels...')

        self.date_text = Label(self.info_font, max_glyphs=40)
        self.date_text.x = 90
        self.date_text.y = 15
        self._text_group.append(self.date_text)

        self.time_text = Label(self.info_font, max_glyphs=40)
        self.time_text.x = 115
        self.time_text.y = 35
        self._text_group.append(self.time_text)

        self.city1_name = Label(self.small_font, max_glyphs=40)
        self.city1_name.x = 10
        self.city1_name.y = 100
        self._text_group.append(self.city1_name)

        self.city1_temp = Label(self.small_font, max_glyphs=40)
        self.city1_temp.x = 10
        self.city1_temp.y = 120
        self._text_group.append(self.city1_temp)

        self.city1_desc = Label(self.small_font, max_glyphs=40)
        self.city1_desc.x = 10
        self.city1_desc.y = 140
        self._text_group.append(self.city1_desc)

        self.city1_humid = Label(self.small_font, max_glyphs=40)
        self.city1_humid.x = 10
        self.city1_humid.y = 160
        self._text_group.append(self.city1_humid)

        self.city1_wind = Label(self.small_font, max_glyphs=40)
        self.city1_wind.x = 10
        self.city1_wind.y = 180
        self._text_group.append(self.city1_wind)

        self.city1_sunrise = Label(self.small_font, max_glyphs=40)
        self.city1_sunrise.x = 10
        self.city1_sunrise.y = 200
        self._text_group.append(self.city1_sunrise)

        self.city1_sunset = Label(self.small_font, max_glyphs=40)
        self.city1_sunset.x = 10
        self.city1_sunset.y = 220
        self._text_group.append(self.city1_sunset)


        self.city2_name = Label(self.small_font, max_glyphs=40)
        self.city2_name.x = 175
        self.city2_name.y = 100
        self._text_group.append(self.city2_name)

        self.city2_temp = Label(self.small_font, max_glyphs=40)
        self.city2_temp.x = 175
        self.city2_temp.y = 120
        self._text_group.append(self.city2_temp)

        self.city2_desc = Label(self.small_font, max_glyphs=40)
        self.city2_desc.x = 175
        self.city2_desc.y = 140
        self._text_group.append(self.city2_desc)

        self.city2_humid = Label(self.small_font, max_glyphs=40)
        self.city2_humid.x = 175
        self.city2_humid.y = 160
        self._text_group.append(self.city2_humid)

        self.city2_wind = Label(self.small_font, max_glyphs=40)
        self.city2_wind.x = 175
        self.city2_wind.y = 180
        self._text_group.append(self.city2_wind)

        self.city2_sunrise = Label(self.small_font, max_glyphs=40)
        self.city2_sunrise.x = 175
        self.city2_sunrise.y = 200
        self._text_group.append(self.city2_sunrise)

        self.city2_sunset = Label(self.small_font, max_glyphs=40)
        self.city2_sunset.x = 175
        self.city2_sunset.y = 220
        self._text_group.append(self.city2_sunset)


        # add flag images to the text group
        self.add_flag("/icons/brit.bmp", 10, 36)
        self.add_flag("/icons/finn.bmp", 175, 36)


        board.DISPLAY.show(self._text_group)
        
    def add_flag(self, path, x, y):
        self._icon_file = open(self._cwd+path, "rb")
        icon = displayio.OnDiskBitmap(self._icon_file)
        try:
            self._icon_sprite = displayio.TileGrid(icon,
                                                   pixel_shader=displayio.ColorConverter())
        except TypeError:
            self._icon_sprite = displayio.TileGrid(icon,
                                                   pixel_shader=displayio.ColorConverter(),
                                                   position=(x,y))

        self._text_group.append(self._icon_sprite)


    def display_date_time(self, io_time):
        """Parses and displays the time obtained from Adafruit IO, based on IP
        :param struct_time io_time: Structure used for date/time, returned from Adafruit IO.
        """
        self.time_text.text = '%02d:%02d'%(io_time[3],io_time[4])
        if not self._usa_date:
            self.date_text.text = '{0}/{1}/{2}'.format(io_time[2], io_time[1], io_time[0])
        else:
            self.date_text.text = '{0}/{1}/{2}'.format(io_time[1], io_time[2], io_time[0])

    def display_io_status(self, status_text):
        """Displays the current Adafruit IO status.
        :param str status_text: Description of Adafruit IO status
        """
        self.io_status_text.text = status_text

    def display_city_name(self, response_text, cityNum):
        """Displays the name of the city

        """
        data = response_text.split(",")
        name_string = data[24].split(":")
        name = name_string[1]
        name = name.strip('\"')
        
        if cityNum == 1:
            self.city1_name.text = name
        elif cityNum == 2:
            self.city2_name.text = name
    
    def display_city_temp(self, response_text, cityNum):
        """Displays the temperature in the city
        """
        data = response_text.split(",")
        temp_string = data[7].split(":")
        temp_kelvin = temp_string[2]
        temp = float(temp_kelvin) - 273.15
        temp = (round(temp, 2))

        colour = 0xFFFFFF # default white temperature colour

        if temp < 0:
            colour = 0x00FFFF # set colour to cyan if sub zero

        if temp > 25:
            colour = 0xff7700 # set colour orange if over 25C
        
        if cityNum == 1:
            self.city1_temp.color = colour
            self.city1_temp.text = str(temp)+"C"
        elif cityNum == 2:
            self.city2_temp.color = colour
            self.city2_temp.text = str(temp)+"C"


    def display_weather_desc(self, response_text, cityNum):
        """Displays the description of the weather

        """
        data = response_text.split(",")
        desc_string = data[4].split(":")
        desc = desc_string[1]
        desc = desc.strip('\"')
        
        if cityNum == 1:
            self.city1_desc.text = desc
        elif cityNum == 2:
            self.city2_desc.text = desc
    
    def display_humid(self, response_text, cityNum):
        """Displays the humidity %
        """
        data = response_text.split(",")
        humid_string = data[9].split(":")
        humid = humid_string[1]
        humid = "humidity: "+ humid +"%"

        if cityNum == 1:
            self.city1_humid.text = humid
        elif cityNum == 2:
            self.city2_humid.text = humid

    def display_wind(self, response_text, cityNum):
        """Displays the wind speed
        """
        data = response_text.split(",")
        wind_string = data[13].split(":")
        wind_ms = wind_string[2]
        wind_mph = float(wind_ms) * 2.2369362912
        wind_mph = (round(wind_mph, 2))

        wind = "wind: "+ str(wind_mph) +" MPH"

        if cityNum == 1:
            self.city1_wind.text = wind
        elif cityNum == 2:
            self.city2_wind.text = wind
    
    def display_sun(self, response_text, cityNum):
        """Displays the sun rise and sun set times in local time
        """

        data = response_text.split(",")
        sunrise_string = data[21].split(":")
        sunrise = sunrise_string[1]
        sunset_string = data[22].split(":")
        sunset = sunset_string[1]
        sunset = sunset[: len(sunset)-1] # trim trailing } char

        if cityNum == 1:
            self.city1_sunrise.text = "sunrise: "+sunrise
            self.city1_sunset.text = "sunset: "+sunset
        elif cityNum == 2:
            self.city2_sunrise.text = "sunrise: "+sunrise
            self.city2_sunset.text = "sunset: "+sunset


    def set_icon(self, filename):
        """Sets the background image to a bitmap file.

        :param filename: The filename of the chosen icon
        """
        print("Set icon to ", filename)
        if self._icon_group:
            self._icon_group.pop()

        if not filename:
            return  # we're done, no icon desired
        if self._icon_file:
            self._icon_file.close()
        self._icon_file = open(filename, "rb")
        icon = displayio.OnDiskBitmap(self._icon_file)
        try:
            self._icon_sprite = displayio.TileGrid(icon,
                                                   pixel_shader=displayio.ColorConverter())
        except TypeError:
            self._icon_sprite = displayio.TileGrid(icon,
                                                   pixel_shader=displayio.ColorConverter(),
                                                   position=(0,0))

        self._icon_group.append(self._icon_sprite)
        board.DISPLAY.refresh_soon()
        board.DISPLAY.wait_for_frame()
  
