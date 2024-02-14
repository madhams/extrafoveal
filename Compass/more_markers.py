#-------------move images on canvas-------------

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

distance = 112
x_boundary = 1000
y_boundary = 600
x_start = x_boundary/2
y_start = y_boundary/2
# marker_x = x_start
# marker_y = y_start
right_toggle = 0
overflow = 100
edge_margin = 20
x_values = []
y_values = []

#Values are received from angle given by magnetometer
look_x = []
look_y = []
mark_bound = 50
#change speed to depend on ratio between look_x and look_y
xspeeds = []
yspeeds = []

num = 0
guidance = []
dist = []

def click(event):
    global canvas, num, guidance, dist
    x,y = (event.x), (event.y)
    canvas.tab[num]['image'] = ImageTk.PhotoImage(marker_img)
    guidance.append(canvas.create_image(x,y, image=canvas.tab[num]['image'], anchor='center'))
    dist.append(canvas.create_text(x+20, y+5, text=f'{distance} m', font='SegoeUI 13',fill='black', anchor='nw'))
    x_values.append(x)
    y_values.append(y)
    look_x.append(x)
    look_y.append(y)
    xspeeds.append(0)
    yspeeds.append(0)
    num += 1

def blue(event):
    global canvas, num, guidance, dist
    x,y = (event.x), (event.y)
    canvas.tab[num]['image'] = ImageTk.PhotoImage(marker_blue)
    guidance.append(canvas.create_image(x,y, image=canvas.tab[num]['image'], anchor='center'))
    dist.append(canvas.create_text(x+20, y+5, text=f'{distance} m', font='SegoeUI 13',fill='black', anchor='nw'))
    x_values.append(x)
    y_values.append(y)
    look_x.append(x)
    look_y.append(y)
    xspeeds.append(0)
    yspeeds.append(0)
    num += 1

def green(event):
    global canvas, num, guidance, dist
    x,y = (event.x), (event.y)
    canvas.tab[num]['image'] = ImageTk.PhotoImage(marker_green)
    guidance.append(canvas.create_image(x,y, image=canvas.tab[num]['image'], anchor='center'))
    dist.append(canvas.create_text(x+20, y+5, text=f'{distance} m', font='SegoeUI 13',fill='black', anchor='nw'))
    x_values.append(x)
    y_values.append(y)
    look_x.append(x)
    look_y.append(y)
    xspeeds.append(0)
    yspeeds.append(0)
    num += 1

def red(event):
    global canvas, num, guidance, dist
    x,y = (event.x), (event.y)
    canvas.tab[num]['image'] = ImageTk.PhotoImage(marker_red)
    guidance.append(canvas.create_image(x,y, image=canvas.tab[num]['image'], anchor='center'))
    dist.append(canvas.create_text(x+20, y+5, text=f'{distance} m', font='SegoeUI 13',fill='black', anchor='nw'))
    x_values.append(x)
    y_values.append(y)
    look_x.append(x)
    look_y.append(y)
    xspeeds.append(0)
    yspeeds.append(0)
    num += 1

def yellow(event):
    global canvas, num, guidance, dist
    x,y = (event.x), (event.y)
    canvas.tab[num]['image'] = ImageTk.PhotoImage(marker_yellow)
    guidance.append(canvas.create_image(x,y, image=canvas.tab[num]['image'], anchor='center'))
    dist.append(canvas.create_text(x+20, y+5, text=f'{distance} m', font='SegoeUI 13',fill='black', anchor='nw'))
    x_values.append(x)
    y_values.append(y)
    look_x.append(x)
    look_y.append(y)
    xspeeds.append(0)
    yspeeds.append(0)
    num += 1

def deleteImage(event):
    global canvas, num
    canvas.tab[num-1] = {}
    del guidance[num-1]
    canvas.delete(dist[num-1])
    del dist[num-1]
    del look_x[num-1]
    del look_y[num-1]
    del x_values[num-1]
    del y_values[num-1]
    del xspeeds[num-1]
    del yspeeds[num-1]
    num -= 1

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

"""
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
   
"""
   
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
   global look_y, num, x_values, y_values, look_x
   for i in range(num):
      look_y[i] = look_y[i] - 20
   print("x_values:" + str(x_values))
   print("y_values:" + str(y_values))
   print("look_x:" + str(look_x))
   print("look_y:" + str(look_y))
   print("yspeeds:" + str(yspeeds))

def look_down(event):
   global look_y, num, x_values, y_values, look_x
   for i in range(num):
      look_y[i] = look_y[i] + 20
   print("x_values:" + str(x_values))
   print("y_values:" + str(y_values))
   print("look_x:" + str(look_x))
   print("look_y:" + str(look_y))
   print("yspeeds:" + str(yspeeds))


def look_left(event):
   global look_x, num, x_values, y_values, look_y
   for i in range(num):
      look_x[i] = look_x[i] - 20
   print("x_values:" + str(x_values))
   print("y_values:" + str(y_values))
   print("look_x:" + str(look_x))
   print("look_y:" + str(look_y))
   print("xspeeds:" + str(xspeeds))


def look_right(event):
   global look_x, num, x_values, y_values, look_y
   for i in range(num):
      look_x[i] = look_x[i] + 20
   print("x_values:" + str(x_values))
   print("y_values:" + str(y_values))
   print("look_x:" + str(look_x))
   print("look_y:" + str(look_y))
   print("xspeeds:" + str(xspeeds))


"""
def reset(event):
   global marker_x, marker_y, look_x, look_y, x_value

   # get bounding box of the image
   
   
   ## Resets marker to new starting point for when a POI is reached
   canvas.moveto(guidance, x_start-25, y_start-25)
   canvas.moveto(dist, x_start+20, y_start+5)
   (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance)
   x_value = (leftPos + rightPos)/2
   look_x = x_start
   look_y = y_start
   marker_x = x_start
   marker_y = y_start
   x_pos.configure(text = f'current x value: {x_value}')
   y_pos.configure(text = f'current y value: {marker_y}')
"""

#Funciton enabling all movement of marker and distance text
def moveMark():
   global xspeeds, yspeeds, look_x, look_y, x_values, y_values, guidance, dist, num

   """
   # get bounding box of the image
   for i in range(num):
      (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance[i])
      x_values[i] = (leftPos + rightPos)/2
      y_values[i] = (topPos + bottomPos)/2
   """

   #boundaries of the canvas to swap sides of display
   for i in range(num):
      #Right side overflow
      if look_x[i] >= x_boundary + overflow:
         canvas.moveto(guidance[i], mark_bound/2, y_values[i]-mark_bound/2)
         canvas.moveto(dist[i], mark_bound+20, y_values[i]+5)
         look_x[i] = look_x[i] - (x_boundary + (2*overflow))

      #Left side overflow
      if look_x[i] <= -(overflow):
         canvas.moveto(guidance[i], x_boundary-1.5*mark_bound, y_values[i]-mark_bound/2)
         canvas.moveto(dist[i], x_boundary+20, y_values[i]+5)
         look_x[i] = look_x[i] + (x_boundary + (2*overflow))

      #Bottom overflow
      if look_y[i] >= y_boundary + overflow:
         canvas.moveto(guidance[i], x_values[i]-mark_bound/2, mark_bound/2)
         canvas.moveto(dist[i], x_values[i]+20, mark_bound+5)
         look_y[i] = look_y[i] - (y_boundary + (2*overflow))

      #Top overflow
      if look_y[i] <= -(overflow):
         canvas.moveto(guidance[i], x_values[i]-mark_bound/2, y_boundary-1.5*mark_bound)
         canvas.moveto(dist[i], x_values[i]+20, y_boundary+5)
         look_y[i] = look_y[i] + (y_boundary + (2*overflow))


   ## Modifiyng the speed at which the marker travels
   ## if the point to get to is outside of horizontal boundaries then marker will 
   ## stop moving in out of bounds direction

      if (x_values[i] <= mark_bound and look_x[i] <=mark_bound) or (x_values[i] >= x_boundary-mark_bound and look_x[i] >= x_boundary-mark_bound):
         xspeeds[i] = 0
         if (x_values[i] <= mark_bound and look_x[i] <=mark_bound):
            canvas.moveto(guidance[i], -mark_bound/2, y_values[i]-mark_bound/2)
            canvas.moveto(dist[i], 20, y_values[i]+5)
         else:
            canvas.moveto(guidance[i], x_boundary-mark_bound/2, y_values[i]-mark_bound/2)
            canvas.moveto(dist[i], x_boundary+20, y_values[i]+5)
      ## Otherwise it will gradually speed up and slow down with distance
      else:
         xspeeds[i] = (look_x[i] - x_values[i])/50
      ## if the point to get to is outside of vertical boundaries then marker will 
      ## stop moving in out of bounds direciton
      if (y_values[i] <= mark_bound and look_y[i] <= mark_bound) or (y_values[i] >= y_boundary-mark_bound and look_y[i] >= y_boundary-mark_bound):
         yspeeds[i] = 0
         if (y_values[i] <= mark_bound and look_y[i] <= mark_bound):
            canvas.moveto(guidance[i], x_values[i]-mark_bound/2, -mark_bound/2)
            canvas.moveto(dist[i], x_values[i]+20, 5)
         else:
            canvas.moveto(guidance[i], x_values[i]-mark_bound/2, y_boundary-mark_bound/2)
            canvas.moveto(dist[i], x_values[i]+20, y_boundary+5)
      ## Otherwise it will gradually speed up and slow down with distance
      else:
         yspeeds[i] = (look_y[i] - y_values[i])/50
   

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


      if ((mark_bound - edge_margin <= x_values[i] <= x_boundary - mark_bound + edge_margin) and not (look_x[i] -5 < x_values[i] < look_x[i] + 5)):
         #move image in x direction
         canvas.move(guidance[i], xspeeds[i], 0)
         canvas.move(dist[i], xspeeds[i], 0)
         (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance[i])
         x_values[i] = (leftPos + rightPos)/2
      elif x_values[i] > x_boundary - mark_bound:
         x_values[i] = x_boundary - mark_bound
      elif x_values[i] < mark_bound:
         x_values[i] = mark_bound

      if ((mark_bound <= y_values[i] <= y_boundary - mark_bound) and not (look_y[i] -5 < y_values[i] < look_y[i] + 5)):
         #move image in x direction
         canvas.move(guidance[i], 0, yspeeds[i])
         canvas.move(dist[i], 0, yspeeds[i])
         (leftPos, topPos, rightPos, bottomPos) = canvas.bbox(guidance[i])
         y_values[i] = (topPos + bottomPos)/2
      elif y_values[i] > y_boundary - mark_bound:
         y_values[i] = y_boundary - mark_bound
      elif y_values[i] < mark_bound:
         y_values[i] = mark_bound


   canvas.after(5, moveMark)


window = tk.Tk()

#Movement
window.bind("<w>",look_up)
window.bind("<s>",look_down)
window.bind("<a>",look_left)
window.bind("<d>",look_right)
# window.bind("<Left>",move_left)
# window.bind("<Right>",move_right)
window.bind("<space>",deleteImage)
window.bind("<Button-1>", click)
window.bind("<b>", blue)
window.bind("<g>", green)
window.bind("<r>", red)
window.bind("<y>", yellow)

#Counting
window.bind("<Up>",count_up)
window.bind("<Down>",count_down)



canvas = tk.Canvas(window,width=x_boundary,height=y_boundary)
canvas.pack()
canvas.tab = [{} for q in range(50)]
canvas.focus_set()

##No longer using had a visual background that interfered with marker image
# dist_lab = tk.Label(window, fg='black')
# dist_lab.configure(text = f'{distance} meters')
# dist_lab.pack()
# obj_dist = canvas.create_window(x_start+20, y_start, window=dist_lab, anchor='nw') 

#Did NOT WORK
# dist_lab.place(100,100,width=50)

#dist = canvas.create_text(x_start+20, y_start+5, text=f'{distance} m', font='SegoeUI 13',fill='black', anchor='nw')

"""
x_pos = tk.Label(window, fg='black')
x_pos.configure(text = f'current x value: {x_value}')
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

#Load an image in the script
img= (Image.open("marker.png"))
blue = (Image.open("marker_blue.png"))
green = (Image.open("marker_green.png"))
red = (Image.open("marker_red.png"))
yellow = (Image.open("marker_yellow.png"))
#Resize the Image using resize method
marker_img= img.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)
marker_blue = blue.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)
marker_green = green.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)
marker_red = red.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)
marker_yellow = yellow.resize((mark_bound,mark_bound), Image.Resampling.LANCZOS)

# photoimage = ImageTk.PhotoImage(marker_img)
# guidance = canvas.create_image(x_start,y_start,image=photoimage,anchor='center')

#canvas.create_text(3, 120, text=f'test skull: {distance}', font='SegoeUI 13',fill='black', anchor='nw')

canvas.after(20, moveMark)
window.mainloop()