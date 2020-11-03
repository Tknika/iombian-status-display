#!/usr/bin/python

import logging

import digitalio
import board
import math
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735

logger = logging.getLogger(__name__)

class ST7735Controller(object):

    cs_pin = digitalio.DigitalInOut(board.CE0)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = digitalio.DigitalInOut(board.D24)
    BAUDRATE = 24000000

    def __init__(self, rotation=270, max_font_size=11):
        self.rotation = rotation
        self.diplay = None
        self.display_width = None
        self.display_height = None
        self.font_cache = {}
        self.max_font_size = max_font_size

    def initialize(self):
        spi = board.SPI()

        self.display = st7735.ST7735R(spi, rotation=self.rotation, cs=ST7735Controller.cs_pin,
                                dc=ST7735Controller.dc_pin, rst=ST7735Controller.reset_pin,
                                baudrate=ST7735Controller.BAUDRATE)
        
        if self.display.rotation % 180 == 90:
            self.display_height = self.display.width
            self.display_width = self.display.height
        else:
            self.display_height = self.display.height
            self.display_width = self.display.width
   
    def shutdown(self, message=None):
        image = Image.new("RGB", (self.display_width, self.display_height))

        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.display_width, self.display_height), fill=(255, 255, 255))
        self.display.image(image)

    def render(self, lines):
        image = Image.new("RGB", (self.display_width, self.display_height))

        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.display_width, self.display_height), fill=(255, 255, 255))
        self.display.image(image)
        
        num_lines = len(lines)
        size = math.floor(self.display_height / num_lines)
        font_size = size if size < self.max_font_size else self.max_font_size
        font = self.__get_font(font_size)
        height_step = size
        height_pos = 0

        for line in lines:
            draw.text((0, height_pos), line, font=font, fill=(0, 0, 0))
            height_pos += height_step

        self.display.image(image)

    def __get_font(self, font_size):
        cache = self.font_cache.get(font_size, None)
        if cache:
            return cache
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        self.font_cache[font_size] = font
        return font

    def __resize_image(self, original_image):
        image_ratio = original_image.width / original_image.height
        screen_ratio = self.display_width / self.display_height
        if screen_ratio > image_ratio:
            scaled_width = original_image.width * self.display_height // original_image.height
            scaled_height = self.display_height
        else:
            scaled_width = self.display_width
            scaled_height = original_image.height * self.display_width // original_image.width

        image = original_image.resize((scaled_width, scaled_height), Image.BICUBIC)
        
        x = scaled_width // 2 - self.display_width // 2
        y = scaled_height // 2 - self.display_height // 2
        image = original_image.crop((x, y, x + self.display_width, y + self.display_width))

        return image