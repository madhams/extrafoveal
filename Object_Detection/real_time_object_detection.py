# How to run?: python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel
# python real_time.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import zmq
from msgpack import unpackb, packb
import math
import time
import paramiko
from scp import SCPClient
import csv

def write_csv(fname, data):
    with open(fname, 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONE, delimiter=',')
        writer.writerows(data)
    return None

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

server = 'raspberrypi.local'
server = '168.5.185.223'
port = 22
user = 'foveal'
password = 'extrafoveal'
ssh = createSSHClient(server, port, user, password)


'''
Pupil Setup
'''

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
# Filter by messages by stating string 'STRING'. '' receives all messages
# sub.setsockopt_string(zmq.SUBSCRIBE, 'gaze')
sub.setsockopt_string(zmq.SUBSCRIBE, 'frame.world')
sub.setsockopt_string(zmq.SUBSCRIBE, 'fixations')



def recv_from_sub():
    """Recv a message with topic, payload.

    Topic is a utf-8 encoded string. Returned as unicode object.
    Payload is a msgpack serialized dict. Returned as a python dict.

    Any addional message frames will be added as a list
    in the payload dict with key: '__raw_data__' .
    """
    topic = sub.recv_string()
    payload = unpackb(sub.recv(), raw=False)
    extra_frames = []
    while sub.get(zmq.RCVMORE):
        extra_frames.append(sub.recv())
    if extra_frames:
        payload["__raw_data__"] = extra_frames
    return topic, payload

frame = None

FRAME_FORMAT = "bgr"

'''
CV Model
'''
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak predictions")
args = vars(ap.parse_args())


CLASSES = ["aeroplane", "background", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# Assigning random colors to each of the classes
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
# The model from Caffe: MobileNetSSD_deploy.prototxt.txt; MobileNetSSD_deploy.caffemodel;
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# and initialize the FPS counter
print("[INFO] starting video stream...")
# vs = VideoStream(0).start()

# warm up the camera for a couple of seconds
time.sleep(2.0)

# FPS: used to compute the (approximate) frames per second
# Start the FPS timer
# fps = FPS().start()

frame_skip = 6  # Process every 5th frame
frame_count = 0

fixation = (0, 0)
condition_met_time = None
last_fixation_label = None
# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it to have a maximum width of 400 pixels
	# vs is the VideoStream

	topic, msg = recv_from_sub()
	# print(topic)


	if topic.startswith("frame.") and msg["format"] != FRAME_FORMAT:
		print(
			f"different frame format ({msg['format']}); "
			f"skipping frame from {topic}"
		)
		continue

	if topic == "fixations":
		fixation_norm_pos = msg['norm_pos'] 
		if fixation_norm_pos != "None":
			x, y = fixation_norm_pos
			# x += 1
			y = 1 - y
			x *= 800
			y *= 600
			x = round(x)
			y = round(y) 
			fixation = (x, y)
			# print('Fixation detected (x,y): ', x, ' ',y)


	if topic == "frame.world":
		
		frame_count += 1
		frame = np.frombuffer(
			msg["__raw_data__"][0], dtype=np.uint8
		).reshape(msg["height"], msg["width"], 3)
		if frame_count % frame_skip != 0:
			# cv2.imshow("Frame", frame)
			continue
			  # Skip this frame
	else:
		continue
		


	if np.any(frame == None):
		print('no frame')
		continue
	# frame = imutils.resize(frame, width=400)
	# print(frame.shape) # (225, 400, 3)
	# grab the frame dimensions and convert it to a blob
	# First 2 values are the h and w of the frame. Here h = 225 and w = 400
	(h, w) = frame.shape[:2]
	# Resize each frame
	resized_image = cv2.resize(frame, (300, 300))

	blob = cv2.dnn.blobFromImage(resized_image, (1/127.5), (300, 300), 127.5, swapRB=True)
	# print(blob.shape) # (1, 3, 300, 300)
	# pass the blob through the network and obtain the predictions and predictions
	net.setInput(blob) # net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
	# Predictions:
	predictions = net.forward()
	dist = np.zeros(predictions.shape[2])
	# # loop over the predictions
	for i in np.arange(0, predictions.shape[2]):
		# extract the confidence (i.e., probability) associated with the prediction
		# predictions.shape[2] = 100 here
		confidence = predictions[0, 0, i, 2]
		# Filter out predictions lesser than the minimum confidence level
		# Here, we set the default confidence as 0.2. Anything lesser than 0.2 will be filtered
		if confidence > 0.4: # args["confidence"]:
			# extract the index of the class label from the 'predictions'
			# idx is the index of the class label
			# E.g. for person, idx = 15, for chair, idx = 9, etc.
			idx = int(predictions[0, 0, i, 1])
			# then compute the (x, y)-coordinates of the bounding box for the object
			box = predictions[0, 0, i, 3:7] * np.array([w, h, w, h])
			# Example, box = [130.9669733   76.75442174 393.03834438 224.03566539]
			# Convert them to integers: 130 76 393 224
			(startX, startY, endX, endY) = box.astype("int")
			center_bb = [(startX+endX)/2.0, (startY+endY)/2.0]
			dist[i] = math.hypot(center_bb[0]-fixation[0], center_bb[1]-fixation[1])
			# print(center_bb)
			# Get the label with the confidence score
			label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
			# print("Object detected: ", label)
			# Draw a rectangle across the boundary of the object
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			# Put a text outside the rectangular detection
			# Choose the font of your choice: FONT_HERSHEY_SIMPLEX, FONT_HERSHEY_PLAIN, FONT_HERSHEY_DUPLEX, FONT_HERSHEY_COMPLEX, FONT_HERSHEY_SCRIPT_COMPLEX, FONT_ITALIC, etc.
			cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

	min_idx = int(predictions[0, 0, np.argmin(dist), 1])
	fixation_label = CLASSES[min_idx]
	current_time = time.time()

	if fixation_label == last_fixation_label:
		if condition_met_time is None:
			# Start the timer
			print('Object fixation detected')
			condition_met_time = current_time
		
		elif current_time - condition_met_time < 1:
			print('waiting for 2 seconds to elapse')

		elif current_time - condition_met_time >= 1:
			# Condition has been met for 2 seconds

			
			print(fixation_label, ' detected and sent to Pi')
			# time.sleep(1)
			# write text file, send it
			scp = SCPClient(ssh.get_transport())

			write_csv('Object_Label.csv', [[fixation_label]])
			scp.put('Object_Label.csv', '/home/foveal/Senior_Design/Compass/Object_Label.csv')

			# end_time = time.time()
			# print(end_time-start_time)

			# Reset the timer
			condition_met_time = None
	else:
		# Reset the timer if condition is not met
		# print('condition not met')
		condition_met_time = None

	last_fixation_label = CLASSES[min_idx]
	# # show the output frame
	cv2.circle(frame, fixation, radius=15, color=(0, 0, 255), thickness=5)
	cv2.imshow("Frame", frame)

	# Now, let's code this logic (just 3 lines, lol)
	key = cv2.waitKey(1) & 0xFF

	# Press 'q' key to break the loop
	if key == ord("q"):
		break


# Destroy windows and cleanup
cv2.destroyAllWindows()
# Stop the video stream
# vs.stop()

# In case you removed the opaque tape over your laptop cam, make sure you put them back on once finished ;)
# YAYYYYYYYYYY WE ARE DONE!