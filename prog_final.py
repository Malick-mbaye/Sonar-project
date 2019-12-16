import can4python as can
import RPi.GPIO as GPIO
import abc
import threading
import logging
import time
from can4python.caninterface_bcm import SocketCanBcmInterface as BCM
from can4python.canframe import CanFrame
from can4python import cansignal
from can4python import canframe_definition
import numpy


distance = [0,0]
levels=[0,0]
i=0

SENSOR_1_ID = 0
SENSOR_2_ID = 1


ParkAssitVolumeState_ID=0
SensorAvailabilityFrontCenter_ID=1
SensorAvailabilityFrontleft_ID=2
SensorAvailabilityFrontRight_ID=3
SensorAvailabilityRearCenter_ID=4
SensorAvailabilityRearLeft_ID=5
SensorAvailabilityRearRight_ID=6
SonarObstacleDistanceDisplay_ID=7
UPA_ClosingAuthorization_ID=8
UPA_Image_DisplayRequest_ID=9
UPA_Obstacle_Zone_Front_Center_ID=10
UPA_Obstacle_zone_front_left_ID=11
UPA_Obstacle_zone_front_Right_ID=12
UPA_Obstacle_zone_Rear_Center_ID=13
UPA_Obstacle_zone_Rear_Left_ID=14
UPA_Obstacle_zone_Rear_Right_ID=15
UPA_SoundActivationBeep_ID=16
UPA_SoundErrorBeep_ID=17
UPA_SoundObstacleZone_ID=18
UPA_SoundReccurencePeriod_ID=19
UPA_SoundReccurenceType_ID=20
UPA_SystemState_ID=21
UPAStatusDisplayRequest_ID=22
triggers=[19,23]
echos=[16,24]
on=1
off=0
periode=40
sensorToSignal=[16,19,18]


class TestCanFrame():
    

    def __init__(self):
        print("Distance for both sensors:",distance) 
        
        self.bus = BCM('can0',timeout=5.0)
        print("Bus created")
        
        #byte position 1 & bit position 4 --> startbit=10 & signal size 3
        self.signals = [cansignal.CanSignalDefinition('ParkAssitVolumeState', 48, 3),
                        cansignal.CanSignalDefinition('SensorAvailabilityFrontCenter', 34, 1),
                        cansignal.CanSignalDefinition('SensorAvailabilityFrontleft', 33, 1),
                        cansignal.CanSignalDefinition('SensorAvailabilityFrontRight', 41, 1),
                        cansignal.CanSignalDefinition('SensorAvailabilityRearCenter', 55, 1),
                        cansignal.CanSignalDefinition('SensorAvailabilityRearLeft', 54, 1),
                        cansignal.CanSignalDefinition('SensorAvailabilityRearRight', 53, 1),
                        cansignal.CanSignalDefinition('SonarObstacleDistanceDisplay', 44, 4),
                        cansignal.CanSignalDefinition('UPA_ClosingAuthorization', 58, 1),
                        cansignal.CanSignalDefinition('UPA_Image_DisplayRequest', 17, 2),
                        cansignal.CanSignalDefinition('UPA_Obstacle_Zone_Front_Center', 31, 3),
                        cansignal.CanSignalDefinition('UPA_Obstacle_zone_front_left', 15, 3),
                        cansignal.CanSignalDefinition('UPA_Obstacle_zone_front_Right', 12, 3),
                        cansignal.CanSignalDefinition('UPA_Obstacle_zone_Rear_Center', 29, 3),
                        cansignal.CanSignalDefinition('UPA_Obstacle_zone_Rear_Left', 23, 3),
                        cansignal.CanSignalDefinition('UPA_Obstacle_zone_Rear_Right', 20, 3),
                        cansignal.CanSignalDefinition('UPA_SoundActivationBeep ', 24, 1),
                        cansignal.CanSignalDefinition('UPA_SoundErrorBeep', 25, 1),
                        cansignal.CanSignalDefinition('UPA_SoundObstacleZone', 34, 3),
                        cansignal.CanSignalDefinition('UPA_SoundReccurencePeriod',1, 7),
                        cansignal.CanSignalDefinition('UPA_SoundReccurenceType', 0, 1),
                        cansignal.CanSignalDefinition('UPA_SystemState', 9, 2),
                        cansignal.CanSignalDefinition('UPAStatusDisplayRequest', 39, 3)]
                    
        #byte position 1 & bit position 7 --> startbit=13 & signal size 3
        #self.signals[1] = cansignal.CanSignalDefinition('UPA_Obstacle_zone_front_left', 13, 3)
        #ajout des signaux sur la trame global 
        self.frame_def=canframe_definition.CanFrameDefinition(1,'sonarA4')
        self.frame_def.signaldefinitions.append(self.signals[0])
        self.frame_def.signaldefinitions.append(self.signals[1])
        self.frame_def.signaldefinitions.append(self.signals[2])
        self.frame_def.signaldefinitions.append(self.signals[3])
        self.frame_def.signaldefinitions.append(self.signals[4])
        self.frame_def.signaldefinitions.append(self.signals[5])
        self.frame_def.signaldefinitions.append(self.signals[6])
        self.frame_def.signaldefinitions.append(self.signals[7])
        self.frame_def.signaldefinitions.append(self.signals[2])
        self.frame_def.signaldefinitions.append(self.signals[9])
        self.frame_def.signaldefinitions.append(self.signals[10])
        self.frame_def.signaldefinitions.append(self.signals[11])
        self.frame_def.signaldefinitions.append(self.signals[12])
        self.frame_def.signaldefinitions.append(self.signals[13])
        self.frame_def.signaldefinitions.append(self.signals[14])
        self.frame_def.signaldefinitions.append(self.signals[15])
        self.frame_def.signaldefinitions.append(self.signals[16])
        self.frame_def.signaldefinitions.append(self.signals[17])
        self.frame_def.signaldefinitions.append(self.signals[18])
        self.frame_def.signaldefinitions.append(self.signals[19])
        self.frame_def.signaldefinitions.append(self.signals[20])
        

        self.frame = CanFrame(0x53D,frame_data=[0, 0, 0, 0, 0, 0, 0, 0],frame_format='standard')
        print("Frame created")
        
        self.th1 = threading.Thread(target=self.sensor_reader,args=(triggers[SENSOR_2_ID], echos[SENSOR_2_ID],SENSOR_2_ID))
        #self.th2 = threading.Thread(target=self.sensor_reader,args=(triggers[SENSOR_2_ID], echos[SENSOR_2_ID],SENSOR_2_ID))
        
    def sensor_reader(self,trigger_id, echo_id, sensor_id):
        Periode_calculer=127
        while(1):
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(trigger_id,GPIO.OUT)
            GPIO.setup(echo_id,GPIO.IN)
            GPIO.output(trigger_id,False)
            print("waiting a few seconds for the sensor to sttle")
            time.sleep(2)
            GPIO.output(trigger_id,True)
            time.sleep(0.00001)
            GPIO.output(trigger_id,False)
            while GPIO.input(echo_id)==0:
                pulse_start=time.time()
            while GPIO.input(echo_id)==1:
                 pulse_end=time.time()
            pulse_duration=pulse_end-pulse_start
            distance_temp=pulse_duration*17150
            distance[sensor_id]=round(distance_temp)
            print("Distance sensor numero ", sensor_id, " :",distance[sensor_id],"cm")
            if distance[sensor_id] < 30  :
                print("level1");
                levels[sensor_id] = 1;
                print("periode_calculer=126")
                periode_calculer=126
            elif 30<distance[sensor_id] <50 :
                print("level2");
                levels[sensor_id] = 2;
                print("periode_calculer=94")
                periode_calculer=94
            elif 50<distance[sensor_id] <70 :
                print("level3");
                levels[sensor_id] = 3;
                print("periode_calculer=30")
                periode_calculer=30
            else :
                distance[sensor_id] >70 
                print("level4");
                levels[sensor_id] = 4;
                print("periode_calculer=0")
                periode_calculer=0

                
#             if periode_calculer<periode :
#                 periode=periode_calculer
                
            
            #frame.set_signalvalue(signals[sensor_id], level[sensor_id])
            
            #bus.setup_periodic_send(frame, interval=100, restart_timer=False)
            print("set_signalvalue")
#             self.frame.set_signalvalue(self.signals[sensorToSignal[sensor_id]],levels[sensor_id])
            self.frame.set_signalvalue(self.signals[UPA_SoundReccurencePeriod_ID],periode)
#             self.frame.set_signalvalue(self.signals[UPA_SoundActivationBeep_ID],off)
#             self.frame.set_signalvalue(self.signals[UPA_SoundObstacleZone_ID],3)
            #print("get_signalvalue ", self.frame.get_signalvalue(self.signals[sensor_id]))
            self.bus.setup_periodic_send(self.frame, interval=100, restart_timer=False)
            
            
            
    def run(self):

        #self.frame -->trame global envoyé
        self.bus.setup_periodic_send(self.frame, interval=100, restart_timer=True)

        self.th1.start()
        #self.th2.start()
        print("Update!")
        self.th1.join()
        #self.th2.join()

if __name__ == '__main__':
    
    t = TestCanFrame()
    t.run()
 










    

