import glob
import os
import sys
import pygame

import math
import numpy as np
import random

# Pygame başlat
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Carla Manuel Kontrol")

# Font ayarları
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
        # Carla istemcisi oluştur ve dünyaya bağlan
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        world = client.get_world()
        
        # Dünya ayarlarını senkron moda al
        settings = world.get_settings()
        settings.synchronous_mode = False  # Manuel kontrol için senkron modu kapat
        settings.fixed_delta_seconds = None
        world.apply_settings(settings)
        
        # Araç blueprint'i seç
        blueprint_library = world.get_blueprint_library()
        vehicle_bp = blueprint_library.filter('vehicle.tesla.model3')[0]  # Tesla Model 3
        
        # Spawn noktası seç
        spawn_points = world.get_map().get_spawn_points()
        spawn_point = random.choice(spawn_points)
        
        # Aracı dünyaya ekle
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        print(f"Araç oluşturuldu: {vehicle.type_id}")
        
        # Kamerayı oluştur
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(screen_width))
        camera_bp.set_attribute('image_size_y', str(screen_height))
        camera_bp.set_attribute('fov', '110')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        print("Kamera oluşturuldu")
        
        # Kontrol parametreleri
        throttle = 0.0
        steer = 0.0
        brake = 0.0
        reverse = False
        hand_brake = False
        max_throttle = 0.8
        max_steer = 0.7
        
        # Kamera görüntüsü için
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
        
        # Ana döngü
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Olayları işle
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Klavye durumunu al
            keys = pygame.key.get_pressed()
            
            # Gaz kontrolü (W)
            throttle = 0.0
            if keys[pygame.K_w]:
                throttle = max_throttle
            
            # Fren kontrolü (S)
            brake = 0.0
            if keys[pygame.K_s]:
                brake = 1.0
            
            # Sol kontrol (A)
            steer = 0.0
            if keys[pygame.K_a]:
                steer = -max_steer
            # Sağ kontrol (D)
            elif keys[pygame.K_d]:
                steer = max_steer
            
            # Geri vites (R)
            reverse = keys[pygame.K_r]
            
            # El freni (SPACE)
            hand_brake = keys[pygame.K_SPACE]
            
            # Kontrolü araca uygula
            control = carla.VehicleControl(
                throttle=throttle,
                steer=steer,
                brake=brake,
                hand_brake=hand_brake,
                reverse=reverse,
                manual_gear_shift=False
            )
            vehicle.apply_control(control)
            
            # Ekranı temizle
            screen.fill((0, 0, 0))
            
            # Kamera görüntüsünü göster
            if camera_image is not None:
                screen.blit(camera_image, (0, 0))
            else:
                # Eğer kamera görüntüsü yoksa bilgi göster
                text = font.render("Kamera görüntüsü bekleniyor...", True, (255, 255, 255))
                screen.blit(text, (screen_width//2 - 150, screen_height//2 - 15))
            
     
            
            # Ekranı güncelle
            pygame.display.flip()
            
            # FPS kontrolü
            clock.tick(30)
    
    except Exception as e:
        print(f"Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Temizlik
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