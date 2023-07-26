from djitellopy import tello
import cv2
from pyzbar.pyzbar import decode
import threading
import time
import keyboard

live_cam = True

# QR Code Stage
QR1 = 0

def batter_check():
    batt = drone.get_battery()
    return int(batt)

def cameraActive():
    global live_cam
    while live_cam == True:
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
    drone.move_forward(180)
    rounds = qrRead()
    print(rounds)
    for x in range(rounds):
        drone.rotate_clockwise(360)
    QR1 = rounds
    time.sleep(2)
    drone.move_left(120)
    drone.jump_between_pads(x=360,y=120,z=100,speed=100,yaw=0,mid1=4,mid2=2)
    drone.land()
    batt_stat = batter_check()
    print("==============")
    print("Summary QR1 ="+str(QR1))
    print(f"Now Battery is: {batt_stat}")
    print("==============")

def mission2():
    drone.takeoff()
    drone.move_up(60)
    drone.move_forward(150)
    rounds = qrRead()
    print(rounds)
    if rounds == QR1:
        drone.move_up(20)
        drone.move_forward(120)
        drone.move_right(120)
        time.sleep(2)
        drone.move_forward(60)
        for i in range(QR1):
            drone.move_forward(100) 
            drone.move_left(100)
            drone.move_back(100)
            drone.move_right(100)
    else:
        drone.move_up(20)
        drone.move_right(120) # เช็กรัศมีวงกลมอีกครั้ง
        drone.move_forward(120)
        time.sleep(2)
        drone.move_forward(60)
        for i in range(QR1):
            drone.move_forward(100)
            drone.move_left(100)
            drone.move_back(100)
            drone.move_right(100)
        
    drone.rotate_clockwise(180)
    # drone.move_forward(100)
    drone.jump_between_pads(x=360,y=-360,z=100,speed=100,yaw=0,mid1=2,mid2=3)
    drone.land()
    batt_stat = batter_check()
    print("==============")
    print("The End Mission 2")
    print(f"Now Battery is: {batt_stat}%")
    print("==============")



drone = tello.Tello()
print("Hello Tello! Please wait...")
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
                ask = input('If ready press y and enter')
                if ask == 'y':
                    mission2()    
            if ask_input == 'tf':
                drone.takeoff()
                time.sleep(2)
                drone.rotate_clockwise(360)
                drone.land()
            if ask_input == 'b':
                batt_stat = batter_check()
                print(f"Battery status is: {batt_stat}%")
        except KeyboardInterrupt:
            print("Sayonara!")
            live_cam = False
            drone.streamoff()
            t1.join()
            break