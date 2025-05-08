"""
Note: This script assumes the OLED is already wired to the Raspberry Pi
"""

import adafruit_ssd1306
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

class DisplayController:

    # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
    # SPDX-License-Identifier: MIT

    """
    This demo will fill the screen with white, draw a black box on top
    and then print Hello World! in the center of the display

    This example is for use on (Linux) computers that are using CPython with
    Adafruit Blinka to support CircuitPython libraries. CircuitPython does
    not support PIL/pillow (python imaging library)!
    """

    # Use for I2C.
    # i2c = board.I2C()  # uses board.SCL and board.SDA
    # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
    # oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

    def __init__(self, width = 128, height = 32, border = 1, reset_pin = board.D4, cs_pin = board.D5, dc_pin = board.D6):
        """
        Parameters
        ----------
        width : int
            pixel width of the display
        height : int
            pixel height of the display
        border : int
            border size
        reset_pin: Board
            OLED's reset pin
        cs_pin : Board
            OLED's cs pin
        dc_pin : Board
            OLED's dc pin
        """

        # Change these to the right size for your display!
        self.WIDTH = width
        self.HEIGHT = height
        self.BORDER = border

        # Initialize the SPI Bus
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI)
        self.oled_reset = digitalio.DigitalInOut(reset_pin)
        self.oled_cs = digitalio.DigitalInOut(cs_pin)
        self.oled_dc = digitalio.DigitalInOut(dc_pin)

        self.oled = adafruit_ssd1306.SSD1306_SPI(self.WIDTH, self.HEIGHT, self.spi, self.oled_dc, self.oled_reset, self.oled_cs)

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.image = Image.new("1", (self.oled.width, self.oled.height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Load default font.
        self.font = ImageFont.load_default()

    def init_display(self):
        """
        Initialize the display.
        """
        self.clear_display()

        # Draw a white background
        self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=255, fill=255)

        # Draw a smaller inner rectangle
        self.draw.rectangle(
            (self.BORDER, self.BORDER, self.oled.width - self.BORDER - 1, self.oled.height - self.BORDER - 1),
            outline=0,
            fill=0,
        )

    def draw_text(self, text: str):
        """
        Display the desired text.

        Parameters
        ----------
        text : str
            The text to display on screen
        """

        self.clear_display()

        self.image = Image.new("1", (self.oled.width, self.oled.height))
        self.draw = ImageDraw.Draw(self.image)

        self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=255, fill=255)
        self.draw.rectangle(
            (self.BORDER, self.BORDER, self.oled.width - self.BORDER - 1, self.oled.height - self.BORDER - 1),
            outline=0,
            fill=0,
        )

        self.draw.text(
            (1, 2),
            text,
            font=self.font,
            fill=255,
        )

        # Display image
        self.oled.image(self.image)
        self.oled.show()

    def cleanup(self):
        """
        Turn off display.
        """
        self.oled.poweroff()

    def clear_display(self):
        """
        Wipes display.
        """
        # Clear display.
        self.oled.fill(0)
        self.oled.show()
