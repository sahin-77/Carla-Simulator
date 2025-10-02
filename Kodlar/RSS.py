import glob
import os
import sys
import pygame
import time
import math
import numpy as np
import random


pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Carla Manuel Kontrol - RSS Sensörü")

font = pygame.font.SysFont('Arial', 24)

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

def draw_rss_lines(world, vehicle):

    safe_threshold = 10.0  
    warning_threshold = 5.0  
    ray_length = 20.0  
    lateral_offset = 2.0  

    transform = vehicle.get_transform()
    location = transform.location
    forward = transform.get_forward_vector()
    right = transform.get_right_vector()

    start_center = location + carla.Location(z=1.0)
    end_center = start_center + forward * ray_length
    
    start_left = start_center - right * lateral_offset
    start_right = start_center + right * lateral_offset

    center_hit = world.raycast(start_center, end_center)
    left_hit = world.raycast(start_left, start_left + forward * ray_length)
    right_hit = world.raycast(start_right, start_right + forward * ray_length)

    def get_color(hit):
        if not hit:
            return carla.Color(0, 255, 0) 
        distance = hit.distance
        if distance > safe_threshold:
            return carla.Color(0, 255, 0)  
        elif distance > warning_threshold:
            return carla.Color(255, 255, 0)
        else:
            return carla.Color(255, 0, 0)  

    world.debug.draw_line(
        start_center, 
        center_hit.location if center_hit else end_center,
        thickness=0.1, 
        color=get_color(center_hit),
        life_time=0.1
    )
    world.debug.draw_line(
        start_left, 
        left_hit.location if left_hit else start_left + forward * ray_length,
        thickness=0.1, 
        color=get_color(left_hit),
        life_time=0.1
    )
    world.debug.draw_line(
        start_right, 
        right_hit.location if right_hit else start_right + forward * ray_length,
        thickness=0.1, 
        color=get_color(right_hit),
        life_time=0.1
    )

def main():
    try:

        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        world = client.get_world()
        
        settings = world.get_settings()
        settings.synchronous_mode = False 
        settings.fixed_delta_seconds = None
        world.apply_settings(settings)
        
        blueprint_library = world.get_blueprint_library()
        vehicle_bp = blueprint_library.filter('vehicle.tesla.model3')[0]  

        spawn_points = world.get_map().get_spawn_points()
        spawn_point = random.choice(spawn_points)

        vehicle = world.spawn_actor(vehicle_bp, spawn_point)

        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(screen_width))
        camera_bp.set_attribute('image_size_y', str(screen_height))
        camera_bp.set_attribute('fov', '110')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

        
        throttle = 0.0
        steer = 0.0
        brake = 0.0
        reverse = False
        hand_brake = False
        max_throttle = 0.8
        max_steer = 0.7
        
        camera_image = None
        last_image_time = time.time()
        
        def camera_callback(image):
            nonlocal camera_image, last_image_time
            array = np.frombuffer(image.raw_data, dtype=np.uint8)
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]  # RGBA'dan RGB'ye
            array = array[:, :, ::-1]  # BGR to RGB
            camera_image = pygame.surfarray.make_surface(array.swapaxes(0, 1))
            last_image_time = time.time()
        
        camera.listen(camera_callback)
        
        clock = pygame.time.Clock()
        running = True
        
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            keys = pygame.key.get_pressed()
            
            throttle = 0.0
            if keys[pygame.K_w]:
                throttle = max_throttle
            
            brake = 0.0
            if keys[pygame.K_s]:
                brake = 1.0
            
            steer = 0.0
            if keys[pygame.K_a]:
                steer = -max_steer

            elif keys[pygame.K_d]:
                steer = max_steer
            
            reverse = keys[pygame.K_r]
            
            hand_brake = keys[pygame.K_SPACE]
            
            control = carla.VehicleControl(
                throttle=throttle,
                steer=steer,
                brake=brake,
                hand_brake=hand_brake,
                reverse=reverse,
                manual_gear_shift=False
            )
            vehicle.apply_control(control)
            
            draw_rss_lines(world, vehicle)

            screen.fill((0, 0, 0))
            
            if camera_image is not None:
                screen.blit(camera_image, (0, 0))
            else:

                text = font.render("Kamera görüntüsü bekleniyor...", True, (255, 255, 255))
                screen.blit(text, (screen_width//2 - 150, screen_height//2 - 15))
            
            pygame.display.flip()
            
            clock.tick(30)
    
    except Exception as e:
        print(f"Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Temizlik yapılıyor...")
        try:
            if 'camera' in locals() and camera.is_alive:
                camera.destroy()
            if 'vehicle' in locals() and vehicle.is_alive:
                vehicle.destroy()
        except Exception as e:
            print(f"Temizlik hatası: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()