
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

spawn_points=world.get_map().get_spawn_points()
spectator= world.get_spectator()

transform= spectator.get_transform()
spectator_pos= carla.Transform(spawn_points[0].location + carla.Location(x=-30,y=20,z=15),
	carla.Rotation(yaw=spawn_points[0].rotation.yaw -45))
spectator.set_transform(spectator_pos)