import glob
import os
import sys
import time
import random
import numpy as np
import math
import pyvista as pv

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

image_w = 640
image_h = 480

# PyVista plotter oluşturma
plotter = pv.Plotter(window_size=(image_w, image_h), title="Radar")
plotter.background_color = (0.1, 0.1, 0.1)  # Koyu arka plan
plotter.window.set_window_position(640, 100)  # Pencere konumu
plotter.enable_anti_aliasing()  # Kenar yumuşatma

# Boş nokta bulutu oluştur
point_cloud = pv.PolyData(np.empty((0, 3)))
plotter.add_mesh(
    point_cloud,
    point_size=5,
    render_points_as_spheres=True,
    scalars=np.empty((0, 3)),
    rgb=True,
    name="radar_points"
)

def radar_callback(radar_data, velocity_range=7.5):
    points = []
    colors = []

    for detect in radar_data:
        azimuth_rad = math.radians(detect.azimuth)
        altitude_rad = math.radians(detect.altitude)
        depth = detect.depth - 0.25

        x = depth * math.cos(azimuth_rad) * math.cos(altitude_rad)
        y = depth * math.sin(azimuth_rad) * math.cos(altitude_rad)
        z = depth * math.sin(altitude_rad)

        local_point = carla.Location(x=x, y=y, z=z)
        world_point = radar_data.transform.transform(local_point)

        velocity = detect.velocity
        if velocity > 0:
            color = [0, 0, 1]  # Mavi (ileri hareket)
        elif velocity == 0:
            color = [1, 1, 1]  # Beyaz (durağan)
        else:
            color = [1, 0, 0]  # Kırmızı (geri hareket)
        
        points.append([world_point.x, world_point.y, world_point.z])
        colors.append(color)

    # Nokta bulutunu güncelle
    if points:
        points_array = np.array(points)
        colors_array = np.array(colors) / 255.0  # PyVista 0-1 arası renk bekler
        
        # Mevcut nokta bulutunu güncelle
        point_cloud.points = points_array
        point_cloud['colors'] = colors_array
        plotter.update_coordinates(point_cloud.points, mesh=point_cloud)
        plotter.update_scalars(colors_array, mesh=point_cloud)

def main():
    try:
        client = carla.Client("localhost", 2000)
        client.set_timeout(10.0)
        world = client.get_world()

        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        world.apply_settings(settings)

        bp_lib = world.get_blueprint_library()
        spawn_points = world.get_map().get_spawn_points()

        vehicle_bp = random.choice(bp_lib.filter("*vehicle"))
        vehicle = world.spawn_actor(vehicle_bp, random.choice(spawn_points))
        vehicle.set_autopilot(True)

        radar_bp = bp_lib.find("sensor.other.radar")
        radar_bp.set_attribute("horizontal_fov", str(35))
        radar_bp.set_attribute("vertical_fov", str(20))
        radar_bp.set_attribute("range", str(50))
        radar_pos = carla.Transform(carla.Location(x=2.5, z=1.2))
        radar = world.spawn_actor(radar_bp, radar_pos, attach_to=vehicle)

        radar.listen(lambda data: radar_callback(data))

        # Ana görselleştirme döngüsü
        running = True
        while running:
            world.tick()
            
            # PyVista olaylarını işle ve render et
            plotter.update()
            if plotter.iren:
                plotter.iren.process_events()
                if plotter.iren.is_done():
                    running = False

    finally:
        radar.destroy()
        plotter.close()  # PyVista penceresini kapat

if __name__ == "__main__":
    main()