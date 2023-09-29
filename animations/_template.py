import inspect
import json
pass

class Animation():
    def __init__(self, config):
        self.filename = inspect.getsourcefile(Animation).split("/")[-1][:-3]
        try:
            myconfig = config["ANIMATION_SETTINGS"][self.filename]
            pass
        except Exception as _:
            self.defaultConfig(config)
            quit()

    def process_samples(self, samples):
        pass

    def output_display(self, pygame, screen):
        pass
    
    def defaultConfig(self, config):
        config["ANIMATION_SETTINGS"][self.filename] = {}
        config["ANIMATION_SETTINGS"][self.filename]["PARAMETER"] = 'value'
        pass

        with open("audio_visualizer.config", "w+") as configfile:
            json.dump(config, configfile, indent=4)
            quit()