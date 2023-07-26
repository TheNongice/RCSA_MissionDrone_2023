from djitellopy import tello
import cv2
from pyzbar.pyzbar import decode
import threading
import time
import keyboard

# QR Code Stage
QR1 = 0
QR2 = 0
QR3 = 0

def cameraActive():
    while True:
        img = drone.get_frame_read().frame
        cv2.imshow("Image", img)
        cv2.waitKey(1)

def qrRead():
    my_data = 'null'
    while True:
        img = drone.get_frame_read().frame
        for barcode in decode(img):
            print(barcode.data)
            my_data = barcode.data.decode('utf-8')
            print(my_data)
            break
        if my_data != 'null':
            break
    return int(my_data)

def mission1():
    global QR1
    drone.takeoff()
    drone.move_up(60)
    drone.move_forward(190)
    rounds = qrRead()
    print(rounds)
    for x in range(rounds):
        drone.rotate_clockwise(360)
    QR1 = rounds
    time.sleep(2)
    drone.move_left(120)
    drone.move_forward(200)
    drone.land()


drone = tello.Tello()
print("Hello world! Please wait...")
drone.connect()
drone.streamon()


battery_info = drone.get_battery()
print(f"Battery info: {battery_info}")

t1 = threading.Thread(target=cameraActive)
t1.start()

while True:
    if(keyboard.read_key()=='q'):
        try:
            ask_input = input('Please enter mode: ')
            if ask_input == 'st':
                mission1()
            if ask_input == 'tf':
                drone.takeoff()
                time.sleep(2)
                drone.rotate_clockwise(360)
                drone.land()

        except KeyboardInterrupt:
            print("Sayonara!")
            break