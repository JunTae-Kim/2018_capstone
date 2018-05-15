import RPi.GPIO as GPIO
import time

#pin_encZ = 24
pin_encA = 23
pin_encB = 24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pin_encA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_encB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(pin_encZ, GPIO.IN, pull_up_down=GPIO.PUD_UP)

encoderPos = 0
#encoderPosZ = 0

def encoderA(channel):
    global encoderPos
    if GPIO.input(pin_encA) == GPIO.input(pin_encB):
        encoderPos += 1
    else:
        encoderPos -= 1
    #print('PinA : %d, encoder : %f' %(channel, float(encoderPos)/float(200)))
    
def encoderB(channel):
    global encoderPos
    if GPIO.input(pin_encB) == GPIO.input(pin_encA):
        encoderPos -= 1
    else:
        encoderPos += 1
    #print('PinB : %d, encoder : %lf' %(channel, encoderPos/198))

#def encoderZ(channel):
#    global encoderPos
#    if GPIO.input(pin_encZ) == GPIO.input(pin_encA):
#        encoderPos += 1
#    print('PinA : %d, encoder : %lf' %(channel, encoderPos))

GPIO.add_event_detect(pin_encA, GPIO.BOTH, callback=encoderA)
GPIO.add_event_detect(pin_encB, GPIO.BOTH, callback=encoderB)
#GPIO.add_event_detect(pin_encA, GPIO.RISING, callback=encoderZ)

while True:
    
    start_time = time.time()
    start_pos = encoderPos
    print('start_time = %d, start_pos = %d' %(start_time, start_pos))
    time.sleep(1)
    
    end_time = time.time()
    end_pos = encoderPos
    print('end_time = %d, end_pos = %d' %(end_time, end_pos))
    
    speed = (end_pos-start_pos)/(end_time-start_time)
    print('speed = %d' %(speed))
    

          