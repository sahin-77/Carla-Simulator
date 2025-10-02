import glob
import os
import sys
import time
import random
import numpy as np
import cv2
from numpy import uint64

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

settings=world.get_settings()
settings.synchronous_mode=True
settings.fixed_delta_seconds=0.05
world.apply_settings(settings)


spawn_points=world.get_map().get_spawn_points()
bp_lib=world.get_blueprint_library()

def radar_callback(radar_data):
    points=np.frombuffer(radar_data.raw_data,dtype=np.float32)
    points=np.reshape(points,(-1,4))
    print(f"\nAlgilanan Araclar: {len(points)}")
    for i in points:
        velocity,azimuth,depth,altitude = i
        print(f"Hiz:{velocity:.2f} | Açı:{np.degrees(azimuth):.2f}, | Mesafe: {depth:.2f}")
    if "radar" in locals():  
        radar.destroy()
    settings.synchronous_mode=False
    world.apply_settings(settings)    
try:
    vehicle_bp=random.choice(bp_lib.filter("*vehicle"))
    vehicle=world.spawn_actor(vehicle_bp,random.choice(spawn_points))
    vehicle.set_autopilot(True)

    radar_bp=bp_lib.find("sensor.other.radar") 
    radar_bp.set_attribute("horizontal_fov",str(30))
    radar_bp.set_attribute("vertical_fov",str(25))
    radar_bp.set_attribute("range",str(50))
    radar_bp.set_attribute("points_per_second",str(10000))
    radar_pos=carla.Transform(carla.Location(x=2.5,z=1.2))
    radar=world.spawn_actor(radar_bp,radar_pos)

    radar.listen(lambda data: radar_callback(data))

    world.tick()
    time.sleep(0.1)

finally:
    if "radar" in locals():
        radar.destroy()
    










