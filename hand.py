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

        elif len(hands) == 2 and real_right and real_left:
            hand2 = real_left
            centerPoint2 = hand2["center"]
            length, info, img = detector.findDistance(centerPoint1, centerPoint2, img)

            cv2.circle(img, (info[4], info[5]), int(length) // 2, (100, 100, 30), 5)

            righty = info[3]
            lefty  = info[1]

            if lefty - 30 <= righty <= lefty + 30:
                cv2.putText(img, "Move Forward", (50, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)
                if ser:
                    ser.write(b'F')

            elif lefty >= righty + 31:
                cv2.putText(img, "Move Right", (50, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)
                if ser:
                    ser.write(b'R')

            elif lefty <= righty - 31:
                cv2.putText(img, "Move Left", (50, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)
                if ser:
                    ser.write(b'L')

        else:
            cv2.putText(img, "Stop", (50, 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)
            if ser:
                ser.write(b'S')

    else:
        cv2.putText(img, "Stop", (50, 50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)
        if ser:
            ser.write(b'S')

    cv2.imshow("Hand Control Robot", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()