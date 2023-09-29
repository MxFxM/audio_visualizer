import json
import threading
import pygame
from pygame.locals import *
import pyaudio
import numpy as np
import importlib
import time
import os
import sys

##################################################################################################
# Global Flags                                                                                   #
##################################################################################################

stop_threads_flag = False



##################################################################################################
# Display the animation in a pygame window                                                       #
##################################################################################################

class AnimationDisplay(threading.Thread):
    def __init__(self, config, animation):
        threading.Thread.__init__(self)
        self.running = False
        self.framerate = config["PYGAME"]["FRAMERATE"]
        self.background = (config["PYGAME"]["BACKGROUND_COLOR_R"], config["PYGAME"]["BACKGROUND_COLOR_G"], config["PYGAME"]["BACKGROUND_COLOR_B"])
        self.animation = animation

    def run(self):
        global stop_threads_flag

        # initialize Pygame
        pygame.init()

        # set window size
        #screen = pygame.display.set_mode((700, 1000))
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        # set the window title
        pygame.display.set_caption("Audio Visualizer")

        # set desired framerate and initialize the clock
        clock = pygame.time.Clock()

        # run the animation loop
        self.running = True
        while self.running:
            for event in pygame.event.get():
                # quit on window colsed
                if event.type == pygame.QUIT:
                    self.running = False
                # quit on esc key
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False

            # fill the background with the background color
            screen.fill(self.background)

            # run the animation
            self.animation.output_display(pygame, screen)

            # update the display
            pygame.display.update()

            # limit the framerate to 60Hz
            clock.tick(self.framerate)

        # quit Pygame
        pygame.quit()

        # stop other threads
        stop_threads_flag = True



##################################################################################################
# Capture the audio and preprocess it for the animations                                         #
##################################################################################################

class AudioThread(threading.Thread):
    def __init__(self, config, animation):
        super().__init__()
        self.stop_event = threading.Event()
        self.chunk = config["PYAUDIO"]["CHUNK"]
        self.channels = config["PYAUDIO"]["CHANNELS"]
        self.rate = config["PYAUDIO"]["RATE"]
        self.animation = animation

    def run(self):
        global leds
        global stop_threads_flag

        # define the audio recording parameters
        CHUNK = self.chunk
        FORMAT = pyaudio.paInt16
        CHANNELS = self.channels
        RATE = self.rate

        # initialize the audio stream
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        # start recording
        while not self.stop_event.is_set():
            # check global flag to stop executing
            if stop_threads_flag:
                break

            # read audio data from the stream
            data = stream.read(CHUNK)

            # convert the audio data to a numpy array
            audio_samples = np.frombuffer(data, dtype=np.int16)

            # feed into animation
            animation.process_samples(audio_samples)

        # stop recording
        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self.stop_event.set()
if __name__ == "__main__":
    with open("audio_visualizer.config", 'r') as configfile:
        config = json.load(configfile)
    
    animation_module_name = f"animations.{config['ANIMATION']['SELECTED_ANIMATION']}"
    animation_module = importlib.import_module(animation_module_name)
    animation = animation_module.Animation(config)

    display = AnimationDisplay(config, animation)
    display.start()

    audio = AudioThread(config, animation)
    audio.start()

    """
    while True:
        time.sleep(5)

        if True:
            os.execv(os.path.abspath(sys.argv[0]), sys.argv)
    """