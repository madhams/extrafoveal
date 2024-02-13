import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import compass
import board
import adafruit_lis2mdl
import adafruit_lsm303_accel
import math
import time
import busio
from gpiozero import LED
from Mapbox_functions import find_bearing_angle, haversine_distance, get_route_coordinates
import numpy as np
import serial
import adafruit_gps
import os
import csv
"""
Notes:
 - GPS is accurate
 - Magnetometer works significntly better outside
 - Need to find if bearing angle calculation is accurate
 - Need to change distance in moveMark function
"""
# Initialize GPS
#os.system('sudo chmod 666 /dev/ttyS0')
#uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
#gps = adafruit_gps.GPS(uart, debug=False)
#gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
#gps.send_command(b"PMTK220,1000")
#gps_lon = -95.400303  # Right outside Valhalla
#gps_lat = 29.719109  # Right outside Valhalla
#gps_timer = time.monotonic()

# Coordinate List
# first list is for IM field 5
# second list is for outside OEDK on street and back
#coord_list = [(-95.403431, 29.718996), (-95.404681, 29.719268), (-95.403750, 29.719614)]

# Calibrate Compass
# Note that I will use GPIO zero code, but just replace with the LED strip code
# Use other python library  for screen measurement
i2c = busio.I2C(board.SCL, board.SDA)
mag = adafruit_lis2mdl.LIS2MDL(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
hardiron_cal = compass.calibrate(mag)
#hardiron_cal = [[-70.5, 29.7], [-58.8, 24.15], [-16.2, 82.35]]
#hardiron_cal = [[-80.1, 3.15], [19.65, 104.55], [19.05, 96.0]]  # At table in OEDK
#hardiron_cal = [[-93.45, 31.65], [-55.05, 68.7], [-28.799999999999997, 93.0]]
#hardiron_cal =  [[-68.7, -2.55], [-34.05, 26.4], [2.55, 65.85]]
#hardiron_cal = [[-79.95, 14.1], [-49.35, 37.05], [-4.35, 81.75]]
#print(f"Hardiron Cal = {hardiron_cal}")
# Finish calibration
#screen_vec = tk.Tk()
led_right = LED(10)
led_left = LED(9)
distance = 112
x_boundary = 1200 #1920 + 10  # +10 to eliminate any white areas on screen
y_boundary = 600  #1080
x_start = x_boundary/2
y_start = y_boundary/2
marker_x = x_start
marker_y = y_start
right_toggle = 0
overflow = 4 * x_boundary
speed_var = 2.25
#Values are received from angle given by magnetometer
look_x = 400
look_y = 540
marker_size = 50
#change speed to depend on ratio between look_x and look_y
xspeed = speed_var * (look_x - marker_x)/50
yspeed = (look_y - marker_y)/50
edge_margin = 20

# In order to read csv output from gps, use filename and function below
filename = 'gps_info.csv'
def read_csv(fname):
   data = None
   with open(filename, mode='r') as file:
      csvFile = csv.reader(file)
      data = next(csvFile)
   return data

def find_sign(number):
   s = 0
   if number > 0:
      s = 1
   else:
      s = -1
   return s


def find_marker_shift(target_angle, mag_angle):
   ang_diff = target_angle - mag_angle
   res = 0

   if abs(ang_diff) < 180:
      ang_sign = find_sign(ang_diff)
      res = ang_sign * abs(ang_diff)
   else:
      ang_sign = -1 * find_sign(ang_diff)
      res = ang_sign * (360 - abs(ang_diff))

   return res


def adjust_north(angle, north_offset):
    return (angle - north_offset) % 360

def count_up(event):
   global distance
   distance = distance + 1
   dist_lab.configure(text = f'{distance}')

def count_down(event):
   global distance
   if distance > 0:
      distance = distance - 1
      dist_lab.configure(text = f'{distance}')

def move_up(event):
   global  marker_y
   marker_y = marker_y - 10
   if marker_y >= 100:
      canvas.move(guidance,0,-10)
      canvas.move(obj_dist,0,-10)     
   if marker_y == -100:
      canvas.move(guidance,0,y_boundary-200)
      canvas.move(obj_dist,0,y_boundary-200)
      marker_y = y_boundary - 100
   y_pos.configure(text = f'current y value: {marker_y}')


def move_down(event):
   global  marker_y
   marker_y = marker_y + 10
   if marker_y <= y_boundary - 100:
      canvas.move(guidance,0,10)
      canvas.move(obj_dist,0,10)  
   if marker_y == y_boundary + 100:
      canvas.move(guidance,0,200-y_boundary)
      canvas.move(obj_dist,0,200-y_boundary)
      marker_y = 100
   y_pos.configure(text = f'current y value: {marker_y}')

def move_left(event):
   global  marker_x
   
   if (marker_x > 100) and (marker_x <= x_boundary-100):
      canvas.move(guidance,-10,0)
      canvas.move(obj_dist,-10,0)
   if marker_x == -100:
      canvas.move(guidance,x_boundary-200,0)
      canvas.move(obj_dist,x_boundary-200,0)
      marker_x = x_boundary + 100
   # if marker_x > x_boundary-110:
   #    marker_x = x_boundary-110
   marker_x = marker_x - 10
   x_pos.configure(text = f'current x value: {marker_x}')



def move_right(event):
   global  marker_x
   
   if (marker_x < x_boundary-100) and (marker_x >= 100):
      canvas.move(guidance,10,0)
      canvas.move(obj_dist,10,0)
   if marker_x == x_boundary + 100:
      canvas.move(guidance,200-x_boundary,0)
      canvas.move(obj_dist,200-x_boundary,0)
      marker_x = -100
   # if marker_x < 110:
   #    marker_x = 110
   marker_x = marker_x + 10
   x_pos.configure(text = f'current x value: {marker_x}')
   

# def toggle_right(event):
#    global  marker_x
   
#    if (marker_x < x_boundary-100) and (marker_x >= 100):
#       canvas.move(guidance,10,0)
#       canvas.move(obj_dist,10,0)
#    if marker_x == x_boundary + 100:
#       canvas.move(guidance,200-x_boundary,0)
#       canvas.move(obj_dist,200-x_boundary,0)
#       marker_x = -100
#    # if marker_x < 110:
#    #    marker_x = 110
#    marker_x = marker_x + 10
#    x_pos.configure(text = f'current x value: {marker_x}')

def look_up(event):
   global look_y
   look_y = look_y - 20
   eye_y_pos.configure(text = f'current look y value: {look_y}')

def look_down(event):
   global look_y
   look_y = look_y + 20
   eye_y_pos.configure(text = f'current look y value: {look_y}')

def look_left(event):
   global look_x
   look_x = look_x - 20
   eye_x_pos.configure(text = f'current look x value: {look_x}')

def look_right(event):
   global look_x
   look_x = look_x + 20
   eye_x_pos.configure(text = f'current look x value: {look_x}')

def reset(event):
   global marker_x, marker_y

   # get bounding box of the image
   (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance)
   
   canvas.moveto(guidance, x_start-50, y_start-50)
   canvas.moveto(obj_dist, x_start+20, y_start)
   marker_x = x_start
   marker_y = y_start
   x_pos.configure(text = f'current x value: {marker_x}')
   y_pos.configure(text = f'current y value: {marker_y}')

def moveMark():
   global xspeed, yspeed, look_x, look_y, marker_x, marker_y, coord_list, gps_lon, gps_lat, coord_idx, gps_timer
   # get bounding box of the image
   # may want to remove averaging
   # Overflow will be used to determine FOV
   # Make overflow proportional to fov
   # look_x is where you want to look, not where you are actively looking

  # Updates GPS if there is a fix, doesn't if there isn't, initializes to right outside valhalla (can change)
   prev_target_angle = 0
   try:
      tmp = read_csv(filename)
      if tmp != None:
         distance = tmp[0]
         target_angle = tmp[1]
         dist_lab.configure(text=f'{distance}')
         prev_target_angle = target_angle
   except StopIteration:
      target_angle = prev_target_angle
      pass

   mag_pitch_vec = compass.run_compass_tilt(mag, accel, hardiron_cal)
   mag_angle = mag_pitch_vec[0]
   offset_angle = find_marker_shift(float(target_angle), mag_angle)
   (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance)
   ang2pixel = offset_angle / 360 * 9 * x_boundary
   pitch_angle = mag_pitch_vec[2] / 360 * 18 * y_boundary
   #print(f"Angle: {compass.run_compass_tilt(mag, accel, hardiron_cal)}")
   print(f'Angle: {mag_angle}')
   print(f'Offset angle is: {offset_angle}')
   print(f'Bearing angle is: {target_angle}')
   print(f'Pitch Angle: {mag_pitch_vec[2]}')
   look_x = float(x_boundary / 2 - ang2pixel)
   look_y = float(y_boundary / 2 - pitch_angle)
   #eye_x_pos.configure(text = f'current look x value:  {look_x}')
   #boundaries of the canvas to swap sides of display
   # Adjust for edge cases, add/subtract from overflow to set 

   if 160 < offset_angle < 170:
      canvas.moveto(guidance, marker_size/2, marker_y-marker_size/2)
      canvas.moveto(obj_dist, marker_size+20, marker_y)
      marker_x = marker_size
      look_x = look_x - (x_boundary + (2*overflow))
     # x_pos.configure(text = f'current x value: {marker_x}')
   if -170 < offset_angle < -160:
      canvas.moveto(guidance, x_boundary-1.5*marker_size, marker_y-marker_size/2)
      canvas.moveto(obj_dist, x_boundary-marker_size+20, marker_y)
      marker_x = x_boundary - marker_size
      look_x = look_x + (x_boundary + (2*overflow))
     # x_pos.configure(text = f'current x value: {marker_x}')
   if look_y >= y_boundary + overflow:
      canvas.moveto(guidance, marker_x-marker_size/2, marker_size/2)
      canvas.moveto(obj_dist, marker_x+20, marker_size)
      marker_y = marker_size
      look_y = look_y - (y_boundary + (2*overflow))
     # y_pos.configure(text = f'current y value: {marker_y}')
   if look_y <= -(overflow):
      canvas.moveto(guidance, marker_x-marker_size/2, y_boundary-1.5*marker_size)
      canvas.moveto(obj_dist, marker_x+20, y_boundary-marker_size)
      marker_y = y_boundary - marker_size
      look_y = look_y + (y_boundary + (2*overflow))
     # y_pos.configure(text = f'current y value: {marker_y}')

   if (marker_x <= marker_size and look_x <= marker_size) or (marker_x >= x_boundary - marker_size  and look_x >= x_boundary - marker_size):
      xspeed = 0
      if (marker_x <= marker_size and look_x <= marker_size):
         led_left.on()
         canvas.moveto(guidance, -marker_size/2, marker_y - marker_size/2)
         canvas.moveto(obj_dist, 20, marker_y)
      else:
         led_right.on()
         canvas.moveto(guidance, x_boundary-marker_size/2, marker_y - marker_size/2)
         canvas.moveto(obj_dist, x_boundary+20, marker_y)
   else:
      xspeed = speed_var*(look_x - marker_x) / 50
      led_left.off()
      led_right.off()

   if (marker_y <= marker_size and look_y <= marker_size) or (marker_y >= y_boundary-marker_size and look_y >= y_boundary-marker_size):
      yspeed = 0
      if (marker_y <= marker_size and look_y <= marker_size):
         canvas.moveto(guidance, marker_x - marker_size/2, -marker_size/2)
         canvas.moveto(obj_dist, marker_x, 20)
      else:
         canvas.moveto(guidance, marker_x - marker_size/2, y_boundary - marker_size / 2)
         canvas.moveto(obj_dist, marker_x, y_boundary + 20)
   else:
      yspeed = (look_y - marker_y)/50
   #move_x.configure(text = f'current x speed: {xspeed}')
   #move_y.configure(text = f'current y speed: {yspeed}')

   if ((marker_size - edge_margin <= marker_x <= x_boundary - marker_size + edge_margin) and not (abs(look_x) - 10 < marker_x < abs(look_x) + 10)) and (-135 < offset_angle < 135):
      #move image in x direction
      canvas.move(guidance, xspeed, 0)
      canvas.move(obj_dist, xspeed, 0)
      marker_x = marker_x + xspeed
   elif marker_x > x_boundary - marker_size + edge_margin:
      marker_x = x_boundary - marker_size 
   elif marker_x < marker_size - edge_margin:
      marker_x = marker_size
   #x_pos.configure(text = f'current x value: {marker_x}')

   if ((marker_size - edge_margin < marker_y < y_boundary - marker_size + edge_margin) and not (abs(look_y) - 10 < marker_y < abs(look_y) + 10)):
      #move image in x direction
      canvas.move(guidance, 0, yspeed)
      canvas.move(obj_dist, 0, yspeed)
      marker_y = marker_y + yspeed
   elif marker_y > y_boundary - marker_size + edge_margin:
      marker_y = y_boundary - marker_size
   elif marker_y < marker_size - edge_margin:
      marker_y = marker_size
    #  y_pos.configure(text = f'current x value: {marker_y}')
   canvas.after(15, moveMark)


window = tk.Tk()

canvas = tk.Canvas(window,width=x_boundary,height=y_boundary)
canvas.pack()
canvas.configure(background='black')
#Load an image in the script
img= (Image.open("destiny_marker.png"))

dist_lab = tk.Label(window, fg='black')
dist_lab.configure(text = f'{distance}')
dist_lab.pack()
obj_dist = canvas.create_window(x_start+20, y_start, window=dist_lab, anchor='nw') 
#Did NOT WORK
# dist_lab.place(100,100,width=50)
"""
x_pos = tk.Label(window, fg='black')
x_pos.configure(text = f'current x value: {marker_x}')
x_pos.pack()
canvas.create_window(0, 0, window=x_pos, anchor='nw')
y_pos = tk.Label(window, fg='black')
y_pos.configure(text = f'current y value: {marker_y}')
y_pos.pack()
canvas.create_window(0, 20, window=y_pos, anchor='nw')

eye_x_pos = tk.Label(window, fg='black')
eye_x_pos.configure(text = f'current look x value: {look_x}')
eye_x_pos.pack()
canvas.create_window(0, 40, window=eye_x_pos, anchor='nw')
eye_y_pos = tk.Label(window, fg='black')
eye_y_pos.configure(text = f'current look y value: {look_y}')
eye_y_pos.pack()
canvas.create_window(0, 60, window=eye_y_pos, anchor='nw')

move_x = tk.Label(window, fg='black')
move_x.configure(text = f'current x speed: {xspeed}')
move_x.pack()
canvas.create_window(0, 80, window=move_x, anchor='nw')
move_y = tk.Label(window, fg='black')
move_y.configure(text = f'current y speed: {yspeed}')
move_y.pack()
canvas.create_window(0, 100, window=move_y, anchor='nw')
"""
#Resize the Image using resize method
resized_image= img.resize((marker_size,marker_size), Image.Resampling.LANCZOS)

photoimage = ImageTk.PhotoImage(resized_image)
# guidance = canvas.create_image(350,350,image=photoimage,anchor='nw')
guidance = canvas.create_image(x_start,y_start,image=photoimage,anchor='center')

canvas.after(10, moveMark)
window.mainloop()
