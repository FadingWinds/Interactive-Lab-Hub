import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789


# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# -- Added Code Starts-- 
alarm_text_visible = False
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

try:
    alarm_hour, alarm_minute = input('Please enter the alarm time (HH MM): ').split(' ')
except ValueError as e:
    print('Input Not Acceptble')

alarm_text = 'Alarm at ' + alarm_hour + ':' + alarm_minute
alarm_blink = False
alarm_color = False
# -- Added Code Ends --

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    #TODO: fill in here. You should be able to look in cli_clock.py and stats.py
    time_shown = time.strftime("%m/%d/%Y %H:%M:%S")
    second_angle = (int(time.strftime("%S")) + 45) * 6
    minute_angle = (int(time.strftime("%M")) + 45) * 6
    hour_angle = (int(time.strftime("%H")) % 12 + 9) * 30

    draw.text((0.5, 0.5), time_shown, font=font, fill="#FFFFFF")
    
    draw.pieslice((30, 40, 100, 110), start=second_angle-1, 
        end=second_angle, outline="#0000FF")
    draw.pieslice((30, 40, 100, 110), start=minute_angle-1, 
        end=minute_angle, outline="#FFFF00")
    draw.pieslice((30, 40, 100, 110), start=hour_angle-1, 
        end=hour_angle, outline="#00FF00")
    draw.arc((30, 40, 100, 110), start=0, end=360, fill="#FFFFFF")
    draw.regular_polygon((65, 75, 40), n_sides=12, outline="#FFFFFF")

    if alarm_text_visible:
        draw.text((110, 40), alarm_text, font=font, fill="#FFFFFF")

    if int(time.strftime('%M')) == int(alarm_minute) and int(time.strftime('%H')) == int(
        alarm_hour) and int(time.strftime('%S')) < 5:
        alarm_blink = True
    if alarm_blink:
        if not alarm_color:
            draw.rectangle((120, 65, 220, 110), fill='#FF0000')
        alarm_color = not alarm_color

    # Display image.
    disp.image(image, rotation)
    if buttonA.value and not buttonB.value:
        alarm_text_visible = not alarm_text_visible
    if buttonB.value and not buttonA.value:
        alarm_blink = False
    time.sleep(0.3)