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
import carla

client=carla.Client("localhost",2000)
client.set_timeout(10.0)
world=client.get_world()
client.reload_world()
print("reset")
# settings = world.get_settings()
# settings.synchronous_mode = True
# settings.fixed_delta_seconds=0.0
# world.apply_settings(settings)