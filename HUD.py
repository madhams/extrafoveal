#-------------move images on canvas-------------

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

distance = 112
x_boundary = 1500
y_boundary = 800
x_start = x_boundary/2
y_start = y_boundary/2
marker_x = x_start
marker_y = y_start
right_toggle = 0
overflow = 100

#Values are received from angle given by magnetometer
look_x = 400
look_y = 400
mark_bound = 50
#change speed to depend on ratio between look_x and look_y
xspeed = (look_x - marker_x)/50
yspeed = (look_y - marker_y)/50

def count_up(event):
   global distance
   distance = distance + 1
   # dist_lab.configure(text = f'{distance} skelingtons')
   canvas.itemconfigure(dist, text = f'{distance} m')
   # if distance == 1:
   #       canvas.itemconfigure(dist, text = f'{distance} meter')

def count_down(event):
   global distance
   if distance > 0:
      distance = distance - 1
      # dist_lab.configure(text = f'{distance} skelingtons')
      canvas.itemconfigure(dist, text = f'{distance} m')
      # if distance == 1:
      #    canvas.itemconfigure(dist, text = f'{distance} meter')

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
      canvas.move(dist,200-x_boundary,0)
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
   global marker_x, marker_y, look_x, look_y

   # get bounding box of the image
   (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance)
   
   ## Resets marker to new starting point for when a POI is reached
   canvas.moveto(guidance, x_start-25, y_start-25)
   canvas.moveto(dist, x_start+20, y_start+5)
   look_x = x_start
   look_y = y_start
   marker_x = x_start
   marker_y = y_start
   x_pos.configure(text = f'current x value: {marker_x}')
   y_pos.configure(text = f'current y value: {marker_y}')


#Funciton enabling all movement of marker and distance text
def moveMark():
   global xspeed, yspeed, look_x, look_y, marker_x, marker_y

   # get bounding box of the image
   (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance)


   #boundaries of the canvas to swap sides of display
   #Right side overflow
   if look_x >= x_boundary + overflow:
      canvas.moveto(guidance, mark_bound-25, marker_y-25)
      canvas.moveto(dist, mark_bound+20, marker_y+5)
      marker_x = mark_bound
      look_x = look_x - (x_boundary + (2*overflow))
      x_pos.configure(text = f'current x value: {marker_x}')
   #Left side overflow
   if look_x <= -(overflow):
      canvas.moveto(guidance, x_boundary-mark_bound-25, marker_y-25)
      canvas.moveto(dist, x_boundary-mark_bound+20, marker_y+5)
      marker_x = x_boundary - mark_bound
      look_x = look_x + (x_boundary + (2*overflow))
      x_pos.configure(text = f'current x value: {marker_x}')
   #Bottom overflow
   if look_y >= y_boundary + overflow:
      canvas.moveto(guidance, marker_x-25, mark_bound-25)
      canvas.moveto(dist, marker_x+20, mark_bound+5)
      marker_y = mark_bound
      look_y = look_y - (y_boundary + (2*overflow))
      y_pos.configure(text = f'current y value: {marker_y}')
   #Top overflow
   if look_y <= -(overflow):
      canvas.moveto(guidance, marker_x-25, y_boundary-mark_bound-25)
      canvas.moveto(dist, marker_x+20, y_boundary-mark_bound+5)
      marker_y = y_boundary - mark_bound
      look_y = look_y + (y_boundary + (2*overflow))
      y_pos.configure(text = f'current y value: {marker_y}')

   ## Modifiyng the speed at which the marker travels
   ## if the point to get to is outside of horizontal boundaries then marker will 
   ## stop moving in out of bounds direction
   if (marker_x <= mark_bound and look_x <=mark_bound) or (marker_x >= x_boundary-mark_bound and look_x >= x_boundary-mark_bound):
      xspeed = 0
   ## Otherwise it will gradually speed up and slow down with distance
   else:
      xspeed = (look_x - marker_x)/25
   ## if the point to get to is outside of vertical boundaries then marker will 
   ## stop moving in out of bounds direciton
   if (marker_y <= mark_bound and look_y <= mark_bound) or (marker_y >= y_boundary-mark_bound and look_y >= y_boundary-mark_bound):
      yspeed = 0
   ## Otherwise it will gradually speed up and slow down with distance
   else:
      yspeed = (look_y - marker_y)/50

   move_x.configure(text = f'current x speed: {xspeed}')
   move_y.configure(text = f'current y speed: {yspeed}')
   

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

   if ((mark_bound <= marker_x <= x_boundary - mark_bound) and not (look_x -3 < marker_x < look_x + 3)):
      #move image in x direction
      canvas.move(guidance, xspeed, 0)
      canvas.move(dist, xspeed, 0)
      marker_x = marker_x + xspeed
      if marker_x > x_boundary - mark_bound:
        marker_x = x_boundary - mark_bound
      elif marker_x < mark_bound:
        marker_x = mark_bound
      x_pos.configure(text = f'current x value: {marker_x}')
   if ((mark_bound <= marker_y <= y_boundary - mark_bound) and not (look_y -3 < marker_y < look_y + 3)):
      #move image in x direction
      canvas.move(guidance, 0, yspeed)
      canvas.move(dist, 0, yspeed)
      marker_y = marker_y + yspeed
      if marker_y > y_boundary - mark_bound:
         marker_y = y_boundary - mark_bound
      elif marker_y < mark_bound:
         marker_y = mark_bound
      y_pos.configure(text = f'current x value: {marker_y}')

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

#Load an image in the script
img= (Image.open("marker.png"))

##No longer using had a visual background that interfered with marker image
# dist_lab = tk.Label(window, fg='black')
# dist_lab.configure(text = f'{distance} meters')
# dist_lab.pack()
# obj_dist = canvas.create_window(x_start+20, y_start, window=dist_lab, anchor='nw') 

#Did NOT WORK
# dist_lab.place(100,100,width=50)

dist = canvas.create_text(x_start+20, y_start+5, text=f'{distance} m', font='SegoeUI 13',fill='black', anchor='nw')


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
resized_image= img.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)

photoimage = ImageTk.PhotoImage(resized_image)
# guidance = canvas.create_image(350,350,image=photoimage,anchor='nw')
guidance = canvas.create_image(x_start,y_start,image=photoimage,anchor='center')

#canvas.create_text(3, 120, text=f'test skull: {distance}', font='SegoeUI 13',fill='black', anchor='nw')

canvas.after(20, moveMark)
window.mainloop()