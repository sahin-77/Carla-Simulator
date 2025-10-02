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

# settings= world.get_settings()
# settings.synchronous_mode= True
# settings.fixed_delta_seconds=0.05
# world.apply_settings(settings)

pygame.init()
screen_width=480
screen_heigth=720
screen=pygame.display.set_mode((screen_width,screen_heigth))
pygame.display.set_caption("CAMERA")
clock=pygame.time.Clock()


spawn_points=world.get_map().get_spawn_points()
blueprints=world.get_blueprint_library()

impala_bp=blueprints.filter("*impala*")[0]
impala_start_point=spawn_points[59]
impala_pos=carla.Transform(impala_start_point.location + carla.Location(x=0,y=0,z=0),
	carla.Rotation(yaw=impala_start_point.rotation.yaw -180))
impala=world.spawn_actor(impala_bp,impala_pos)
impala_control=carla.VehicleControl(
	throttle=1.0,
	brake=0.0,
	steer=0.0
	)
impala.apply_control(impala_control)

toyota_bp=blueprints.filter("*toyota*")[0]
toyota_start_point=spawn_points[85]
toyota=world.spawn_actor(toyota_bp,toyota_start_point)
toyota_control=carla.VehicleControl(
	throttle=1.0,
	brake=0.0,
	steer=0.0
	)
toyota.apply_control(toyota_control)

def show_image_cam(image,target_surface):
	array=np.frombuffer(image.raw_data, dtype=np.uint8)
	array=np.reshape(array ,(image.height,image.width,4))	
	array=array[:, :, :3]
	# cv2.imshow("TOYOTA VİEW",i3)
	# if cv2.waitKey(10) == 27:
	# 	camera.stop
	# 	cv2.destroyAllWindows()
	pygame.surfarray.blit_array(target_surface, array.swapaxes(0,1))

# def show_image_cam2(image):
# 	i=np.array(image.raw_data, dtype=np.uint8)
# 	i2=i.reshape(image.height,image.width,4)	
# 	i3=i2[:, :, :3]
# 	cv2.imshow("İMPALA VİEW",i3)
# 	if cv2.waitKey(10) == 27:
# 		camera.stop
# 		cv2.destroyAllWindows()

cam1_surface=pygame.Surface((480,360))
cam1_bp=blueprints.find("sensor.camera.rgb")
cam1_bp.set_attribute("image_size_x","480")
cam1_bp.set_attribute("image_size_y","360")
cam1_bp.set_attribute("fov","110")
cam1_pos=carla.Transform(carla.Location(x=1.5,z=2.4))
camera1 = world.spawn_actor(cam1_bp, cam1_pos,attach_to=toyota)
camera1.listen(lambda image: show_image_cam(image,cam1_surface))
# time.sleep(20)

cam2_surface=pygame.Surface((480,360))
cam2_bp=blueprints.find("sensor.camera.rgb")
cam2_bp.set_attribute("image_size_x","480")
cam2_bp.set_attribute("image_size_y","360")
cam2_bp.set_attribute("fov","110")
cam2_pos=carla.Transform(carla.Location(x=1.5,z=2.4))
camera2 = world.spawn_actor(cam2_bp, cam2_pos,attach_to=impala)
camera2.listen(lambda image: show_image_cam(image, cam2_surface))
# time.sleep(20)

running=True
while running:
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			running=False

	screen.blit(cam1_surface, (0, 0))
	screen.blit(cam2_surface, (0, 360))
	pygame.display.flip()
	clock.tick(10)
