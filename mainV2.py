import cv2
import numpy as np
import copy
import sys
import collections
import logWrite
import constant

frame_metadata = {}
ROIs = set()
is_mouse_down = False
k = -1
highlighted_area = None

def num_key_lookup(num_key):
    return { '1' : 1,
        '2' : 2,
        '3' : 3,
        '4' : 4,
        '5' : 5,
        '6' : 6,
        '7' : 7,
        '8' : 8,
        '9' : 9,
    }.get(num_key, 0)

def select_pixels(x, y):
    global k
    global highlighted_area

    n = num_key_lookup(k)
    for x_ in xrange(x-n, x+n+1):
        for y_ in xrange(y-n, y+n+1):
            ROIs.add((x_, y_))
            cv2.rectangle(highlighted_area, (x_, y_), (x_, y_), (0,0,255), 1)

def on_mouse(event, x, y, flags, frame):
    global is_mouse_down
    global highlighted_area

    frameRect = copy.copy(frame)
    
    if event == cv2.cv.CV_EVENT_LBUTTONDOWN:
        is_mouse_down = True
        select_pixels(x/constant.RESCALE_FACTOR, y/constant.RESCALE_FACTOR)
        frameRect = cv2.addWeighted(frameRect, 0.7, highlighted_area, 0.3, 0)
        frameRect = cv2.resize(frameRect, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frameRect)

    elif event == cv2.cv.CV_EVENT_LBUTTONUP:
        is_mouse_down = False

    elif event == cv2.cv.CV_EVENT_MOUSEMOVE:
        if (is_mouse_down == True):
            select_pixels(x/constant.RESCALE_FACTOR, y/constant.RESCALE_FACTOR)
            frameRect = cv2.addWeighted(frameRect, 0.7, highlighted_area, 0.3, 0)
            frameRect = cv2.resize(frameRect, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
            cv2.imshow('frame',frameRect)

    elif event == cv2.cv.CV_EVENT_RBUTTONDOWN:
        ROIs.clear()
        height, width, channels = frame.shape
        highlighted_area = np.zeros((height, width, 3), np.uint8)

        frameRect = cv2.addWeighted(frameRect, 0.7, highlighted_area, 0.3, 0)
        frameRect = cv2.resize(frameRect, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frameRect)

def main(argv):
    global k
    global highlighted_area

    if len(sys.argv) != 2:
        print "Usage: main.py <file name>"
        sys.exit()

    cap = cv2.VideoCapture(sys.argv[1])

    if not cap.isOpened():
      print "Error when reading image file"

    log = logWrite.logWrite()
    log.new(str(sys.argv[1]))

    while(cap.isOpened()):
        ROIs.clear()
        ret, frame = cap.read()

        if int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)) == cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
            break

        height, width, channels = frame.shape
        highlighted_area = np.zeros((height, width, 3), np.uint8)

        cv2.putText(frame,
        str(int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))),
        (6, 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0))

        cv2.namedWindow('frame')
        cv2.cv.SetMouseCallback('frame', on_mouse, frame)

        frame = cv2.addWeighted(frame, 0.7, highlighted_area, 0.3, 0)
        frame = cv2.resize(frame, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frame)

        k = 0
        while k not in (chr(27), 'u', 'n', 's', 'w', 's', 'a', 'd'):
            k = chr(cv2.waitKey(0) & 255)
            print k + " was pressed"

        if k==chr(27):    # Esc key to stop
            break
        elif k=='u':
            ROIs.clear()
            frame_metadata[int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))] = "UNCERTAIN"
            print "UNCERTAIN"
        elif k=='n':
            ROIs.clear()
            frame_metadata[int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))] = "EMPTY"
            print "EMPTY"
        elif k=='w':
            cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)) - constant.FRAME_SKIP - 1)
        elif k=='s':
            cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)) + constant.FRAME_SKIP - 1)
        elif k=='a':
            cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)) - 2)
        elif k=='d':
            pass

        if len(ROIs) > 0:
            frame_metadata[int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))] = tuple(ROIs)
   
    log.write(collections.OrderedDict(sorted(frame_metadata.items(), key=lambda t: t[0])))
    log.close()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
   main(sys.argv[1:])