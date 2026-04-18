from djitellopy import Tello
import time

# Connect to the drone
tello = Tello()
tello.connect()

battery = tello.get_battery()
print(battery)