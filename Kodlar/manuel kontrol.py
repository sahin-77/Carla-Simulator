import glob
import os
import sys
import pygame
import math
import numpy as np

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Carla Manuel Kontrol - W: Gaz, S: Fren, A: Sol, D: Sağ, ESC: Çıkış")


font = pygame.font.SysFont('Arial', 24)

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

def main():
    try:

        client = carla.Client('localhost', 2000)
        client.set_timeout(5.0)
        world = client.get_world()
        

        settings = world.get_settings()
        settings.synchronous_mode = False  
        world.apply_settings(settings)
        
        blueprint_library = world.get_blueprint_library()
        vehicle_bp = blueprint_library.filter('model3')[0]
        

        spawn_points = world.get_map().get_spawn_points()
        spawn_point = spawn_points[0] 
    
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '800')
        camera_bp.set_attribute('image_size_y', '600')
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
        
        def camera_callback(image):
            nonlocal camera_image
            array = np.frombuffer(image.raw_data, dtype=np.uint8)
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]  # BGR to RGB
            camera_image = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        
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
            
            world.wait_for_tick()
            
            screen.fill((0, 0, 0))
            
            if camera_image is not None:
                screen.blit(camera_image, (0, 0))
            

            pygame.display.flip()
            clock.tick(60)
    
    except Exception as e:
        print(f"Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
    finally:

        print("Temizlik yapılıyor...")
        try:
            if 'camera' in locals():
                camera.destroy()
            if 'vehicle' in locals():
                vehicle.destroy()
        except:
            pass
        pygame.quit()

if __name__ == "__main__":
    main()