import glob
import os
import sys
import argparse
import time
from datetime import datetime
import random
import numpy as np
from matplotlib import cm
import open3d as o3d

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

VIRIDIS = np.array(cm.get_cmap('plasma').colors)
VID_RANGE = np.linspace(0.0, 1.0, VIRIDIS.shape[0])

def lidar_callback(point_cloud, point_list):
    data = np.copy(np.frombuffer(point_cloud.raw_data, dtype=np.dtype('f4')))
    data = np.reshape(data, (int(data.shape[0] / 4), 4))

    intensity = data[:, -1]
    intensity_col = 1.0 - np.log(intensity) / np.log(np.exp(-0.004 * 100))
    int_color = np.c_[
        np.interp(intensity_col, VID_RANGE, VIRIDIS[:, 0]),
        np.interp(intensity_col, VID_RANGE, VIRIDIS[:, 1]),
        np.interp(intensity_col, VID_RANGE, VIRIDIS[:, 2])]

    points = data[:, :-1]
    points[:, :1] = -points[:, :1]

    point_list.points = o3d.utility.Vector3dVector(points)
    point_list.colors = o3d.utility.Vector3dVector(int_color)

def add_open3d_axis(vis):

    axis = o3d.geometry.LineSet()
    axis.points = o3d.utility.Vector3dVector(np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]]))
    axis.lines = o3d.utility.Vector2iVector(np.array([
        [0, 1],
        [0, 2],
        [0, 3]]))
    axis.colors = o3d.utility.Vector3dVector(np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]]))
    vis.add_geometry(axis)


def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    try:
        original_settings = world.get_settings()
        settings = world.get_settings()
        traffic_manager = client.get_trafficmanager(8000)
        traffic_manager.set_synchronous_mode(True)

        delta = 0.05

        settings.fixed_delta_seconds = delta
        settings.synchronous_mode = True
        settings.no_rendering_mode =False
        world.apply_settings(settings)

        blueprint_library = world.get_blueprint_library()
        vehicle_bp = random.choice(blueprint_library.filter("*vehicle"))
        vehicle_transform = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_bp, vehicle_transform)
        vehicle.set_autopilot(True)
        print(vehicle)

        for i in range(50):
            traffic_bp = random.choice(world.get_blueprint_library().filter('*vehicle*'))
            traffic_vehicle = world.try_spawn_actor(traffic_bp, random.choice(world.get_map().get_spawn_points()))
            if traffic_vehicle:
                traffic_vehicle.set_autopilot(True)

        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('noise_stddev', '0.2')
        lidar_bp.set_attribute('upper_fov', "15.0")
        lidar_bp.set_attribute('lower_fov', "-25.0")
        lidar_bp.set_attribute('channels', "64.0")
        lidar_bp.set_attribute('range', "50.0")
        lidar_bp.set_attribute('rotation_frequency', str(1.0 / delta))
        lidar_bp.set_attribute('points_per_second', "500000")
        lidar=world.spawn_actor(lidar_bp,carla.Transform(carla.Location(x=0.5,z=1.8)),attach_to=vehicle)

        point_list = o3d.geometry.PointCloud()
        lidar.listen(lambda data: lidar_callback(data, point_list))

        vis = o3d.visualization.Visualizer()
        vis.create_window(
            window_name='Carla Lidar',
            width=960,
            height=540,
            left=480,
            top=270)
        vis.get_render_option().background_color = [0.05, 0.05, 0.05]
        vis.get_render_option().point_size = 1
        vis.get_render_option().show_coordinate_frame = True
        add_open3d_axis(vis)
        frame = 0
      

        while True:
            if frame == 2:
                vis.add_geometry(point_list)
            vis.update_geometry(point_list)

            vis.poll_events()
            vis.update_renderer()
            # # This can fix Open3D jittering issues:
            time.sleep(0.005)
            world.tick()

            frame += 1

    finally:
        world.apply_settings(original_settings)
        traffic_manager.set_synchronous_mode(False)
        vehicle.destroy()
        lidar.destroy()
        vis.destroy_window()
if __name__ == "__main__":
    main()

