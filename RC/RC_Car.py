import RPi.GPIO as GPIO
import time
import sys
import tty
import termios

def getkey():
    fd =sys.stdin.fileno()
    original_attributes = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd,termios.TCSADRAIN, original_attributes)
    return ch

pin_servo = 18
pin_dc = 12
pin_dir = 26
freq = 50

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_servo,GPIO.OUT)
GPIO.setup(pin_dc,GPIO.OUT)
GPIO.setup(pin_dir,GPIO.OUT)

servo = GPIO.PWM(pin_servo,freq)
servo.start(0)
dc = GPIO.PWM(pin_dc,freq)
dc.start(0)

GPIO.output(pin_dir,False)

t = 0
speed = 0
standard = 6.65
angle = standard

while t!=1:
    
    key = getkey()
    
    if key == "c":
        t=1
#    if key == "b":
#        t=1
    elif key == "w":
        speed = speed + 5
    elif key == "s":
        speed = speed - 5
    elif key == "e":
        speed = 0
    elif key == "a": #Left
        angle = angle + 0.1
        k = 1
    elif key == "d": #Right
        angle = angle - 0.1
        k = 1
    elif key == "q":
        angle = standard
        k = 1
        
    if speed < 0 :
        speed = 0
    if k == 1 :
        servo.ChangeDutyCycle(angle)
        time.sleep(0.4)
        k = 0
    dc.ChangeDutyCycle(speed)
    
    servo.ChangeDutyCycle(0)
    print("Speed",speed)
    print("Angle",angle)
    
#    servo.ChangeDutyCycle(0)

