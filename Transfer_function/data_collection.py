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
target_Speed = 0
real_Speed = 0
dutyrate = 0
count = 0
total = 0
circle_length = 3.141592*0.095

servo.ChangeDutyCycle(standard) 
dc.ChangeDutyCycle(0)

data = []
data_set = open("Data.txt",'w')

num = 20
max_Speed = 16
tolerance_Speed = 0.05
unit_Duty = 0.05
unit_Speed = 0.5
per_minmax = 0.1

limit = int(num*per_minmax)

while t!=1:
    
    try :
        
        while count < num :
            
            if real_Speed > target_Speed + tolerance_Speed :
                dutyrate = float(dutyrate - unit_Duty)
            elif real_Speed < target_Speed - tolerance_Speed :
                dutyrate = float(dutyrate + unit_Duty )
            else :
                print('Speed : %f km/h, Target Speed : %f km/h, DutyRate : %f' %(real_Speed, target_Speed, dutyrate))
                #total = total + dutyrate
                data.append(dutyrate)
                count = count + 1
                
            if dutyrate >= 99 or target_Speed > max_Speed :
                dc.ChangeDutyCycle(0)
                time.sleep(1)
                data_set.close()
                t=1
                break
                
            dc.ChangeDutyCycle(dutyrate)
                
            start_time = time.time()
            start_pos = encoderPos
                
            time.sleep(0.1)
                
            end_time = time.time()
            end_pos = encoderPos
                
            pulse_per_sec = float((end_pos-start_pos)/(end_time-start_time))
            encoder_per_sec = pulse_per_sec/ float(11)
            motor_per_sec = encoder_per_sec / float(4.04)
            car_per_sec = motor_per_sec / float(4.5)
            wheel_per_sec = car_per_sec / float(2.5)
            real_Speed = wheel_per_sec * 60 * circle_length * 60 * 0.001
            
        print('List : ' ,data)   
        data.sort()
        print('List_sort : ' ,data)
        
        for i in range (1, limit):
            min_ = min(data)
            data.remove(min_)
            max_ = max(data)
            data.remove(max_)
            
        print('List_limit : ' ,data)
        mean = sum(data)/len(data)

        print('Target Speed : %f km/h, DutyRate : %f' %(target_Speed, mean))
        char_Speed = str(target_Speed) + "\n"
        char_mean = str(mean) + "\n"
        data_set.write(char_Speed)
        data_set.write(char_mean)
        target_Speed = target_Speed + unit_Speed
        count = 0
        mean = 0
        data = []
                
    except KeyboardInterrupt:
        
        key = getkey()
        
        if key == "c":
            t=1
    #    if key == "b":
    #        t=1
        elif key == "w":
            target_Speed = target_Speed + 0.5
        elif key == "s":
            target_Speed = target_Speed - 0.5
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
