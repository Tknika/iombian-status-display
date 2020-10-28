#!/usr/bin/python

import logging
import math

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class EPDController(object):

    CLEAR = 0xFF

    def __init__(self, driver, max_font_size=30):
        self.driver = driver
        self.display = None
        self.display_height = None
        self.display_width = None
        self.font_cache = {}
        self.max_font_size = max_font_size

    def initialize(self):
        self.display = self.driver.EPD()
        self.display_height = self.display.width # Rotate the screen 90º
        self.display_width = self.display.height # Rotate the screen 90º
        self.display.init(self.display.FULL_UPDATE)
        self.display.Clear(self.CLEAR)

    def shutdown(self, message=None):
        if not message:
            self.display.init(self.display.FULL_UPDATE)
            self.display.Clear(self.CLEAR)
            self.display.sleep()
        else:
            self.render(message)

    def render(self, lines):
        image = Image.new('1', (self.display_width, self.display_height), 255) # 255: clear the frame
        draw = ImageDraw.Draw(image)

        self.display.init(self.display.FULL_UPDATE)
        self.display.displayPartBaseImage(self.display.getbuffer(image))

        num_lines = len(lines)
        size = math.floor(self.display_height/num_lines)
        font_size = size if size < self.max_font_size else self.max_font_size
        font = self.__get_font(font_size)
        height_step = size
        height_pos = 0

        for line in lines:
            draw.text((0, height_pos), line, font=font, fill=0)
            height_pos += height_step

        self.display.display(self.display.getbuffer(image))
        self.display.sleep()

    def __get_font(self, font_size):
        cache = self.font_cache.get(font_size, None)
        if cache:
            return cache
        font = ImageFont.truetype('Font.ttc', font_size)
        self.font_cache[font_size] = font
        return font