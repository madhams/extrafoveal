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
from Mapbox_functions import find_bearing_angle, haversine_distance, get_route_coordinates
import numpy as np
import serial
import adafruit_gps
import os
import csv
import adafruit_dotstar as dotstar
import atexit
"""
Notes:
 - GPS is accurate
 - Magnetometer works significntly better outside
 - Need to find if bearing angle calculation is accurate
 - Need to change distance in moveMark function
"""

# Control variables
is_display = False  # Determines if one gets rid of bar for tkinter screen
# For display
coord_idx = 0
coord_list = 0
# Calibrate Compass
# Note that I will use GPIO zero code, but just replace with the LED strip code
# Use other python library  for screen measurement
i2c = busio.I2C(board.SCL, board.SDA)
mag = adafruit_lis2mdl.LIS2MDL(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

#hardiron_cal = compass.calibrate(mag)
hardiron_cal = [[-79.05, 10.65], [-51.75, 33.9], [-13.95, 35.4]]

# Set screen metrics
distance = 112
if is_display:
   x_boundary = 1920  # +10 to eliminate any white areas on screen (SOLVED)
   y_boundary = 1080
else:
   x_boundary = 1200
   y_boundary = 600

x_start = x_boundary/2
y_start = y_boundary/2
marker_x = x_start
marker_y = y_start
right_toggle = 0
overflow = 4 * x_boundary
speed_var = 2.25
refresh_rate = 15

# Initialize LED strip
# Need to change LED strip colors here for warnings
dots = dotstar.DotStar(board.SCK, board.MOSI, 40, brightness=0.2)
white_brightness = 100
white_vec = (white_brightness, white_brightness, white_brightness)

#Values are received from angle given by magnetometer
look_x = []
look_y = []
mark_bound = 80
text_x = mark_bound / 2 - 5
text_y = mark_bound / 10
#change speed to depend on ratio between look_x and look_y
xspeeds = []
yspeeds = []

num = 0
guidance = []
dist = []

edge_margin = 20
x_values = []
y_values = []


def light_left(dots, turn_on=True):
   if turn_on:
      dots.fill((0,0,0))
      turn_on = False

   left_list = [19, 20, 21]
   for dot in left_list:
      dots[dot] = white_vec
   return None

def light_right(dots, turn_on=True):
   if turn_on:
      dots.fill((0,0,0))
      turn_on = False

   right_list = [0, 1, 2]
   for dot in right_list:
      dots[dot] = white_vec
   return None

def light_top(dots, turn_on=True):
   if turn_on:
      dots.fill((0,0,0))
      turn_on = False

   top_list = [10, 11, 12]
   for dot in top_list:
      dots[dot] = white_vec
   return None

def exit_func():
   dots.fill((0,0,0))

# In order to read csv output from gps, use filename and function below
filename = 'gps_info.csv'

def read_csv(fname):
   data = None
   with open(fname, mode='r') as file:
      csvFile = csv.reader(file)
      data = next(csvFile)
   return data

obs_filename = 'gps_obs_info.csv'
def read_csv_obs(fname):
    # Note that the order for this should be angles, distances, markers for each line
    data = []
    with open(fname, mode='r') as file:
        csvFile = csv.reader(file)
        for line in csvFile:
            data.append(line)
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


prev_target_angle = 0
target_angle = 0
obs_angs = []
obs_dists = []
obs_labels = []


def moveMark():
   global xspeed, yspeed, look_x, look_y, marker_x, marker_y, coord_list, coord_idx, \
      prev_target_angle, target_angle, obs_angs, obs_dists, obs_labels, dist, guidance, num
   # get bounding box of the image
   # may want to remove averaging
   # Overflow will be used to determine FOV
   # Make overflow proportional to fov
   # look_x is where you want to look, not where you are actively looking

  # Updates GPS if there is a fix, doesn't if there isn't, initializes to right outside valhalla (can change)
   try:
      tmp = read_csv(filename)
      obs_tmp = read_csv_obs(obs_filename)
      if tmp != None:
         distance = tmp[0]
         target_angle = tmp[1]
         coord_idx = tmp[2]
         coord_list = tmp[3]
         #canvas.itemconfigure(obj_dist, text = f'{distance} m')
         #canvas.itemconfigure(coord_progress, text = f'{coord_idx} / {coord_list} Points Reached')
         prev_target_angle = target_angle
      if obs_tmp != None:
         obs_angs = obs_tmp[0]
         obs_dists = obs_tmp[1]
         obs_labels = obs_tmp[2]
         for i in range(num):
            canvas.itemconfigure(dist[i], text=obs_dists[i] + ' m')

   except StopIteration:
      target_angle = prev_target_angle
      pass


   mag_pitch_vec = compass.run_compass_tilt(mag, accel, hardiron_cal)
   mag_angle = mag_pitch_vec[0]
   offset_angle = find_marker_shift(float(target_angle), mag_angle)
   ang2pixel_arr = []
   #ang2pixel_arr.append(offset_angle / 360 * 9 * x_boundary)
   for i in range(num):
      ang2pixel_arr.append(find_marker_shift(float(obs_angs[i]), mag_angle) / 360 * 9 * x_boundary)
   # (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance)
   # ang2pixel = offset_angle / 360 * 9 * x_boundary
   pitch_angle = mag_pitch_vec[2] / 360 * 16.5 * y_boundary  # Keep all in same y value

   #print(f"Angle: {compass.run_compass_tilt(mag, accel, hardiron_cal)}")
   print(f'Angle: {mag_angle}')
   print(f'Offset angle is: {offset_angle}')
   print(f'Bearing angle is: {target_angle}')
   print(f'Pitch Angle: {mag_pitch_vec[2]}')
   #look_x = float(x_boundary / 2 - ang2pixel)
   look_y = [float(y_boundary / 2 - pitch_angle) for i in range(len(ang2pixel_arr))]
   look_x = [float(x_boundary / 2 - ang2pixel_arr[i]) for i in range(len(ang2pixel_arr))]
   #eye_x_pos.configure(text = f'current look x value:  {look_x}')
   #boundaries of the canvas to swap sides of display
   # Adjust for edge cases, add/subtract from overflow to set 

   for i in range(num):
      # Right side overflow
      if look_x[i] >= x_boundary + overflow:
         canvas.moveto(guidance[i], mark_bound / 2, y_values[i] - mark_bound / 2)
         canvas.moveto(dist[i], mark_bound + text_x, y_values[i] + text_y)
         look_x[i] = look_x[i] - (x_boundary + (2 * overflow))

      # Left side overflow
      if look_x[i] <= -(overflow):
         canvas.moveto(guidance[i], x_boundary - 1.5 * mark_bound, y_values[i] - mark_bound / 2)
         canvas.moveto(dist[i], x_boundary + text_x, y_values[i] + text_y)
         look_x[i] = look_x[i] + (x_boundary + (2 * overflow))

      # Bottom overflow
      if look_y[i] >= y_boundary + overflow:
         canvas.moveto(guidance[i], x_values[i] - mark_bound / 2, mark_bound / 2)
         canvas.moveto(dist[i], x_values[i] + text_x, mark_bound + text_y)
         look_y[i] = look_y[i] - (y_boundary + (2 * overflow))

      # Top overflow
      if look_y[i] <= -(overflow):
         canvas.moveto(guidance[i], x_values[i] - mark_bound / 2, y_boundary - 1.5 * mark_bound)
         canvas.moveto(dist[i], x_values[i] + text_x, y_boundary + text_y)
         look_y[i] = look_y[i] + (y_boundary + (2 * overflow))

      ## Modifiyng the speed at which the marker travels
      ## if the point to get to is outside of horizontal boundaries then marker will
      ## stop moving in out of bounds direction

      if (x_values[i] <= mark_bound and look_x[i] <= mark_bound) or (
              x_values[i] >= x_boundary - mark_bound and look_x[i] >= x_boundary - mark_bound):
         xspeeds[i] = 0
         if (x_values[i] <= mark_bound and look_x[i] <= mark_bound):
            canvas.moveto(guidance[i], -mark_bound / 2, y_values[i] - mark_bound / 2)
            canvas.moveto(dist[i], text_x, y_values[i] + text_y)
         else:
            canvas.moveto(guidance[i], x_boundary - mark_bound / 2, y_values[i] - mark_bound / 2)
            canvas.moveto(dist[i], x_boundary + text_x, y_values[i] + text_y)
      ## Otherwise it will gradually speed up and slow down with distance
      else:
         xspeeds[i] = (look_x[i] - x_values[i]) / 50
      ## if the point to get to is outside of vertical boundaries then marker will
      ## stop moving in out of bounds direciton
      if (y_values[i] <= mark_bound and look_y[i] <= mark_bound) or (
              y_values[i] >= y_boundary - mark_bound and look_y[i] >= y_boundary - mark_bound):
         yspeeds[i] = 0
         if (y_values[i] <= mark_bound and look_y[i] <= mark_bound):
            canvas.moveto(guidance[i], x_values[i] - mark_bound / 2, -mark_bound / 2)
            canvas.moveto(dist[i], x_values[i] + text_x, text_y)
         else:
            canvas.moveto(guidance[i], x_values[i] - mark_bound / 2, y_boundary - mark_bound / 2)
            canvas.moveto(dist[i], x_values[i] + text_x, y_boundary + text_y)
      ## Otherwise it will gradually speed up and slow down with distance
      else:
         yspeeds[i] = (look_y[i] - y_values[i]) / 50

      ## Old code that had issues with bounding and would not move once hitting
      ## the boundary wall

      # if (((100 < marker_x < x_boundary - 100) and not (look_x -3 < marker_x < look_x + 3)) or
      #    ((100 < marker_y < y_boundary - 100) and not (look_y -3 < marker_y < look_y + 3))):
      #       # move the image
      #       canvas.move(guidance, xspeed, yspeed)
      #       canvas.move(obj_dist, xspeed, yspeed)
      #       marker_x = marker_x + xspeed
      #       marker_y = marker_y + yspeed
      #       # if marker_x > x_boundary - 100:
      #       #    marker_x = x_boundary - 100
      #       # elif marker_x < 100:
      #       #    marker_x = 100
      #       # if marker_y > y_boundary - 100:
      #       #    marker_y = y_boundary - 100
      #       # elif marker_y < 100:
      #       #    marker_y = 100

      #       x_pos.configure(text = f'current x value: {marker_x}')
      #       y_pos.configure(text = f'current y value: {marker_y}')

      if ((mark_bound - edge_margin <= x_values[i] <= x_boundary - mark_bound + edge_margin) and not (
              look_x[i] - 5 < x_values[i] < look_x[i] + 5)):
         # move image in x direction
         canvas.move(guidance[i], xspeeds[i], 0)
         canvas.move(dist[i], xspeeds[i], 0)
         (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance[i])
         x_values[i] = (leftPos + rightPos) / 2
      elif x_values[i] > x_boundary - mark_bound:
         x_values[i] = x_boundary - mark_bound
      elif x_values[i] < mark_bound:
         x_values[i] = mark_bound

      if ((mark_bound <= y_values[i] <= y_boundary - mark_bound) and not (look_y[i] - 5 < y_values[i] < look_y[i] + 5)):
         # move image in x direction
         canvas.move(guidance[i], 0, yspeeds[i])
         canvas.move(dist[i], 0, yspeeds[i])
         (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance[i])
         y_values[i] = (topPos + bottomPos) / 2
      elif y_values[i] > y_boundary - mark_bound:
         y_values[i] = y_boundary - mark_bound
      elif y_values[i] < mark_bound:
         y_values[i] = mark_bound

   canvas.after(refresh_rate, moveMark)


def move_app(event):
    window.geometry(f'+{event.x_root}+{event.y_root}')


window = tk.Tk()
canvas = tk.Canvas(window,width=x_boundary,height=y_boundary, bg='black')
canvas.pack()
canvas.tab = [{} for q in range(50)]
canvas.focus_set()

#Load an image in the script
img = (Image.open("destiny_marker.png"))
blue = (Image.open("marker_blue.png"))
green = (Image.open("marker_green.png"))
red = (Image.open("marker_red.png"))
yellow = (Image.open("marker_yellow.png"))
#Resize the Image using resize method
marker_img = img.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)
marker_blue = blue.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)
marker_green = green.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)
marker_red = red.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)
marker_yellow = yellow.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)


icons = {'path' : marker_img, 'good' : marker_blue, 'danger' : marker_red, 'investigate': marker_yellow, 'path_end' : marker_green}
icon_value = 0
tmp = read_csv_obs(obs_filename)
icon_values = tmp[2]


for i in range(len(icon_values)):
   canvas.tab[num]['image'] = ImageTk.PhotoImage(icons[icon_values[i]])
   guidance.append(canvas.create_image(0,0, image=canvas.tab[num]['image'], anchor='center'))
   dist.append(canvas.create_text(text_x, text_y, text=f'{tmp[1][i]} m', font='SegoeUI 13',fill='white', anchor='nw'))
   x_values.append(0)
   y_values.append(0)
   look_x.append(0)
   look_y.append(0)
   xspeeds.append(0)
   yspeeds.append(0)
   num += 1

# photoimage = ImageTk.PhotoImage(marker_img)
# guidance = canvas.create_image(x_start,y_start,image=photoimage,anchor='center')

#canvas.create_text(3, 120, text=f'test skull: {distance}', font='SegoeUI 13',fill='black', anchor='nw')

if is_display:
   window.overrideredirect(True)
   title_bar = tk.Frame(window, bg='black', bd=1)
   title_bar.pack(expand=1, fill=tk.X)
   title_bar.bind("<B1-Motion>", move_app)
   title_label = tk.Label(title_bar, text="hello", bg='black')
   title_label.pack(side=tk.LEFT)
   close_button = tk.Button(window, text="x", font="Helvetica, 8", command=window.quit)
   close_button.pack(pady=10)


canvas.after(refresh_rate, moveMark)
window.mainloop()

atexit.register(exit_func)
