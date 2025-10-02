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

client = carla.Client('localhost', 2000)
world = client.get_world()

spawn_points=world.get_map().get_spawn_points()
bp_lib=world.get_blueprint_library()

settings = world.get_settings()
settings.synchronous_mode = True
settings.fixed_delta_seconds=0.05
world.apply_settings(settings)

traffic_manager = client.get_trafficmanager()
traffic_manager.set_synchronous_mode(True)

vehicle_bp=bp_lib.find('vehicle.audi.tt')
vehicle_start_point=random.choice(spawn_points)
vehicle=world.spawn_actor(vehicle_bp,vehicle_start_point)
vehicle.set_autopilot(True)

# spectator=world.get_spectator()
# spectator_pos=carla.Transform(vehicle.get_transform().transform(carla.Location(y=1.5,z=2.4)),vehicle.get_transform().rotation)
# spectator.set_transform(spectator_pos)

for i in range(10):
    traffic_bp = random.choice(world.get_blueprint_library().filter('*vehicle*'))
    traffic_vehicle = world.try_spawn_actor(traffic_bp, random.choice(spawn_points))
    if traffic_vehicle:
        traffic_vehicle.set_autopilot(True)

camera_start_point= carla.Transform(carla.Location(z=2))

camera_bp=bp_lib.find("sensor.camera.rgb")
camera=world.spawn_actor(camera_bp,camera_start_point,attach_to=vehicle)

semantic_cam_bp=bp_lib.find("sensor.camera.semantic_segmentation")
semantic_cam=world.spawn_actor(semantic_cam_bp,camera_start_point,attach_to=vehicle)

instance_cam_bp=bp_lib.find("sensor.camera.instance_segmentation")
instance_cam=world.spawn_actor(instance_cam_bp,camera_start_point,attach_to=vehicle)

depth_cam_bp=bp_lib.find("sensor.camera.depth")
depth_cam=world.spawn_actor(depth_cam_bp,camera_start_point,attach_to=vehicle)

dvs_cam_bp=bp_lib.find("sensor.camera.dvs")
dvs_cam=world.spawn_actor(dvs_cam_bp,camera_start_point,attach_to=vehicle)

optical_cam_bp=bp_lib.find("sensor.camera.optical_flow")
optical_cam=world.spawn_actor(optical_cam_bp,camera_start_point,attach_to=vehicle)

def rgb_callback(image,data_dict):
    data_dict["rgb_image"] = np.reshape(np.copy(image.raw_data), (image.height,image.width, 4))

def semantic_callback(image,data_dict):
    image.convert(carla.ColorConverter.CityScapesPalette)
    data_dict["semantic_image"]=np.reshape(np.copy(image.raw_data), (image.height,image.width, 4))

def instance_callback(image,data_dict):
    data_dict["instance_image"]=np.reshape(np.copy(image.raw_data), (image.height,image.width,4))

def depth_callback(image,data_dict):
    image.convert(carla.ColorConverter.LogarithmicDepth)
    data_dict["depth_image"]=np.reshape(np.copy(image.raw_data), (image.height,image.width, 4))

def optical_callback(image,data_dict):
    image = image.get_color_coded_flow()
    optical_img=np.reshape(np.copy(image.raw_data),(image.height,image.width,4))
    optical_img[ :, :, 3]=255
    data_dict["optical_image"]=optical_img

def dvs_callback(image,data_dict):
    dvs_events= np.frombuffer(image.raw_data, dtype=np.dtype(
        [("x", np.uint16), ("y",np.uint16), ("t", uint64), ("pol",np.bool)]))
    data_dict["dvs_image"]=np.zeros((image.height,image.width,4),dtype=np.uint8)
    dvs_img=np.zeros((image.height,image.width,3),dtype=np.uint8)
    dvs_img[dvs_events[:]["y"], dvs_events[:]["x"], dvs_events[:]["pol"]*2]=255
    data_dict["dvs_image"][:,:,0:3]=dvs_img

image_w=camera_bp.get_attribute("image_size_x").as_int()
image_h=camera_bp.get_attribute("image_size_y").as_int()

sensor_data={"rgb_image": np.zeros((image_h,image_w,4)),
   "semantic_image":np.zeros((image_h,image_w,4)),
   "instance_image": np.zeros((image_h,image_w,4)),
   "depth_image":np.zeros((image_h,image_w,4)),
   "optical_image":np.zeros((image_h,image_w,4)),
   "dvs_image": np.zeros((image_h,image_w,4))}

cv2_height=640
cv2_width=800
cv2.namedWindow("Tum Kameralar", cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow("Tum Kameralar", cv2_width, cv2_height)

top_row=np.concatenate((sensor_data["rgb_image"], sensor_data["semantic_image"]),axis=1)
mid_row=np.concatenate((sensor_data["instance_image"], sensor_data["depth_image"]),axis=1)
lower_row=np.concatenate((sensor_data["optical_image"], sensor_data["dvs_image"]),axis=1)
resized_Window=np.concatenate((top_row,mid_row,lower_row),axis=0)

cv2.imshow("Tum Kameralar",resized_Window)
cv2.waitKey(1)

camera.listen(lambda image: rgb_callback(image,sensor_data))
semantic_cam.listen(lambda image: semantic_callback(image,sensor_data))
instance_cam.listen(lambda image: instance_callback(image,sensor_data))
depth_cam.listen(lambda image: depth_callback(image,sensor_data))
optical_cam.listen(lambda image: optical_callback(image,sensor_data))
dvs_cam.listen(lambda image: dvs_callback(image,sensor_data))

try:
    while True:
        world.tick()
  
        top_row=np.concatenate((sensor_data["rgb_image"],sensor_data["semantic_image"]),axis=1)
        mid_row=np.concatenate((sensor_data["instance_image"], sensor_data["depth_image"]),axis=1)
        lower_row=np.concatenate((sensor_data["optical_image"], sensor_data["dvs_image"]),axis=1)
        resized_Window=np.concatenate((top_row,mid_row,lower_row),axis= 0)
        resized_Window= cv2.resize(resized_Window,(cv2_width,cv2_height), interpolation=cv2.INTER_AREA)
        cv2.imshow("Tum Kameralar",resized_Window)
        if cv2.waitKey(1) == ord("q"):
            break
finally:
    camera.stop()
    semantic_cam.stop()
    instance_cam.stop()
    depth_cam.stop()
    optical_cam.stop()
    dvs_cam.stop()
    cv2.destroyAllWindows()