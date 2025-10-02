import glob
import os
import sys
import time
import random

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

client=carla.Client("localhost",2000)
client.set_timeout(10.0)
world=client.get_world()

settings=world.get_settings()
settings.synchronous_mode=True
settings.fixed_delta_seconds=0.05
world.apply_settings(settings)

traffic_manager = client.get_trafficmanager(8000)
traffic_manager.set_synchronous_mode(True)

spawn_points=world.get_map().get_spawn_points()

for i in range(50):
    traffic_bp = random.choice(world.get_blueprint_library().filter('*vehicle*'))
    traffic_vehicle = world.try_spawn_actor(traffic_bp, random.choice(spawn_points))
    if traffic_vehicle:
        traffic_vehicle.set_autopilot(True)

try:
    while True:
        world.tick()
finally:
    pass