
import glob
import os
import sys
import time

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import time
import carla
import random
import numpy as np 
import cv2
import pygame

client=carla.Client("localhost",2000)
client.set_timeout(10.0)
world= client.get_world()

weather = carla.WeatherParameters.ClearSunset
# weather = carla.WeatherParameters(
#             cloudiness=80.0,
#             precipitation=100.0,
#             sun_altitude_angle=-10)
world.set_weather(weather)
