import glob
import os
import sys
import time
import random
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

# Matplotlib 3D görselleştirme ayarları
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.set_title('Radar Verileri')
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.set_zlim(-5, 5)
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)  # Kenar boşluklarını azalt

# Renkler için boş scatter plot
scatter = ax.scatter([], [], [], s=20, alpha=0.7)

# Verileri saklamak için global değişkenler
points_array = np.empty((0, 3))
colors_array = []

def radar_callback(radar_data, velocity_range=7.5):
    global points_array, colors_array
    
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
            color = 'b'  # Mavi (ileri hareket)
        elif velocity == 0:
            color = 'w'  # Beyaz (durağan)
        else:
            color = 'r'  # Kırmızı (geri hareket)
        
        points.append([world_point.x, world_point.y, world_point.z])
        colors.append(color)
    
    # Verileri global değişkenlere kaydet
    if points:
        points_array = np.array(points)
        colors_array = colors

def update_plot():
    """Plot'u güncelleme fonksiyonu (ana thread'de çağrılacak)"""
    if points_array.size > 0:
        scatter._offsets3d = (points_array[:,0], points_array[:,1], points_array[:,2])
        scatter.set_color(colors_array)
        
    # Grafiği yeniden çiz
    plt.draw()
    plt.pause(0.001)

def main():
    global points_array, colors_array
    
    try:
        client = carla.Client("localhost", 2000)
        client.set_timeout(10.0)
        world = client.get_world()

        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        world.apply_settings(settings)

        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)

        bp_lib = world.get_blueprint_library()
        spawn_points = world.get_map().get_spawn_points()

        vehicle_bp = random.choice(bp_lib.filter("*vehicle"))
        vehicle = world.spawn_actor(vehicle_bp, random.choice(spawn_points))
        vehicle.set_autopilot(True)

        for i in range(5):
            traffic_bp=random.choice(bp_lib.filter("*vehicle"))
            traffic=world.spawn_actor(traffic_bp,random.choice(spawn_points))
            if traffic:
                traffic.set_autopilot(True)

        radar_bp = bp_lib.find("sensor.other.radar")
        radar_bp.set_attribute("horizontal_fov", str(35))
        radar_bp.set_attribute("vertical_fov", str(20))
        radar_bp.set_attribute("range", str(50))
        radar_pos = carla.Transform(carla.Location(x=2.5, z=1.2))
        radar = world.spawn_actor(radar_bp, radar_pos, attach_to=vehicle)

        radar.listen(lambda data: radar_callback(data))

        # Matplotlib interaktif modu başlat
        plt.ion()
        plt.show(block=False)
        
        # Ana görselleştirme döngüsü
        running = True
        last_update = time.time()
        
        while running:
            world.tick()
            
            # Plot'u düzenli olarak güncelle (saniyede ~20 kere)
            current_time = time.time()
            if current_time - last_update > 0.05:  # 20 FPS
                update_plot()
                last_update = current_time
            
            # Pencere kapatıldıysa döngüyü sonlandır
            if not plt.fignum_exists(fig.number):
                running = False
                
            # CPU kullanımını azaltmak için kısa uyku
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"Ana program hatası: {e}")
    finally:
        # Temizlik işlemleri
        try:
            radar.destroy()
        except:
            pass
        try:
            vehicle.destroy()
        except:
            pass
        plt.ioff()
        plt.close()

if __name__ == "__main__":
    main()