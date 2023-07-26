from djitellopy import tello
import cv2
from pyzbar.pyzbar import decode
import threading
import time
import keyboard

###################### Setup ######################

live_cam = True

# Constants for everythings
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

###################### Mission ######################

def mission1():
    global QR1
    FORWARD_DIS = 180
    FORWARD_LEFT = 120

    # Set height to 120 cm for scan QR Code
    drone.takeoff()
    drone.move_up(60)

    # Go in front of QR code
    drone.move_forward(FORWARD_DIS-45)

    # Scan, Get value and Rotate
    rounds = qrRead()
    print(rounds)
    for x in range(rounds):
        drone.rotate_clockwise(360)
    QR1 = rounds
    time.sleep(2)

    # Take position for circle hoop
    drone.move_left(FORWARD_LEFT+110)

    # Becaureful coordinate Z because sometimes it's too low
    drone.jump_between_pads(x=480,y=210,z=100,speed=100,yaw=0,mid1=4,mid2=2)
    drone.land()

    batt_stat = batter_check()
    print("==============")
    print("Summary QR1 ="+str(QR1))
    print(f"Now Battery is: {batt_stat}")
    print("==============")

def mission2(QR1):
    FORWARD_DIS1 = 180
    
    # Set height to 60 cm for Scan QR Code
    drone.takeoff()
    
    # Go in front of QR Code (Left check first)
    drone.move_forward(FORWARD_DIS1)
    drone.move_left(120)

    # Scan QR Code and choose lane
    rounds = qrRead()
    print(rounds)
    if rounds == QR1:
        # Set 120 cm height to center of circle hoop
        drone.move_up(60)
        drone.move_forward(180)
        drone.move_right(180)

        # Fly around flag
        for i in range(QR1):
            drone.move_forward(130) 
            drone.move_left(130)
            drone.move_back(130)
            drone.move_right(130)
    else:
        # Set 120 cm height to center of circle hoop
        drone.move_up(60)
        drone.move_right(240) 
        drone.move_forward(180)
        drone.move_left(75)
        
        # Fly around flag
        for i in range(QR1):
            drone.move_forward(130)
            drone.move_left(130)
            drone.move_back(130)
            drone.move_right(130)

    # Landing    
    drone.rotate_clockwise(180)
    drone.jump_between_pads(x=420,y=-430,z=100,speed=100,yaw=0,mid1=2,mid2=3)
    drone.land()

    batt_stat = batter_check()
    print("==============")
    print("The End Mission 2")
    print(f"Now Battery is: {batt_stat}%")
    print("==============")

### Check lower QR Code First ###
def mission3(QR1):
    # height 60 cm
    drone.takeoff()

    ##### Left lower
    # drone.move_left(60)
    ##### Right lower
    drone.move_right(60)

    drone.move_forward(110)
    
    # Scan QR Code
    rounds = qrRead()
    if rounds == QR1:
        # height 120 cm
        drone.move_up(60)
        drone.move_forward(130)
        
        # height 175 cm
        drone.move_up(55)
        drone.move_forward(240)
        
        # right lower == move_left, left lower == move_right
        drone.move_left(60)
        
        # height 120 cm
        drone.move_down(55)
        drone.move_forward(390)
        
        # landing
        drone.rotate_clockwise(180)
        drone.jump_between_pads(x=860,y=-240,z=100,speed=100,yaw=0,mid1=3,mid2=4)
        drone.land()
    else:
        # right lower == left, left lower == right To change lane
        drone.move_left(100)

        # height 175 cm
        drone.move_up(115)
        drone.move_forward(130)

        # height 110 cm
        drone.move_down(65)
        drone.move_forward(240)

        # right lower == right, left lower == left
        drone.move_right(60)
        drone.move_forward(390)

        # landing
        drone.rotate_clockwise(180)
        drone.jump_between_pads(x=860,y=-240,z=100,speed=100,yaw=0,mid1=3,mid2=4)
        drone.land()
    batt_stat = batter_check()
    print("==============")
    print("The End Mission 2")
    print(f"Now Battery is: {batt_stat}%")
    print("==============")
        

#################################################################################################################

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

            # Mission
            if ask_input == '1':
                mission1()
            if ask_input == '2':
                if QR1 == 0:
                    QR1 = int(input("Amount of QR Code: "))
                mission2(QR1)
            if ask_input == '3':
                if QR1 == 0:
                    QR1 = int(input("Amount of QR Code: "))
                mission3(QR1)

            # Check
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