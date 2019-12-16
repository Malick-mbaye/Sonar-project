import RPi.GPIO as GPIO
import time
import can

GPIO.setmode(GPIO.BCM)

TRIG=23
ECHO=24
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, False)

while(1):
    
    time.sleep(0.1
               )
    GPIO.output(TRIG, True)

    time.sleep(0.00001)

    GPIO.output(TRIG, False) 

    while GPIO.input(ECHO) == 0:

        pulse_start = time.time()

    while GPIO.input(ECHO)==1:

        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    print ("Distance:",distance,"cm")
    
    if(distance<=20):
        print ("level1")
        bus=can.interface.Bus(channel='slcan0', bustype='socketcan_native')
        msg=can.Message(arbitration_id=0x53D,
                data=[254, 0, 0, 0, 12, 10, 0, 0],
                extended_id=False)
        bus.send(msg)
    elif (distance>20 and distance<=30):
        print ("level2")
        bus=can.interface.Bus(channel='slcan0', bustype='socketcan_native')
        msg=can.Message(arbitration_id=0x53D,
                data=[190, 0, 0, 0, 12, 10, 0, 0],
                extended_id=False)
        bus.send(msg)
    elif (distance>30 and distance<=40):
        print ("level3")
        bus=can.interface.Bus(channel='slcan0', bustype='socketcan_native')
        msg=can.Message(arbitration_id=0x53D,
                data=[62, 0, 0, 0, 12, 10, 0, 0],
                extended_id=False)
        
        bus.send(msg)
    else:
        print ("level4")
        bus=can.interface.Bus(channel='slcan0', bustype='socketcan_native')
        msg=can.Message(arbitration_id=0x53D,
                data=[0, 0, 0, 0, 12, 10, 0, 0],
                extended_id=False)
        bus.send(msg)
        
        
        
        
        
        
GPIO.cleanup()