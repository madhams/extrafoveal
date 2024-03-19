# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple GPS module demonstration.
# Will wait for a fix and print a message every second with the current location
# and other details.
import time
import board
import busio
import adafruit_gps
import math
# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
# uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)

# for a computer, use the pyserial library for uart access
import serial
import csv
import os
from Mapbox_functions import find_bearing_angle, haversine_distance
os.system("sudo chmod 666 /dev/ttyS0")
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)

# If using I2C, we'll create an I2C interface to talk to using default pins
# i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# Create a GPS module instance.
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial
# gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)  # Use I2C interface

# Initialize the GPS module by changing what data it sends and at what rate.
# These are NMEA extensions for PMTK_314_SET_NMEA_OUTPUT and
# PMTK_220_SET_NMEA_UPDATERATE but you can send anything from here to adjust
# the GPS module behavior:
#   https://cdn-shop.adafruit.com/datasheets/PMTK_A11.pdf

# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# Turn on just minimum info (RMC only, location):
# gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn off everything:
# gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn on everything (not all of it is parsed!)
# gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b"PMTK220,1000")
# Or decrease to once every two seconds by doubling the millisecond value.
# Be sure to also increase your UART timeout above!
# gps.send_command(b'PMTK220,2000')
# You can also speed up the rate, but don't go too fast or else you can lose
# data during parsing.  This would be twice a second (2hz, 500ms delay):
# gps.send_command(b'PMTK220,500')

# Main loop runs forever printing the location, etc. every second.
last_print = time.monotonic()

counter = 0
ave = 0
prev_lat = 0
prev_long = 0
distance = 0
ang = 0
coord_dict = dict()
#coord_list = [(-95.403431, 29.718996), (-95.404681, 29.719268), (-95.403750, 29.719614), (-95.403431, 29.718996)]  # GPS coordinates in route
#coord_list = [(-95.398920, 29.722100), (-95.398496, 29.722080), (-95.398790, 29.721940), (-95.398653, 29.721818)]
intro_route = [(-95.400912, 29.720961), (-95.401456, 29.720913)]
test_route = [(-95.403833, 29.719431), (-95.403691, 29.719109), (-95.404638, 29.719074), (-95.405190, 29.719272),
              (29.719371, -95.406200), (-95.406183, 29.719104), (-95.405547, 29.719131), (-95.405846, 29.718826),
              (-95.404945, 29.718698), (-95.403822, 29.719461)]
edge_route = [(-95.403822, 29.719438), (-95.403652, 29.719109), (-95.404496, 29.718789), (-95.404737, 29.719092),
              (-95.405066, 29.719748), (-95.405687, 29.719498), (-95.405202, 29.718651), (-95.404626, 29.718849),
              (-95.404719, 29.719124), (-95.403842, 29.719445), (-95.403652, 29.719109), (-95.403842, 29.719445)]
perim_route = [(-95.403847, 29.719427), (-95.404649, 29.719139), (-95.405105, 29.719737),
               (-95.405681, 29.719528), (-95.404488, 29.718815), (-95.403702, 29.719092)]
intro_field = [(-95.403847, 29.719427), (-95.404649, 29.719139), (-95.403847, 29.719427)]

# Put here a list of static coordinates to also display
obstacle_list = []
# Also list of what obstacles should be (integers)
obs_markers = ['path', 'danger']

# Set up so first obstacle is always the path

coord_dict['intro'] = intro_route
coord_dict['test'] = test_route
coord_dict['edge'] = edge_route
coord_dict['perim'] = perim_route
coord_dict['intro_edge'] = intro_field
coord_list = coord_dict['intro']
coord_idx = 0
obstacle_list.append(coord_list[coord_idx])
filename = 'gps_route_info.csv'
obs_file = 'gps_obs_info.csv'
complete_flag = False

def write_csv(fname, data):
    with open(fname, 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONE, delimiter=',')
        writer.writerows(data)
    return None


while True:
    # Make sure to call gps.update() every loop iteration and at least twice
    # as fast as data comes from the GPS unit (usually every second).
    # This returns a bool that's true if it parsed new data (you can ignore it
    # though if you don't care and instead look at the has_fix property).
    gps.update()
    # Every second print out current location details if there's a fix.
    current = time.monotonic()
    if current - last_print >= 2:
        last_print = current
        if gps.has_fix:
            obs_angs = []
            obs_dist = []
            gps_coord = (gps.longitude, gps.latitude)
            distance = haversine_distance(gps_coord, obstacle_list[0])
            ang = 360 - math.degrees(find_bearing_angle(gps_coord, obstacle_list[0])) % 360
            obs_angs.append(ang)
            obs_dist.append(dist)
            for i in range(1, len(obstacle_list)):
                tmp_ang = 360 - math.degrees(find_bearing_angle(gps_coord, obstacle_list[i])) % 360
                tmp_dist = haversine_distance(gps_coord, obstacle_list[i])
                obs_angs.append(tmp_ang)
                obs_dist.append(tmp_dist)
            print(f'Distance is {distance}, angle is {ang}')
            print(f'Coord index is {coord_idx}')
            if distance < 7 and coord_idx != len(coord_list) - 1:
                coord_idx += 1
                obstacle_list[0] = coord_list[coord_idx]
            data = [[distance, ang, coord_idx, len(coord_list)]]
            write_csv(filename, data)
            if len(obs_angs) == len(obs_dist):
                write_csv(obs_file, [obs_angs, obs_dist, obs_markers])
