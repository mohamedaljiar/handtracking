import cv2
from cvzone.HandTrackingModule import HandDetector
import serial

try:
    ser = serial.Serial("/dev/tty.HC-05-SerialPort", 9600)
    ser.flushInput()
    print("Robot Connected!")
except:
    print("Robot not found, running in Debug Mode.")
    ser = None


cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=2)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)

    if hands:
        real_right = None
        real_left = None

        for hand in hands:
            
            
            if hand["type"] == "Right":
                real_left = hand
                
            elif hand["type"] == "Left":
                real_right = hand
                
            

        hand1 = real_right if real_right else real_left
        centerPoint1 = hand1["center"]
        fingers = detector.fingersUp(hand1)

        if fingers == [0, 1, 1, 0, 0]:
            cv2.putText(img, "AUTO MODE (Ultrasonic)", (50, 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
            if ser:
                ser.write(b'A')
#this coommit by ahmed awad awad cv2.destroyAllWindows()
def send_command(command):
    if ser:
        ser.write(command)


def draw_text(img, text):
    cv2.putText(
        img, text, (50, 50),
        cv2.FONT_HERSHEY_PLAIN, 2,
        (0, 0, 255), 4
    )


def handle_two_hands(img, detector, centerPoint1, real_left):
    centerPoint2 = real_left["center"]

    length, info, img = detector.findDistance(centerPoint1, centerPoint2, img)

    mid_x, mid_y = info[4], info[5]
    cv2.circle(img, (mid_x, mid_y), int(length) // 2, (100, 100, 30), 5)

    right_y = info[3]
    left_y = info[1]

    return img, left_y, right_y


def decide_movement(img, left_y, right_y):
    threshold = 30

    if abs(left_y - right_y) <= threshold:
        draw_text(img, "Move Forward")
        send_command(b'F')

    elif left_y > right_y + threshold:
        draw_text(img, "Move Right")
        send_command(b'R')

    elif left_y < right_y - threshold:
        draw_text(img, "Move Left")
        send_command(b'L')
        
while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    real_right = None
    real_left = None

    if hands:
        for hand in hands:
            if hand["type"] == "Right":
                real_right = hand
            elif hand["type"] == "Left":
                real_left = hand

    if len(hands) == 2 and real_right and real_left:
        centerPoint1 = real_right["center"]

        img, left_y, right_y = handle_two_hands(
            img, detector, centerPoint1, real_left
        )

        decide_movement(img, left_y, right_y)

    else:
        draw_text(img, "Stop")
        send_command(b'S')

    cv2.imshow("Hand Control Robot", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
#end of the part and project
