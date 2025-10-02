import glob
import os
import sys
import argparse
import time
import random
import numpy 
import math
import cv2
import pygame
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

client=carla.Client("localhost",2000)
client.set_timeout(10.0)
world=client.get_world()

clock=pygame.time.Clock()
settings = world.get_settings()
settings.synchronous_mode = True 
settings.fixed_delta_seconds = 0.05
world.apply_settings(settings)
traffic_manager = client.get_trafficmanager()
traffic_manager.set_synchronous_mode(True)

window_width=640
window_height=480
center_x=window_width//2
center_y=window_height//2

bp_lib=world.get_blueprint_library()
spawn_points=world.get_map().get_spawn_points()

vehicle_bp=random.choice(bp_lib.filter("*vehicle*"))
vehicle=world.try_spawn_actor(vehicle_bp,spawn_points[0])
vehicle.set_autopilot(True)

spectator=world.get_spectator()
# spectator_pos=carla.Transform(vehicle.get_transform().transform(carla.Location(x=-4,z=2.5)), vehicle.get_transform().rotation)
# spectator.set_transform(spectator_pos)

def lidar_callback(data):
    lidar_data=numpy.frombuffer(data.raw_data,dtype=numpy.float32)
    lidar_data=numpy.reshape(lidar_data,(-1,4))[:,:2]

    image=numpy.zeros((window_height,window_width,3),numpy.uint8)

    for x,y in lidar_data:
        point_x= int(center_x + x*10)
        point_y=int(center_y- y*10)
        if 0 <= point_x < window_width and 0 <= point_y < window_height:
            cv2.circle(image,(point_x,point_y), 2, (0,255,0),-1)

    if "radar_data" in globals():
        for detection in radar_data:
            velocity,altitude,azimuth= detection[0],detection[1],detection[2]
            distance=min(altitude,100)*6
            point_x= int(center_x+ distance * math.sin(azimuth))
            point_y= int(center_x- distance*math.cos(azimuth))
            color_intensity= min(255, int(velocity*20))
            cv2.circle(image,(point_x,point_y),4,(0,0,color_intensity),-1)
            end_x=int(point_x+velocity*5*math.cos(azimuth))
            end_y=int(point_y-velocity*5*math.sin(azimuth))
            cv2.arrowedLine(image,(point_x,point_y),(end_x,end_y),(255,255,0),1)
    cv2.circle(image,(center_x,center_y),8,(255,255,255),-1)
    cv2.imshow("2 BOYUTLU SENSOR", image)
    cv2.waitKey(1)

def radar_callback(data):
    global radar_data
    radar_data=numpy.frombuffer(data.raw_data,dtype=numpy.float32)
    radar_data=numpy.reshape(radar_data,(-1,4))[:,:3] 

lidar_bp=bp_lib.find("sensor.lidar.ray_cast")
lidar_pos=carla.Transform(carla.Location(z=2.5))
lidar=world.spawn_actor(lidar_bp,lidar_pos,attach_to=vehicle)
lidar.listen(lidar_callback)

radar_bp=bp_lib.find("sensor.other.radar")
radar_pos=carla.Transform(carla.Location(2.5))
radar=world.spawn_actor(radar_bp,radar_pos,attach_to=vehicle)
radar.listen(radar_callback)

all_vehicles = [vehicle]
for i in range(10):
    traffic_bp = random.choice(bp_lib.filter("*vehicle*"))
    traffic = world.try_spawn_actor(traffic_bp, random.choice(spawn_points))
    if traffic:
        traffic.set_autopilot(True, traffic_manager.get_port())
        all_vehicles.append(traffic)

try:
    while True:
        world.tick()
        clock.tick(10)
        vehicle_transform = vehicle.get_transform()
        camera_location = carla.Location(x=-10,y=8, z=8)  
        camera_rotation= carla.Rotation(yaw=-45, pitch=-20)
        spectator.set_transform(carla.Transform(
            vehicle_transform.location + camera_location, camera_rotation))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    for vehicle in world.get_actors().filter("*vehicle*"):
        vehicle.destroy()
    for sensor in world.get_actors().filter("*sensor*"):
        sensor.destroy()
    cv2.destroyAllWindows()
    print("destroyed")