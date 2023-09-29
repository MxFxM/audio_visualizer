import inspect
import json
import numpy as np
import pygame
import math

class Animation():
    def __init__(self, config):
        self.filename = inspect.getsourcefile(Animation).split("/")[-1][:-3]
        try:
            myconfig = config["ANIMATION_SETTINGS"][self.filename]
            self.hue = 0
            self.hue_offset = myconfig["HUE_OFFSET"]
            self.hue_change_speed = myconfig["HUE_CHANGE_SPEED"]
            self.offset = 0
            self.anglespeed = myconfig["ANGLE_SPEED"]
            self.number_of_stipes = myconfig["NUMBER_OF_STRIPES"]
            self.number_of_leds_per_stipe = myconfig["NUMBER_OF_LEDS_PER_STRIPE"]
            self.leds = [[] for _ in range(self.number_of_stipes)]
            self.led_size = myconfig["LED_SIZE"]
            for stripe in self.leds:
                for led in range(self.number_of_leds_per_stipe):
                    # set LED color
                    led_color = pygame.Color([0, 0, 0])
                    stripe.append(led_color)
        except Exception as _:
            self.defaultConfig(config)
            quit()

    def process_samples(self, samples):
        # process values for the strips
        fft_result = np.abs(np.fft.fft(samples))
        stripe_values = fft_result[:self.number_of_stipes]
        maxval = np.max(stripe_values)
        if maxval == 0:
            maxval = 0.001
        stripe_values = [int((v/maxval)*self.number_of_leds_per_stipe) for v in stripe_values]

        # get hue
        self.hue += self.hue_change_speed
        if self.hue > 255:
            self.hue -= 255

        # update leds
        for stripe in range(self.number_of_stipes):
            led_range = self.number_of_leds_per_stipe - stripe_values[stripe]
            self.leds[stripe][:led_range] = [(0, 0, 0)] * led_range
            r, g, b = self.toRgb(self.hue + stripe * self.hue_offset, 255, 255)
            self.leds[stripe][led_range:] = [(r, g, b)] * stripe_values[stripe]

        # return led values
        return self.leds

    def output_display(self, pygame, screen):
        # draw the LED stripes
        self.offset += self.anglespeed
        if self.offset > 360:
            self.offset -= 360
        for i in range(self.number_of_stipes):
            for j in range(self.number_of_leds_per_stipe):
                if self.leds[i][j] == (0, 0, 0):
                    continue
                width, height = screen.get_size()
                radius = 0
                if width > height:
                    # landscape mode
                    center_x1 = width / 4
                    center_y1 = height / 2
                    center_x2 = width * 3 / 4
                    center_y2 = height / 2
                    radius = width / 4 - self.led_size
                else:
                    center_x1 = width / 2
                    center_y1 = height / 4
                    center_x2 = width / 2
                    center_y2 = height * 3 / 4
                    radius = height / 4 - self.led_size
                x_off = math.cos(self.toRadians((i / self.number_of_stipes) * 360) + self.offset) * (radius - (j / self.number_of_leds_per_stipe) * radius)
                y_off = math.sin(self.toRadians((i / self.number_of_stipes) * 360) + self.offset) * (radius - (j / self.number_of_leds_per_stipe) * radius)
                x1 = center_x1 + x_off
                y1 = center_y1 + y_off
                x2 = center_x2 + x_off
                y2 = center_y2 + y_off

                pygame.draw.circle(screen, self.leds[i][j], (x1 + self.led_size // 2, y1 + self.led_size // 2), self.led_size // 2)
                pygame.draw.circle(screen, self.leds[i][j], (x2 + self.led_size // 2, y2 + self.led_size // 2), self.led_size // 2)
    
    def defaultConfig(self, config):
        config["ANIMATION_SETTINGS"][self.filename] = {}
        config["ANIMATION_SETTINGS"][self.filename]["ANGLE_SPEED"] = 0.01
        config["ANIMATION_SETTINGS"][self.filename]["NUMBER_OF_STRIPES"] = 36
        config["ANIMATION_SETTINGS"][self.filename]["NUMBER_OF_LEDS_PER_STRIPE"] = 20
        config["ANIMATION_SETTINGS"][self.filename]["LED_SIZE"] = 10
        config["ANIMATION_SETTINGS"][self.filename]["HUE_OFFSET"] = 7
        config["ANIMATION_SETTINGS"][self.filename]["HUE_CHANGE_SPEED"] = 1

        with open("audio_visualizer.config", "w+") as configfile:
            json.dump(config, configfile, indent=4)
    
    def toRadians(self, degrees):
        radians = (degrees / 360) * 2 * math.pi
        return radians

    def toRgb(self, h, s, v):
        if h > 255:
            h -= 255
        h = h / 255.0
        s = s / 255.0
        v = v / 255.0
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        if i % 6 == 0:
            r, g, b = v, t, p
        elif i % 6 == 1:
            r, g, b = q, v, p
        elif i % 6 == 2:
            r, g, b = p, v, t
        elif i % 6 == 3:
            r, g, b = p, q, v
        elif i % 6 == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        return (int(r * 255), int(g * 255), int(b * 255))