
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
# world=client.load_world("Town01")

world.unload_map_layer(carla.MapLayer.Buildings)
world.unload_map_layer(carla.MapLayer.Decals)
world.unload_map_layer(carla.MapLayer.Foliage)
world.unload_map_layer(carla.MapLayer.ParkedVehicles)
world.unload_map_layer(carla.MapLayer.Particles)
world.unload_map_layer(carla.MapLayer.Props)
world.unload_map_layer(carla.MapLayer.Walls)