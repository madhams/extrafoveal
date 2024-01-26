import time
import board
import math
import adafruit_lsm303_accel
import adafruit_lis2mdl

# Need to use away from a laptop for best results even indoors
# Note that magnetoemeter fluctauate by ~ 3 degrees when in a steady state
def calibrate(magnetometer):
    # Find Hard-Iron calibration values, rotate along x/y axis to each extreme value
    # Leave flat for most accurate X/Y calibration, makes Z direction not effect angle
    start_time = time.monotonic()

    # calibration for magnetometer X (min, max), Y and Z
    hardiron_calibration = [[1000, -1000], [1000, -1000], [1000, -1000]]
    # Update the high and low extremes
    while time.monotonic() - start_time < 20:
        magval = magnetometer.magnetic
        print("Calibrating - X:{0:10.2f}, Y:{1:10.2f}, Z:{2:10.2f} uT".format(*magval))
        for i, axis in enumerate(magval):
            hardiron_calibration[i][0] = min(hardiron_calibration[i][0], axis)
            hardiron_calibration[i][1] = max(hardiron_calibration[i][1], axis)
    print("Calibration complete:")
    print("hardiron_calibration =", hardiron_calibration)
    return hardiron_calibration

def normalize(_magvals, hardiron_cal):
    ret = [0, 0, 0]
    for i, axis in enumerate(_magvals):
        minv, maxv = hardiron_cal[i]
        axis = min(max(minv, axis), maxv)  # keep within min/max calibration
        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100
    return ret

def run_compass(sensor, hard_iron_vals):
    mag_vals = sensor.magnetic
    norm_mag_vals = normalize(mag_vals, hard_iron_vals)
    return math.atan2(norm_mag_vals[1], norm_mag_vals[0]) * 180.0 / math.pi + 180

def run_compass_tilt(mag, accel, hard_iron_vals):
    # Need to normalize compass after tilt adjustment
    tmp_mag_vals = mag.magnetic
    mag_vals = normalize(tmp_mag_vals, hard_iron_vals)
    #mag_vals = tmp_mag_vals
    accel_vals = accel.acceleration
    r = math.sqrt(accel_vals[0]**2 + accel_vals[1]**2 + accel_vals[2]**2)
    roll_angle = math.asin(accel_vals[1] / r)
    pitch_angle = math.asin(accel_vals[0] / r)
    #roll_angle = math.atan2(accel_vals[1], accel_vals[2])
    #pitch_angle = math.atan2(-accel_vals[0], accel_vals[1] * math.sin(roll_angle) + accel_vals[2] * math.cos(roll_angle))
    xh = mag_vals[0] * math.cos(pitch_angle) + mag_vals[1] * math.sin(pitch_angle) * math.sin(roll_angle) - mag_vals[2] * math.cos(roll_angle) * math.sin(pitch_angle) # Horizontal x value
    yh = mag_vals[1] * math.cos(roll_angle) - mag_vals[2] * math.sin(roll_angle)
    #norm_x, norm_y, norm_z = normalize((xh, yh, mag_vals[2]), hard_iron_vals)
    #print(f"Xh = {xh}, Yh = {yh}")
    #print(f"Roll = {math.degrees(roll_angle)}, Pitch = {math.degrees(pitch_angle)}")
    #print(mag.magnetic)
    return math.atan2(yh, xh) * 180.0 / math.pi + 180, math.degrees(roll_angle), math.degrees(pitch_angle)

if __name__ == '__main__':
    i2c = board.I2C()
    magnetometer = adafruit_lis2mdl.LIS2MDL(i2c)
    accelerometer = adafruit_lsm303_accel.LSM303_Accel(i2c)
    hardiron_cal = calibrate(magnetometer)
    #hardiron_cal = [[-94.2, 38.55], [-71.25, 40.5], [-22.05, 85.35]]  # For outdoors on sundeck
    #hardiron_cal = [[-100.2, 55.35], [-84.75, 62.85], [-26.4, 124.95]]
    #hardiron_cal = [[-54.0, 25.8], [-62.25, 16.95], [-4.2, 40.949999999999996]]
    #hardiron_cal = [[-99.0, 82.2], [-139.35, 45.75], [-62.4, 120.89999999999999]]
    #hardiron_cal = [[-129.29999999999998, 84.0], [-129.29999999999998, 43.5], [-63.75, 114.0]] # For inside living room
    #hardiron_cal = [[-70.5, 29.7], [-58.8, 24.15], [-16.2, 82.35]]
    print(f"Hardiron cal vals = {hardiron_cal}")
    idx = 0
    ave_arr = []
    ave_arr1 = []
    while True:
#        print(f"Compass heading value after calibration is: {run_compass(magnetometer, hardiron_cal)}")
        accel_tmp = accelerometer.acceleration
        #print(f"Accelerometer values: x = {accel_tmp[0]}, y = {accel_tmp[1]}, z = {accel_tmp[2]}")
        #print(f"Compass heading value after calibration + tilt is: {run_compass_tilt(magnetometer, accelerometer, hardiron_cal)}")
        tmp = run_compass_tilt(magnetometer, accelerometer, hardiron_cal)
        if idx < 1: # and abs(math.degrees(tmp[1])) < 20 and abs(math.degrees(tmp[2])) < 20:
            ave_arr.append(tmp[0])
            ave_arr1.append(run_compass(magnetometer, hardiron_cal))
            idx += 1
            #print(idx)
        elif idx >= 1:
            idx = 0
            print(f"Aveage gaze angle is: {int(100 * sum(ave_arr) / 100)}")
            #print(f"Average without tilt is: {int(sum(ave_arr1) / 100)}")
            print(f"Roll = {tmp[1]}, Pitch = {tmp[2]}")
            ave_arr = []
            ave_arr1 = []


        time.sleep(0.5)
