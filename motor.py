from simple_pid import PID
import time
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import serial,json
from paho.mqtt import client as mqtt_client
import random
class Motor():
    def __init__(self,
                 PINS={"F":11,"B":13},P=3.25,I=0.73,D=0.3):#PINS={"F":11,"B":13},PID=PID(3.25,0.73,0.30,setpoint=0)):
        GPIO.setmode(GPIO.BOARD)
        self.power = 0
        self.speed = 0
        self.target_speed = 0
        self.spin_count = 0
        self.PID=PID(P,I,D,setpoint=self.speed)
        self.PID.output_limits = (-100, 100)
        self.pins=PINS

        GPIO.setup(self.pins["F"],GPIO.OUT)
        GPIO.setup(self.pins["B"],GPIO.OUT)
        
        self.pwm={}
        self.pwm["F"]=GPIO.PWM(PINS["F"], 100)
        self.pwm["F"].start(0)
        self.pwm["B"]=GPIO.PWM(PINS["B"], 100)
        self.pwm["B"].start(0)

        self.reversed=False
        self.DBG=False
    def setPower(self,power):
        self.power=power
        if power>0:
            self.pwm["F"].start(power)
            self.pwm["B"].start(0)
        elif power<0:
            self.pwm["F"].start(0)
            self.pwm["B"].start(-power)
        else:
            self.pwm["F"].start(0)
            self.pwm["B"].start(0)
    
    def update(self,speed):
        self.speed=speed
        self.power=self.PID(self.speed-self.target_speed)
        self.setPower(self.power)
class Car():
    def __init__(self):
        self.motor1=Motor(PINS={"F":11,"B":13})
        self.motor2=Motor(PINS={"F":22,"B":15})
        self.motor3=Motor(PINS={"F":16,"B":18})
        self.motor4=Motor(PINS={"F":19,"B":21})
        self.motors=[self.motor1,self.motor2,self.motor3,self.motor4]

        self.ser=serial.Serial('/dev/ttyUSB0',9600,timeout=4)
        time.sleep(2)
        print("FIRST",self.ser.read_all())
    def setSpeedAll(self,speed):
        for i in range(len(self.motors)):
            self.motors[i].target_speed=speed
    def setSpeed(self,speeds):
        for i in range(len(self.motors)):
            self.motors[i].target_speed=speeds[i]
    def loop(self):
        data=ser.readline().decode().replace('\n','').replace('\r','').split(',')
        for i in range(len(data)-1):
            self.motors[i].update(float(data[i]))
        voltage=data[-1]
        print("Current Speed:",self.motor1.speed,"Current POWER",self.motor1.power,end='    \r')
print("Motor Driver Moudle Loaded With name:",__name__)
if __name__=="__main__":
    speed=int(input("Speed?"))#单位：RPS
    upload=input("Upload Data?")=="Y"
    if(speed==114514):
        randoms=True
    else:
        randoms=False
    ser=serial.Serial('/dev/ttyUSB0',9600,timeout=4)
    time.sleep(2)
    print("FIRST",ser.read_all())
    car=Car()
    car.setSpeed([-2,2,2,0-2])
    if upload:
        client=mqtt_client.Client(client_id="piRobot001")
        client.username_pw_set("allen","800607")
        client.connect("192.168.1.7",1883)
    try:
        while True:
            car.loop()
                
    except KeyboardInterrupt:
        ser.close()
        GPIO.cleanup()
        print("GPIO Cleaned Up")