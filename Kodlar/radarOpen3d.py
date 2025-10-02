import glob
import os
import sys
import time
import random
import numpy as np
from numpy import uint64
import math
# import pygame

os.environ["OPEN3D_USE_SYSTEM_GLFW"] ="1"
os.environ["OPEN3D_USE_DIRECTX"] ="1"
os.environ["SDL_VIDEO_WINDOW_POS"]= "100,100"

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import open3d
image_w=640
image_h=480

# pygame.init()
# display=pygame.display.set_mode((640,480))
# pygame.display.set_caption("Radar Sensor")

open3d.utility.set_verbosity_level(open3d.utility.VerbosityLevel.Debug)
vis = open3d.visualization.Visualizer()
vis.create_window(window_name="Radar",width=640,height=480,left=640,top=100,visible=True)
time.sleep(10)
point_cloud=open3d.geometry.PointCloud()
vis.add_geometry(point_cloud)

# def camera_callback(image):
#     array=np.frombuffer(image.raw_data,dtype=np.uint8)
#     array=np.reshape(array,(image_h,image_w,4))
#     array=array[:,:,:3]
#     array=array[:,:,::-1]
#     surface= pygame.surfarray.make_surface(array.swapaxes(0,1))
#     display.blit(surface,(0,0))
#     pygame.display.flip()


def radar_callback(radar_data,velocity_range=7.5):
    colors=[]
    points=[]

    for detect in radar_data:
        azimuth_rad= math.radians(detect.azimuth)
        altitude_rad=math.radians(detect.altitude)
        depth=detect.depth-0.25

        x=depth * math.cos(azimuth_rad) * math.cos(altitude_rad)
        y=depth * math.sin(azimuth_rad) * math.cos(altitude_rad)
        z=depth * math.sin(altitude_rad)

        local_point=carla.Location(x=x,y=y,z=z)
        world_point= radar_data.transform.transform(local_point)

        velocity=detect.velocity
        if velocity > 0:
            color=[0,0,1]
        elif velocity==0 :
            color=[1,1,1]
        else :
            color=[1,0,0]
        
        points.append([world_point.x,world_point.y,world_point.z])
        colors.append(color)

        if points:
            point_cloud.points = open3d.utility.Vector3dVector(np.array(points))
            point_cloud.colors=open3d.utility.Vector3dVector(np.array(colors))
            vis.update_geometry(point_cloud)
            vis.poll_events()
            vis.update_renderer()

def main():
    try:
        client=carla.Client("localhost",2000)
        client.set_timeout(10.0)
        world=client.get_world()

        settings=world.get_settings()
        settings.synchronous_mode=True
        # settings.no_rendering_mode=True
        settings.fixed_delta_seconds=0.05
        world.apply_settings(settings)

        bp_lib=world.get_blueprint_library()
        spawn_points=world.get_map().get_spawn_points()

        vehicle_bp=random.choice(bp_lib.filter("*vehicle"))
        vehicle=world.spawn_actor(vehicle_bp,random.choice(spawn_points))
        vehicle.set_autopilot(True)

        # camera_bp=bp_lib.find("sensor.camera.rgb")
        # camera_bp.set_attribute("image_size_x","640")
        # camera_bp.set_attribute("image_size_y","480")
        # camera_bp.set_attribute("fov","110")
        # camera_pos=carla.Transform(carla.Location(x=2.4,z=1.5))
        # camera=world.spawn_actor(camera_bp,camera_pos,attach_to=vehicle)

        radar_bp=bp_lib.find("sensor.other.radar")
        radar_bp.set_attribute("horizontal_fov",str(35))
        radar_bp.set_attribute("vertical_fov",str(20))
        radar_bp.set_attribute("range",str(50))
        radar_pos=carla.Transform(carla.Location(x=2.5,z=1.2))
        radar=world.spawn_actor(radar_bp,radar_pos,attach_to=vehicle)

        # camera.listen(lambda image: camera_callback(image))
        radar.listen(lambda data: radar_callback(data))

        # clock = pygame.time.Clock()
        running=True
        while running:
            # for event in pygame.event.get():
            #     if event.type==pygame.QUIT:
            #         running=False
            world.tick()
            # clock.tick(30)


    finally:
        # camera.destroy()
        radar.destroy()
        # pygame.quit()
        vis.destroy_window()

if __name__ == "__main__":
    main()
     




















