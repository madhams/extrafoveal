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
import adafruit_dotstar as dotstar
import atexit

# This file is designed to implement the pitch marker movement functionality


# Calibrate Compass
# Note that I will use GPIO zero code, but just replace with the LED strip code
# Use other python library  for screen measurement
print(dir(board))
i2c = busio.I2C(board.SCL, board.SDA)
mag = adafruit_lis2mdl.LIS2MDL(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
#hardiron_cal = compass.calibrate(mag)
#hardiron_cal = [[-70.5, 29.7], [-58.8, 24.15], [-16.2, 82.35]]
#hardiron_cal = [[-80.1, 3.15], [19.65, 104.55], [19.05, 96.0]]  # At table in OEDK
#hardiron_cal = [[-93.45, 31.65], [-55.05, 68.7], [-28.799999999999997, 93.0]]
#hardiron_cal =  [[-68.7, -2.55], [-34.05, 26.4], [2.55, 65.85]]
hardiron_cal = [[-79.95, 14.1], [-49.35, 37.05], [-4.35, 81.75]]
#print(f"Hardiron Cal = {hardiron_cal}")
# Finish calibration
distance = 112
x_boundary = 1200
y_boundary = 600
x_start = x_boundary/2
y_start = y_boundary/2
marker_x = x_start
marker_y = y_start
right_toggle = 0
overflow = 4 * x_boundary

# Initialize LED strip
dots = dotstar.DotStar(board.SCK, board.MOSI, 40, brightness=0.2)
white_brightness = 100
white_vec = (white_brightness, white_brightness, white_brightness)
#Values are received from angle given by magnetometer
look_x = 400
look_y = 400
marker_size = 50
#change speed to depend on ratio between look_x and look_y
xspeed = 2 * (look_x - marker_x)/50
yspeed = (look_y - marker_y)/50
edge_margin = 20


def light_left(dots):
   dots.fill((0,0,0))
   left_list = [0]
   for dot in left_list:
      dots[dot] = white_vec
   return None

def light_right(dots):
   dots.fill((0,0,0))
   right_list = [30]
   for dot in right_list:
      dots[dot] = white_vec
   return None

def exit_func():
   dots.fill((0,0,0))

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
   global xspeed, yspeed, look_x, look_y, marker_x, marker_y
   # get bounding box of the image
   # may want to remove averaging
   # Overflow will be used to determine FOV
   # Make overflow proportional to fov
   # look_x is where you want to look, not where you are actively looking
   target_angle = 0 # in degrees
   north_angle = 70
   tmp = compass.run_compass_tilt(mag, accel, hardiron_cal)
   mag_angle = adjust_north(tmp[0], north_angle)
   offset_angle = find_marker_shift(target_angle, mag_angle)
   (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance)
   ang2pixel = offset_angle / 360 * 9 * x_boundary
   pitch_angle = tmp[2] / 360 * 18 * y_boundary
   #print(f"Angle: {compass.run_compass_tilt(mag, accel, hardiron_cal)}")
   #print(f'Angle: {mag_angle}')
   #print(f'Offset angle is: {offset_angle}')
   print(f'Pitch angle is: {tmp[2]}')
   # look_x = float(x_boundary / 2 - ang2pixel) # correct for x, but set to nothign to test y
   look_y = float(y_boundary / 2 - pitch_angle)
   look_x = x_boundary / 2
   eye_x_pos.configure(text = f'current look x value:  {look_x}')
   eye_y_pos.configure(text = f'current look y value:  {look_y}')
   #boundaries of the canvas to swap sides of display
   # Adjust for edge cases, add/subtract from overflow to set 

   """
   if look_y >= y_boundary + overflow:
      canvas.moveto(guidance, marker_x-marker_size/2, marker_size/2)
      canvas.moveto(obj_dist, marker_x+20, marker_size)
      marker_y = marker_size
      look_y = look_y - (y_boundary + (2*overflow))
      y_pos.configure(text = f'current y value: {marker_y}')
   if look_y <= -(overflow):
      canvas.moveto(guidance, marker_x-marker_size/2, y_boundary-1.5*marker_size)
      canvas.moveto(obj_dist, marker_x+20, y_boundary-marker_size)
      marker_y = y_boundary - marker_size
      look_y = look_y + (y_boundary + (2*overflow))
      y_pos.configure(text = f'current y value: {marker_y}')
   """

   if (marker_y <= marker_size and look_y <= marker_size) or (marker_y >= y_boundary-marker_size and look_y >= y_boundary-marker_size):
      yspeed = 0
      if (marker_y <= marker_size and look_y <= marker_size):
         canvas.moveto(guidance, marker_x - marker_size/2, -marker_size/2)
         canvas.moveto(obj_dist, marker_x, 20)
      else:
         canvas.moveto(guidance, marker_x - marker_size/2, y_boundary-marker_size/2)
         canvas.moveto(obj_dist, marker_x, y_boundary+20)
   else:
      yspeed = (look_y - marker_y)/50
   move_x.configure(text = f'current x speed: {xspeed}')
   move_y.configure(text = f'current y speed: {yspeed}')

   #if ((marker_size - edge_margin <= marker_x <= x_boundary - marker_size + edge_margin) and not (abs(look_x) - 10 < marker_x < abs(look_x) + 10)) and (-135 < offset_angle < 135):
      #move image in x direction
      #canvas.move(guidance, xspeed, 0)
      #canvas.move(obj_dist, xspeed, 0)
      #marker_x = marker_x + xspeed
   #elif marker_x > x_boundary - marker_size + edge_margin:
    #  marker_x = x_boundary - marker_size 
   #elif marker_x < marker_size - edge_margin:
    #  marker_x = marker_size
   #x_pos.configure(text = f'current x value: {marker_x}')

   if ((marker_size - edge_margin < marker_y <= y_boundary - marker_size + edge_margin) and not (abs(look_y) -3 < marker_y < abs(look_y) + 3)):
      #move image in x direction
      canvas.move(guidance, 0, yspeed)
      canvas.move(obj_dist, 0, yspeed)
      marker_y = marker_y + yspeed
   elif marker_y > y_boundary - marker_size:
      marker_y = y_boundary - marker_size
   elif marker_y <= marker_size:
      marker_y = marker_size
   y_pos.configure(text = f'current y value: {marker_y}')
   canvas.after(5, moveMark)


window = tk.Tk()

#Movement
window.bind("<w>",look_up)
window.bind("<s>",look_down)
window.bind("<a>",look_left)
window.bind("<d>",look_right)
window.bind("<Left>",move_left)
window.bind("<Right>",move_right)
window.bind("<space>",reset)

#Counting
window.bind("<Up>",count_up)
window.bind("<Down>",count_down)


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

#Resize the Image using resize method
resized_image= img.resize((marker_size,marker_size), Image.Resampling.LANCZOS)

photoimage = ImageTk.PhotoImage(resized_image)
# guidance = canvas.create_image(350,350,image=photoimage,anchor='nw')
guidance = canvas.create_image(x_start,y_start,image=photoimage,anchor='center')

canvas.after(10, moveMark)
window.mainloop()

atexit.register(exit_func)
