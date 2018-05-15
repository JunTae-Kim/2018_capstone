import RPi.GPIO as GPIO
import time
import sys
import tty
import termios
import math

def getkey():
    fd =sys.stdin.fileno()
    original_attributes = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd,termios.TCSADRAIN, original_attributes)
    return ch\

def encoderA(channel):
    global encoderPos
    if GPIO.input(pin_encA) == GPIO.input(pin_encB):
        encoderPos -= 1
    else:
        encoderPos += 1
    
def encoderB(channel):
    global encoderPos
    if GPIO.input(pin_encB) == GPIO.input(pin_encA):
        encoderPos += 1
    else:
        encoderPos -= 1

def speed2dutyrate(speed):
    aaa = []
    for j in range(0, num): 
        bbb = float(speed-data_speed[j])
        if bbb <= 0:
            aaa.append(bbb)
        else:
            aaa.append(int(-10))
    max_ = max(aaa)
    print(aaa)
    print(max_)
    i = int(aaa.index(max_))
    print(i)
    dutyrate = ((data_duty[i+1]-data_duty[i])/(data_speed[i+1]-data_speed[i]))*(speed-data_speed[i]) + data_duty[i]
    return dutyrate        

data_set = open("Data.txt",'r')
data_speed = []
data_duty = []

num = 17

for i in range(1, num*2 + 1):
    line = data_set.readline()
    if i%2 == 1:
        data_speed.append(float(line))
    else :
        data_duty.append(float(line))

print(data_speed)
print(data_duty)

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
target_Speed = 0
real_Speed = 0
dutyrate = 0
circle_length = 3.141592*0.095
err = 0
err_prev = 0
time_prev = 0

Kp = 0.75
Ki = 0.5
Kd = 0

servo.ChangeDutyCycle(standard) 
dc.ChangeDutyCycle(0)

while t!=1:
    
    try :
        if k == 1 :
            servo.ChangeDutyCycle(angle)
            time.sleep(0.2)
            k = 0
            
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
        real_Speed = wheel_per_sec * 60 * circle_length * 60 * 0.001
        
        err = target_Speed - real_Speed
        de = err - err_prev
        dt = time.time() - time_prev
        
        PID_Speed = target_Speed + Kp*err + Ki*err*dt + Kd*de/dt 
        
        dutyrate = speed2dutyrate(target_Speed)
        
        if dutyrate < 0 :
            dutyrate = 0
        
        err_prev = err
        time_prev = time.time()
        
        servo.ChangeDutyCycle(0)
        dc.ChangeDutyCycle(dutyrate);
                    
        #print('RPM : Motor = %f, Car = %f, Wheel = %f' %(motor_per_sec*60, car_per_sec*60, wheel_per_sec*60))
        print('Speed : %f km/h, Target Speed : %f km/h, PID Speed : %f km/h, DutyRate : %f' %(real_Speed, target_Speed, PID_Speed, dutyrate))
        
       # time.sleep(1)
        
    except KeyboardInterrupt:
        
        key = getkey()
        
        if key == "c":
            t=1
    #    if key == "b":
    #        t=1
        elif key == "w":
            target_Speed = target_Speed + 0.3
        elif key == "s":
            target_Speed = target_Speed - 0.3
        elif key == "e":
            target_Speed = 0
        elif key == "a": #Left
            angle = angle + 0.1
            k = 1
        elif key == "d": #Right
            angle = angle - 0.1
            k = 1
        elif key == "q":
            angle = standard
            k = 1
