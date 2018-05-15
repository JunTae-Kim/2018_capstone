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
#    print('PinA : %d, encoder : %lf\n\r' %(channel, encoderPos))
    
def encoderB(channel):
    global encoderPos
    if GPIO.input(pin_encB) == GPIO.input(pin_encA):
        encoderPos += 1
    else:
        encoderPos -= 1
#    print('PinB : %d, encoder : %lf\n\r' %(channel, encoderPos))

def speed2dutyrate(speed):
    
    i = int(math.floor(speed));
    dutyrate = ((output[i+1]-output[i])/(input[i+1]-input[i]))*(speed-input[i]) + output[i]
    return dutyrate        

#data_set = open("Data.txt",'r')
#input = []
#output = []

#num = 

#for i in range(1, num*2 - 1):
#    line = data_set.readline()
#    if i%2 == 1:
#        input.append(line)
#    else :
#        output.append(line)

#print(input)
#print(output)

input = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
output = [0,2.11,2.6,3.11,3.65,4.21,4.75,5.45,6.37,7.4,8.7,10.3,12.4,16.5,22.1,34.5,100]

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
encoderPos = 0
target_Speed = 0
real_Speed = 0
dutyrate = 0
circle_length = 3.141592*0.095
err = 0
prev_err = 0
prev_time = 0
Driving_Time = 0

Kp = 0.5
Ki = 0.5
Kd = 0

servo.ChangeDutyCycle(standard)
servo.ChangeDutyCycle(0)
dc.ChangeDutyCycle(0)

while t!=1:
    
    try :
        if k == 1 :
            servo.ChangeDutyCycle(angle)
            time.sleep(0.2)
            servo.ChangeDutyCycle(0)
            k = 0
            
        start_time = time.time()
        start_pos = encoderPos
            
        time.sleep(0.2)
            
        end_time = time.time()
        end_pos = encoderPos
            
        pulse_per_sec = float((end_pos-start_pos)/(end_time-start_time))
        encoder_per_sec = pulse_per_sec/ float(11)
        motor_per_sec = encoder_per_sec / float(4.04)
        car_per_sec = motor_per_sec / float(4.5)
        wheel_per_sec = car_per_sec / float(2.5)
        real_Speed = wheel_per_sec * 60 * circle_length * 60 * 0.001
        
        err = target_Speed - real_Speed
        de = err - prev_err
        dt = time.time() - prev_time
        
        PID_Speed = target_Speed + Kp*err + Ki*err*dt + Kd*de/dt 
        
        if PID_Speed < 0 :
            GPIO.output(pin_dir, False)
        else :
            GPIO.output(pin_dir, True)
            
        PID_Speed = abs(PID_Speed)
        
        dutyrate = speed2dutyrate(PID_Speed)
        
        if dutyrate < 0 :
            dutyrate = 0
        
        prev_err = err
        prev_time = time.time()
        
        dc.ChangeDutyCycle(dutyrate)
        
        Driving_Time = Driving_Time + (prev_time - start_time)
                    
        #print('RPM : Motor = %f, Car = %f, Wheel = %f' %(motor_per_sec*60, car_per_sec*60, wheel_per_sec*60))
        print('Speed : %0.2f km/h, Target Speed : %0.2f km/h, PID Speed : %0.3f km/h' %(real_Speed, target_Speed, PID_Speed))
        print('DutyRate : %0.2f, Time : %0.2f sec' %(dutyrate, Driving_Time))
        
    except KeyboardInterrupt:
        
        key = getkey()
        
        if key == "c":
            t=1
        elif key == "w":
            target_Speed = target_Speed + 1
        elif key == "s":
            target_Speed = target_Speed - 1
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
