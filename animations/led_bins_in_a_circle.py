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

        # update leds
        for stripe in range(self.number_of_stipes):
            led_range = self.number_of_leds_per_stipe - stripe_values[stripe]
            self.leds[stripe][:led_range] = [(0, 0, 0)] * led_range
            self.leds[stripe][led_range:] = [(255, 255, 255)] * stripe_values[stripe]

        # return led values
        return self.leds

    def output_display(self, pygame, screen):
        # draw the LED stripes
        self.offset += self.anglespeed
        for i in range(self.number_of_stipes):
            for j in range(self.number_of_leds_per_stipe):
                width, height = screen.get_size()
                center_x = width / 2
                center_y = height / 2
                radius = 0
                if width > height:
                    radius = height / 2 - self.led_size
                else:
                    radius = width / 2 - self.led_size
                x = center_x + math.cos(self.toRadians((i / self.number_of_stipes) * 360) + self.offset) * (radius - (j / self.number_of_leds_per_stipe) * radius)
                y = center_y + math.sin(self.toRadians((i / self.number_of_stipes) * 360) + self.offset) * (radius - (j / self.number_of_leds_per_stipe) * radius)

                pygame.draw.circle(screen, self.leds[i][j], (x + self.led_size // 2, y + self.led_size // 2), self.led_size // 2)
    
    def defaultConfig(self, config):
        config["ANIMATION_SETTINGS"][self.filename] = {}
        config["ANIMATION_SETTINGS"][self.filename]["ANGLE_SPEED"] = 0.01
        config["ANIMATION_SETTINGS"][self.filename]["NUMBER_OF_STRIPES"] = 20
        config["ANIMATION_SETTINGS"][self.filename]["NUMBER_OF_LEDS_PER_STRIPE"] = 10
        config["ANIMATION_SETTINGS"][self.filename]["LED_SIZE"] = 10

        with open("audio_visualizer.config", "w+") as configfile:
            json.dump(config, configfile, indent=4)
    
    def toRadians(self, degrees):
        radians = (degrees / 360) * 2 * math.pi
        return radians