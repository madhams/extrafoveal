import numpy as np
import argparse
# import imutils
import time
import cv2
import zmq
from msgpack import unpackb, packb, loads
import math
import time
import paramiko
from scp import SCPClient
import csv

'''
This version is for use with the AR display (no Pi). 
To test how the display looks when using the object recognition plus computer vision.
'''

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
# ssh = createSSHClient(server, port, user, password)

'''
Pupil Setup
'''

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

sub.setsockopt_string(zmq.SUBSCRIBE, 'frame.world')
sub.setsockopt_string(zmq.SUBSCRIBE, 'fixations')
# sub.setsockopt_string(zmq.SUBSCRIBE, 'gaze')


def recv_from_sub():
    """Recv a message with topic, payload.

    Topic is a utf-8 encoded string. Returned as unicode object.
    Payload is a msgpack serialized dict. Returned as a python dict.

    Any addional message frames will be added as a list
    in the payload dict with key: '__raw_data__' ."""
    topic = sub.recv_string()
    msg = sub.recv()
    msg = loads(msg, raw=False)
    extra_frames = []
    while sub.get(zmq.RCVMORE):
        extra_frames.append(sub.recv())
    if extra_frames:
        msg["__raw_data__"] = extra_frames
    return topic, msg


def object_identifier():
	frame = None

	FRAME_FORMAT = "bgr"

	'''
	CV Model
	'''
	# construct the argument parse and parse the arguments
	# ap = argparse.ArgumentParser()
	# ap.add_argument("-p", "--prototxt", required=True,
	# 	help="path to Caffe 'deploy' prototxt file")
	# ap.add_argument("-m", "--model", required=True,
	# 	help="path to Caffe pre-trained model")
	# ap.add_argument("-c", "--confidence", type=float, default=0.2,
	# 	help="minimum probability to filter weak predictions")
	# args = vars(ap.parse_args())


	CLASSES = ["aeroplane", "background", "bicycle", "bird", "boat",
			"bottle", "bus", "car", "cat", "Chair", "cow", "Dining Table",
			"dog", "horse", "motorbike", "Person", "Potted Plant", "sheep",
			"sofa", "train", "TV Monitor"]

	# Assigning random colors to each of the classes
	COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
	# The model from Caffe: MobileNetSSD_deploy.prototxt.txt; MobileNetSSD_deploy.caffemodel;
	print("[INFO] loading model...")
	# net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
	net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')

	# and initialize the FPS counter
	print("[INFO] starting video stream...")
	# vs = VideoStream(0).start()

	# warm up the camera for a couple of seconds
	time.sleep(2.0)

	# FPS: used to compute the (approximate) frames per second
	# Start the FPS timer
	# fps = FPS().start()

	frame_skip = 6  # Process every Xth frame
	frame_count = 0

	fixation = (0, 0)
	condition_met_time = None
	condition_met_time1 = None
	condition_met_time2 = None
	fixation_save = None
	last_fixation_label = None
	# loop over the frames from the video stream

	# On/Off variables
	HUD = 1
	Description = 0
	y_array = [0, 0, 0, 0, 0, 0]
	i = 0

	# Label location
	# Calibration Coordinates
	calibration = (390, 310)

	HUDy = calibration[1] - 180
	# buffer values refer to area of gaze that will display in center of HUD
	x_buffer = 100
	y_buffer = 70
	loc_dict = {0:(500,320), 1:(500,50), 2:(950,50), 3:(950,320), 4:(950,600), 5:(500,600), 6:(20,600), 7:(20,300), 8:(20,50)}

	while True:
		# grab the frame from the threaded video stream and resize it to have a maximum width of 400 pixels
		# vs is the VideoStream
		i = i + 1
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

				# xHUD *= 1920
				# yHUD *= 1080
				# x += 1
				y = 1 - y
				x *= 800
				y *= 600
				x = round(x)
				y = round(y)
				fixation = (x, y)
				
				print('Fixation detected (x,y): ', x, ' ',y)
				y_array.append(y)
				y_array = y_array[1:]

				

				current_time = time.time()

				if y < HUDy:
					if condition_met_time1 is None:
						# Start the timer
						print('Started looking down')
						condition_met_time1 = current_time
					
					elif current_time - condition_met_time1 < 1:
						print('waiting for 1.5 seconds to elapse')

					elif current_time - condition_met_time1 >= 1:
						# Condition has been met for 2 seconds
						if HUD == 1:
							HUD = 0
						else:
							HUD = 1
						
						print('HUD Updated: ,',HUD)
						
						time.sleep(2)
						# write text file, send it
						# scp = SCPClient(ssh.get_transport())
						# write_csv('eyefunction.csv', [[HUD, fixation_label, label_loc]])
						# scp.put('HUD_on_off.csv', '/home/foveal/Senior_Design/Compass/HUD_on_off.csv')

						# end_time = time.time()
						# print(end_time-start_time)

						# Reset the timer
						condition_met_time1 = None
					else:
						# Reset the timer if condition is not met
						# print('condition not met')
						condition_met_time1 = None
				else:
					# Reset the timer if condition is not met
					# print('condition not met')
					condition_met_time1 = None


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
			
		black_image = np.zeros((1920, 1080))

		if np.any(frame == None):
			print('no frame')
			continue

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
		bounds = [ [] for i in range(predictions.shape[2]) ]
		# bounds = np.zeros(predictions.shape[2])
		# # loop over the predictions
		for i in np.arange(0, predictions.shape[2]):
			# extract the confidence (i.e., probability) associated with the prediction
			# predictions.shape[2] = 100 here
			confidence = predictions[0, 0, i, 2]
			# Filter out predictions lesser than the minimum confidence level
			# Here, we set the default confidence as 0.2. Anything lesser than 0.2 will be filtered
			if confidence > 0.5: # args["confidence"]:
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
				bounds[i] = (startX, startY, endX, endY)
				# print(center_bb)
				# Get the label with the confidence score
				label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
				# print("Object detected: ", label)
				# Draw a rectangle across the boundary of the object
				
				y = startY - 15 if startY - 15 > 15 else startY + 15
				# Put a text outside the rectangular detection
				# Choose the font of your choice: FONT_HERSHEY_SIMPLEX, FONT_HERSHEY_PLAIN, FONT_HERSHEY_DUPLEX, FONT_HERSHEY_COMPLEX, FONT_HERSHEY_SCRIPT_COMPLEX, FONT_ITALIC, etc.
				# if HUD == 1:
					#cv2.rectangle(black_image, (startX, startY), (endX, endY), COLORS[idx], 2)
					#ncv2.putText(black_image, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

		if HUD == 1:
			if len(dist[dist>0]) > 0:
				non_zero_indices = np.flatnonzero(dist)
				min_non_zero_index = non_zero_indices[np.argmin(dist[non_zero_indices])]
				min_idx = int(predictions[0, 0, min_non_zero_index, 1])
				min_bounds = bounds[min_non_zero_index]
				# print(min_bounds)
				if fixation[0] > min_bounds[0]-25 and fixation[0] < min_bounds[2]+25 and fixation[1] > min_bounds[1]-25 and fixation[1] < min_bounds[3]+25:
					fixation_label = CLASSES[min_idx]
				else:
					fixation_label = 'n/a'
			else:
				fixation_label = 'n/a'
			
			current_time = time.time()

			if condition_met_time2 is None:
				cv2.putText(black_image, 'n/a', loc_dict[0], cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[0], 2)
			elif current_time - condition_met_time2 < 1.5:
				cv2.putText(black_image, fixation_save, loc_dict[label_loc], cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[0], 2)
			else:
				cv2.putText(black_image, fixation_save, loc_dict[label_loc], cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[0], 2)
				condition_met_time2 = None

			if fixation_label == last_fixation_label and fixation_label != 'n/a':
				if condition_met_time is None:
					# Start the timer
					# print('Object fixation detected')
					# cv2.putText(frame, fixation_label, fixation, cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[0], 2)
					condition_met_time = current_time
				
				# elif current_time - condition_met_time < 1.5:
				# 	# cv2.putText(frame, fixation_label, fixation, cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[0], 2)
				# 	print('waiting')

				elif current_time - condition_met_time >= 1.5:
					# Condition has been met for 2 seconds

					
					# print(fixation_label, ' detected and sent to Pi')
					# time.sleep(1.5)
					# write text file, send it
					
					if fixation[0] < calibration[0]+x_buffer and fixation[0] > calibration[0]-x_buffer and fixation[1] < calibration[1]+y_buffer and fixation[1] > calibration[1]-y_buffer:
						label_loc = 0
					elif fixation[0] < calibration[0]+x_buffer and fixation[0] > calibration[0]-x_buffer and fixation[1] <= calibration[1]-y_buffer:
						label_loc = 1
					elif fixation[0] >= calibration[0]+x_buffer and fixation[1] <= calibration[1]-y_buffer:
						label_loc = 2
					elif fixation[0] >= calibration[0]+x_buffer and fixation[1] < calibration[1]+y_buffer and fixation[1] > calibration[1]-y_buffer:
						label_loc = 3
					elif fixation[0] >= calibration[0]+x_buffer and fixation[1] >= calibration[1]+y_buffer:
						label_loc = 4
					elif fixation[0] < calibration[0]+x_buffer and fixation[0] > calibration[0]-x_buffer and fixation[1] >= calibration[1]+y_buffer:
						label_loc = 5
					elif fixation[0] <= calibration[0]-x_buffer and fixation[1] >= calibration[1]+y_buffer:
						label_loc = 6
					elif fixation[0] <= calibration[0]-x_buffer and fixation[1] < calibration[1]+y_buffer and fixation[1] > calibration[1]-y_buffer:
						label_loc = 7
					elif fixation[0] <= calibration[0]-x_buffer and fixation[1] <= calibration[1]-y_buffer:
						label_loc = 8

					cv2.putText(black_image, fixation_label, loc_dict[label_loc], cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[0], 2)
					
					# scp = SCPClient(ssh.get_transport())
					# write_csv('eyefunction.csv', [[HUD,fixation_label,label_loc]])
					# scp.put('Object_Label.csv', '/home/foveal/Senior_Design/Compass/Object_Label.csv')

					# end_time = time.time()
					# print(end_time-start_time)

					# Reset the timer
					condition_met_time = None
					condition_met_time2 = time.time()
					fixation_save = fixation_label
			else:
				# Reset the timer if condition is not met
				# print('condition not met')
				# cv2.putText(frame, 'n/a', fixation, cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[0], 2)
				condition_met_time = None

			last_fixation_label = fixation_label
			# # show the output frame
			# print(fixation)
			# cv2.circle(frame, fixation, radius=15, color=(0, 0, 255), thickness=5)
			cv2.putText(black_image, 'HUD ON', (500,420), cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[0], 2)
		else:
			cv2.putText(black_image, 'HUD OFF', (500,420), cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[0], 2)
		
		cv2.imshow("Frame", black_image)

		# Now, let's code this logic (just 3 lines, lol)
		key = cv2.waitKey(1) & 0xFF

		# Press 'q' key to break the loop
		if key == ord("q"):
			break


	cv2.destroyAllWindows()


object_identifier()