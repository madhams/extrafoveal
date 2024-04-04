import zmq
from msgpack import loads

'''
For calibrating the gaze mapping to AR display.
Look at center point of AR display, fixation value will serve as calibration value for eyefunction program.
'''

# World-view dimensions
x_dim, y_dim = 800, 600

# Network setup
context = zmq.Context()
# open a req port to talk to pupil
addr = "127.0.0.1"  # remote ip or localhost
req_port = "50020"  # same as in the pupil remote gui
req = context.socket(zmq.REQ)
req.connect("tcp://{}:{}".format(addr, req_port))
# ask for the sub port
req.send_string("SUB_PORT")
sub_port = req.recv_string()

# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://{}:{}".format(addr, sub_port))
sub.setsockopt_string(zmq.SUBSCRIBE, 'fixations')

print("Connected to Pupil Core. Waiting for gaze data...")

smooth_x, smooth_y = 0.5, 0.5

while True:
    topic = sub.recv_string()
    msg = sub.recv()
    msg = loads(msg, raw=False)
    my_gaze = msg['norm_pos']

    if my_gaze != "None":
        x,y = my_gaze
        y = 1 - y
        x *= 800
        y *= 600
        x = round(x)
        y = round(y)
        fixation = (x, y)
        
        print('Fixation detected (x,y): ', x, ' ',y)

