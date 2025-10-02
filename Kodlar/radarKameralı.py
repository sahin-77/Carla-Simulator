import glob
import os
import sys
import time
import random
import numpy as np
import cv2
from numpy import uint64
import pygame
import math

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

pygame.init()
display=pygame.display.set_mode((640,480))
pygame.display.set_caption("Radar Sensor")

def main():
    try:
        client=carla.Client("localhost",2000)
        client.set_timeout(10.0)
        world=client.get_world()

        image_w=640
        image_h=480

        settings=world.get_settings()
        settings.synchronous_mode=True
        settings.fixed_delta_seconds=0.05
        world.apply_settings(settings)

        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)

        spawn_points=world.get_map().get_spawn_points()
        bp_lib=world.get_blueprint_library()

        vehicle_bp=random.choice(bp_lib.filter("*vehicle"))
        vehicle=world.spawn_actor(vehicle_bp,random.choice(spawn_points))
        vehicle.set_autopilot(True)

        for i in range(5):
            traffic_bp=random.choice(bp_lib.filter("*vehicle"))
            traffic=world.spawn_actor(traffic_bp,random.choice(spawn_points))
            if traffic:
                traffic.set_autopilot(True)

        camera_bp=bp_lib.find("sensor.camera.rgb")
        camera_bp.set_attribute("image_size_x",f"{image_w}")
        camera_bp.set_attribute("image_size_y",f"{image_h}")
        camera_bp.set_attribute("fov","110")
        camera_pos=carla.Transform(carla.Location(x=2.4,z=1.5))
        camera=world.spawn_actor(camera_bp,camera_pos,attach_to=vehicle)

        radar_bp=bp_lib.find("sensor.other.radar")
        radar_bp.set_attribute("horizontal_fov",str(35))
        radar_bp.set_attribute("vertical_fov",str(20))
        radar_bp.set_attribute("range",str(50))
        radar_pos=carla.Transform(carla.Location(x=2.5,z=1.2))
        radar=world.spawn_actor(radar_bp,radar_pos,attach_to=vehicle)

        def rgb_callback(image):
            array=np.frombuffer(image.raw_data,dtype=np.uint8)
            array=np.reshape(array,(image_h,image_w,4))
            array=array[:,:,:3]
            array=array[:,:,::-1]
            surface=pygame.surfarray.make_surface(array.swapaxes(0,1))
            display.blit(surface,(0,0))
            pygame.display.flip()


        def radar_callback(data):
            points=np.frombuffer(data.raw_data,dtype=np.float32)
            points=np.reshape(points,(-1,4))

            for point in points:
                velocity,azimuth,altitude,depth=point
                
                azimuth_rad = math.radians(azimuth)
                altitude_rad=math.radians(altitude)
                
                x=depth * math.cos(azimuth_rad) * math.cos(altitude_rad)
                y=depth * math.sin(azimuth_rad) * math.cos(altitude_rad)
                z=depth * math.sin(altitude_rad)

                local_point=carla.Location(x=x,y=y,z=z)
                world_point= data.transform.transform(local_point)

                if velocity > 0:
                    color=carla.Color(0,0,255)
                elif velocity==0 :
                    color=carla.Color(255,255,255)
                else :
                    color=carla.Color(255,0,0)

              
                world.debug.draw_point(
                    location=world_point,size=0.1,life_time=0.1,color=color,persistent_lines=False
                    )

        camera.listen(rgb_callback)
        radar.listen(radar_callback)

        clock=pygame.time.Clock()
        running=True

        while running:
            
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running = False
            world.tick()
            clock.tick(10)
    finally:
        # camera.destroy()
        # radar.destroy()
        pygame.quit()

if __name__ == "__main__":
    main()        





