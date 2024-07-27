import serial,time
import matplotlib.pyplot as plt
ser = serial.Serial('COM4',9600,timeout=4)
ser.write(b'!')
time.sleep(2)
print("FIRST",ser.read_all())
try:
    while True:
        data=ser.readline().decode().replace('\n','').replace('\r','').split(',')
        print(data)
except KeyboardInterrupt:
    ser.close()