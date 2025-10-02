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

blueprints=world.get_blueprint_library()
spawn_points=world.get_map().get_spawn_points()

vehicle_bp = blueprints.filter("*vehicle")[0]
start_point=spawn_points[0]
vehicle=world.spawn_actor(vehicle_bp,start_point)

lidar_bp= blueprints.find("sensor.lidar.ray_cast")

lidar_bp.set_attribute("channels", "32")
lidar_bp.set_attribute("range", "100")
lidar_bp.set_attribute("points_per_second", "56000")
lidar_bp.set_attribute("rotation_frequency", "10")
lidar_bp.set_attribute("upper_fov", "15")
lidar_bp.set_attribute("lower_fov", "-25")

lidar_pos=carla.Transform(carla.Location(x=0,z=2.5))
lidar_sensor=world.spawn_actor(lidar_bp,lidar_pos,attach_to=vehicle)

def lidar_callback(point_cloud):
    data=np.frombuffer(point_cloud.raw_data, dtype=np.float32)
    points=np.reshape(data, (int(data.shape[0]/4),4))
  

lidar_sensor.listen(lambda point_cloud: lidar_callback(point_cloud))

