import zmq
from msgpack import loads
import numpy as np
import cv2


context = zmq.Context()
# open a req port to talk to pupil
addr = "168.5.184.207"  # remote ip or localhost
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


def has_new_data_available():
    # Returns True as long subscription socket has received data queued for processing
    return sub.get(zmq.EVENTS) & zmq.POLLIN

recent_world = None

while True:
    while has_new_data_available():
        topic, msg = recv_from_sub()
        if topic == "frame.world":
            recent_world = np.frombuffer(
                msg["__raw_data__"][0], dtype=np.uint8
            ).reshape(msg["height"], msg["width"], 3)

        if recent_world is not None:
            cv2.imshow("Frame",recent_world)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break