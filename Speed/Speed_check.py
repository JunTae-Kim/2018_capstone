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

def encoderA(channel):
    global encoderPos
    if GPIO.input(pin_encA) == GPIO.input(pin_encB):
        encoderPos -= 1
    else:
        encoderPos += 1
#    print('PinA : %d, encoder : %lf\n\r' %(channel, encoderPos))
    
def encoderB(channel):
    global encoderPos
    if GPIO.input(pin_encB) == GPIO.input(pin_encA):
        encoderPos += 1
    else:
        encoderPos -= 1
#    print('PinB : %d, encoder : %lf\n\r' %(channel, encoderPos))

pin_servo = 18
pin_dc = 12
pin_dir = 26
pin_encA = 23
pin_encB = 24
freq = 50

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_servo,GPIO.OUT)
GPIO.setup(pin_dc,GPIO.OUT)
GPIO.setup(pin_dir,GPIO.OUT)
GPIO.setup(pin_encA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_encB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(pin_encA, GPIO.BOTH, callback=encoderA)
GPIO.add_event_detect(pin_encB, GPIO.BOTH, callback=encoderB)

servo = GPIO.PWM(pin_servo,freq)
servo.start(0)
dc = GPIO.PWM(pin_dc,freq)
dc.start(0)

GPIO.output(pin_dir, True)

a = 0
t = 0
k = 0
speed = 0
standard = 6.65
angle = standard
encoderPos = 0
duty_rate = 0
circle_length = 3.141592*0.095
Mean_speed = 0

servo.ChangeDutyCycle(standard) 
dc.ChangeDutyCycle(0)

while t!=1:
    
    try :
        if k == 1 :
            servo.ChangeDutyCycle(angle)
            time.sleep(0.2)
            k = 0
        
        servo.ChangeDutyCycle(0)
        dc.ChangeDutyCycle(duty_rate)
        
        for i in range(1,6):
            
            start_time = time.time()
            start_pos = encoderPos
            #print('start_time = %d, start_pos = %d' %(start_time, start_pos))
            
            time.sleep(0.1)
            
            end_time = time.time()
            end_pos = encoderPos
            #print('end_time = %d, end_pos = %d' %(end_time, end_pos))
            
            pulse_per_sec = float((end_pos-start_pos)/(end_time-start_time))
            encoder_per_sec = pulse_per_sec/ float(11)
            motor_per_sec = encoder_per_sec / float(4.04)
            car_per_sec = motor_per_sec / float(4.5)
            wheel_per_sec = car_per_sec / float(2.5)
            real_speed = wheel_per_sec * 60 * circle_length * 60 * 0.001
            
            Mean_speed = Mean_speed + real_speed
            
            if i == 5 :
                Mean_speed = Mean_speed/5
                print('RPM : Motor = %d, Car = %d, Wheel = %d' %(motor_per_sec*60, car_per_sec*60, wheel_per_sec*60))
                print('Speed : %0.2f km/h, DutyRate : %0.2f' %(Mean_speed, duty_rate))
                Mean_speed = 0
                
       # print('RPM : Motor = %f, Car = %f, Wheel = %f' %(motor_per_sec*60, car_per_sec*60, wheel_per_sec*60))
       # print('Speed : %f km/h, DutyRate : %d' %(real_speed, duty_rate))
        
       # time.sleep(1)
        
    except KeyboardInterrupt:
        
        key = getkey()
        
        if key == "c":
            t=1
    #    if key == "b":
    #        t=1
        elif key == "w":
            duty_rate = duty_rate + 5
        elif key == "s":
            duty_rate = duty_rate - 5
        elif key == "e":
            duty_rate = 0
        elif key == "a": #Left
            angle = angle + 0.1
            k = 1
        elif key == "d": #Right
            angle = angle - 0.1
            k = 1
        elif key == "q":
            angle = standard
            k = 1
                
        if duty_rate < 0 :
            duty_rate = 0
        