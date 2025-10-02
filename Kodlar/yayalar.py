
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

spawn_points=world.get_map().get_spawn_points()
blueprints=world.get_blueprint_library()

client=carla.Client("localhost",2000)
client.set_timeout(10.0)
world= client.get_world()
pedestrian_bp=blueprints.filter("0008")[0]
pedestrian_start_point=spawn_points[108]
pedestrian_pos=carla.Transform(pedestrian_start_point.location + carla.Location(y=-2.0),carla.Rotation(yaw=pedestrian_start_point.rotation.yaw -180))
pedestrian=world.spawn_actor(pedestrian_bp,pedestrian_start_point)
controller_bp=blueprints.find("controller.ai.walker")
controller=world.spawn_actor(controller_bp,carla.Transform(),attach_to=pedestrian)
controller.start()
pedestrian_location=pedestrian.get_location()
target_location=carla.Location(x=pedestrian_location.x + 5,y=pedestrian_location.y, z=pedestrian_location.z)
controller.go_to_location(target_location)
controller.set_max_speed(2.0)


pedestrian2_bp=blueprints.filter("0009")[0]
pedestrian2_start_point=spawn_points[93]
pedestrian2=world.spawn_actor(pedestrian2_bp,pedestrian2_start_point)

pedestrian3_bp=blueprints.filter("0003")[0]
pedestrian3_start_point=spawn_points[55]
pedestrian3=world.spawn_actor(pedestrian3_bp,pedestrian3_start_point)

pedestrian4_bp=blueprints.filter("0015")[0]
pedestrian4_start_point=spawn_points[53]
pedestrian4=world.spawn_actor(pedestrian4_bp,pedestrian4_start_point)
