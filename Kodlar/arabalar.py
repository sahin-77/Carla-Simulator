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
blueprints=world.get_blueprint_library()

tesla_bp=blueprints.filter("*tesla*")[1]
tesla_start_point=spawn_points[0]
tesla=world.spawn_actor(tesla_bp,tesla_start_point) 
# tesla_control = carla.VehicleControl(
# 	throttle=0.8,
# 	brake = 0.0,
# 	steer= 0.0
# )	
# tesla.apply_control(tesla_control)
tesla.set_autopilot(True)

dodge_bp=blueprints.filter("*dodge*")[1]
dodge_start_point=spawn_points[1]
dodge=world.spawn_actor(dodge_bp,dodge_start_point)
# dodge_control=carla.VehicleControl(
# 	throttle=0.8,
# 	brake=0.0,
# 	steer=0.0
# 	)
# dodge.apply_control(dodge_control)

impala_bp=blueprints.filter("*impala*")[0]
impala_start_point=spawn_points[91]
impala=world.spawn_actor(impala_bp,impala_start_point)
# impala_control=carla.VehicleControl(
# 	throttle=1.0,
# 	brake=0.0,
# 	steer=0.0
# 	)
# impala.apply_control(impala_control)

toyota_bp=blueprints.filter("*toyota*")[0]
toyota_start_point=spawn_points[94]
toyota=world.spawn_actor(toyota_bp,toyota_start_point)
# toyota_control=carla.VehicleControl(
# 	throttle=1.0,
# 	brake=0.0,
# 	steer=0.0
# 	)
# toyota.apply_control(toyota_control)