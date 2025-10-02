
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
world=client.load_world("Town01")

# # world.unload_map_layer(carla.MapLayer.Buildings)
# # world.unload_map_layer(carla.MapLayer.Decals)
# # world.unload_map_layer(carla.MapLayer.Foliage)
# # world.unload_map_layer(carla.MapLayer.ParkedVehicles)
# # world.unload_map_layer(carla.MapLayer.Particles)
# # world.unload_map_layer(carla.MapLayer.Props)
# # world.unload_map_layer(carla.MapLayer.Walls)

# # weather = carla.WeatherParameters.ClearSunset
# # weather = carla.WeatherParameters(
# #             cloudiness=80.0,
# #             precipitation=100.0,
# #             sun_altitude_angle=-10)
# # world.set_weather(weather)

# # spawn_points=world.get_map().get_spawn_points()
# # spectator= world.get_spectator()
# # transform= spectator.get_transform()
# # spectator_pos= carla.Transform(spawn_points[0].location + carla.Location(x=-30,y=20,z=15),
# # 	carla.Rotation(yaw=spawn_points[0].rotation.yaw -45))
# # spectator.set_transform(spectator_pos)


	

# spawn_points=world.get_map().get_spawn_points()
# blueprints=world.get_blueprint_library()
# tesla_bp=blueprints.filter("*tesla*")[1]
# tesla_start_point=spawn_points[0]
# tesla=world.spawn_actor(tesla_bp,tesla_start_point) 
# tesla_control = carla.VehicleControl(
# 	throttle=0.8,
# 	brake = 0.0,
# 	steer= 0.0
# )	
# tesla.apply_control(tesla_control)

# dodge_bp=blueprints.filter("*dodge*")[1]
# dodge_start_point=spawn_points[1]
# dodge=world.spawn_actor(dodge_bp,dodge_start_point)
# dodge_control=carla.VehicleControl(
# 	throttle=0.8,
# 	brake=0.0,
# 	steer=0.0
# 	)
# dodge.apply_control(dodge_control)

# impala_bp=blueprints.filter("*impala*")[0]
# impala_start_point=spawn_points[91]
# impala=world.spawn_actor(impala_bp,impala_start_point)
# impala_control=carla.VehicleControl(
# 	throttle=1.0,
# 	brake=0.0,
# 	steer=0.0
# 	)
# impala.apply_control(impala_control)

# toyota_bp=blueprints.filter("*toyota*")[0]
# toyota_start_point=spawn_points[94]
# toyota=world.spawn_actor(toyota_bp,toyota_start_point)
# # toyota_control=carla.VehicleControl(
# # 	throttle=1.0,
# # 	brake=0.0,
# # 	steer=0.0
# # 	)
# # toyota.apply_control(toyota_control)

# # pedestrian_bp=blueprints.filter("0008")[0]
# # pedestrian_start_point=spawn_points[108]
# # pedestrian_pos=carla.Transform(pedestrian_start_point.location + carla.Location(y=-2.0),carla.Rotation(yaw=pedestrian_start_point.rotation.yaw -180))
# # pedestrian=world.spawn_actor(pedestrian_bp,pedestrian_start_point)
# # controller_bp=blueprints.find("controller.ai.walker")
# # controller=world.spawn_actor(controller_bp,carla.Transform(),attach_to=pedestrian)
# # controller.start()
# # pedestrian_location=pedestrian.get_location()
# # target_location=carla.Location(x=pedestrian_location.x + 5,y=pedestrian_location.y, z=pedestrian_location.z)
# # controller.go_to_location(target_location)
# # controller.set_max_speed(2.0)


# # pedestrian2_bp=blueprints.filter("0009")[0]
# # pedestrian2_start_point=spawn_points[93]
# # pedestrian2=world.spawn_actor(pedestrian2_bp,pedestrian2_start_point)

# # pedestrian3_bp=blueprints.filter("0003")[0]
# # pedestrian3_start_point=spawn_points[55]
# # pedestrian3=world.spawn_actor(pedestrian3_bp,pedestrian3_start_point)

# # pedestrian4_bp=blueprints.filter("0015")[0]
# # pedestrian4_start_point=spawn_points[53]
# # pedestrian4=world.spawn_actor(pedestrian4_bp,pedestrian4_start_point)

# def show_image(image):
# 	i=np.array(image.raw_data, dtype=np.uint8)
# 	i2=i.reshape(image.height,image.width,4)	
# 	i3=i2[:, :, :3]
# 	cv2.imshow("",i3)
# 	if cv2.waitKey(10) == 27:
# 		camera.stop
# 		cv2.destroy.AllWindows()


# cam_bp=blueprints.find("sensor.camera.rgb")
# cam_bp.set_attribute("image_size_x","640")
# cam_bp.set_attribute("image_size_y","360")
# cam_bp.set_attribute("fov","110")
# cam_pos=carla.Transform(carla.Location(x=1.5,z=2.4))
# camera = world.spawn_actor(cam_bp, cam_pos,attach_to=toyota)
# camera.listen(lambda image: show_image(image))
# # time.sleep(20)

# # cam_bp=blueprints.find("sensor.camera.rgb")
# # cam_bp.set_attribute("image_size_x","640")
# # cam_bp.set_attribute("image_size_y","360")
# # cam_bp.set_attribute("fov","110")
# # cam_pos=carla.Transform(carla.Location(z=3))
# # camera = world.spawn_actor(cam_bp, cam_pos,attach_to=pedestrian)
# # camera.listen(lambda image: show_image(image))
# # time.sleep(20)

# pygame.init()
# screen=pygame.display.set_mode((200,100))

# try:
# 	while True:
# 		pygame.event.pump()
# 		key=pygame.key.get_pressed()

# 		toyota_control=carla.VehicleControl()
# 		if key[pygame.K_y]:
# 			toyota_control.throttle=1.0
# 		if key[pygame.K_h]:
# 			toyota_control.brake=1.0
# 		if key[pygame.K_g]:
# 			toyota_control.steer=-0.4
# 		if key[pygame.K_j]:
# 			toyota.control.steer=0.4
# 		if key[pygame.K_q]:
# 			toyota_control.reverse=True	 
# 		toyota.apply_control(toyota_control)
		


# finally:
# 	time.sleep(50.0)
# 	pygame.quit()