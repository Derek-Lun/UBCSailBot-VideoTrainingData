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
selected_area = None
highlighted_area = None
brush_size = 1

def load_ROIs(ROIs_):
    global ROIs

    print "ROIS is", ROIs_

    if not isinstance(ROIs_, tuple):
        print "not a set"
        return

    print "load frame data"
    for ROI in ROIs_:
        ROIs.add(ROI)
        cv2.rectangle(selected_area, ROI, ROI, (0,0,255), 1)

def select_pixels(x, y):
    global ROI
    global selected_area
    global brush_size

    for x_ in xrange(x-brush_size+1, x+brush_size):
        for y_ in xrange(y-brush_size+1, y+brush_size):
            ROIs.add((x_, y_))
            cv2.rectangle(selected_area, (x_, y_), (x_, y_), (0,0,255), 1)

def highlight_pixels(x, y):
    global k
    global highlighted_area

    for x_ in xrange(x-brush_size+1, x+brush_size):
        for y_ in xrange(y-brush_size+1, y+brush_size):
            cv2.rectangle(highlighted_area, (x_, y_), (x_, y_), (0,255,0), 1)

def on_mouse(event, x, y, flags, frame):
    global is_mouse_down
    global selected_area
    global highlighted_area

    frameRect = copy.copy(frame)
    
    if event == cv2.cv.CV_EVENT_LBUTTONDOWN:
        is_mouse_down = True
        select_pixels(x/constant.RESCALE_FACTOR, y/constant.RESCALE_FACTOR)
        frameRect = cv2.addWeighted(frameRect, 0.7, selected_area, 0.3, 0)
        frameRect = cv2.resize(frameRect, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frameRect)

    elif event == cv2.cv.CV_EVENT_LBUTTONUP:
        is_mouse_down = False

    elif event == cv2.cv.CV_EVENT_MOUSEMOVE:
        if (is_mouse_down == True):
            select_pixels(x/constant.RESCALE_FACTOR, y/constant.RESCALE_FACTOR)
            frameRect = cv2.addWeighted(frameRect, 0.7, selected_area, 0.3, 0)
            frameRect = cv2.resize(frameRect, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
            cv2.imshow('frame',frameRect)
        else:
            highlighted_area = copy.copy(selected_area)
            highlight_pixels(x/constant.RESCALE_FACTOR, y/constant.RESCALE_FACTOR)
            frameRect = cv2.addWeighted(frameRect, 0.7, highlighted_area, 0.3, 0)
            frameRect = cv2.resize(frameRect, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
            cv2.imshow('frame',frameRect)

    elif event == cv2.cv.CV_EVENT_RBUTTONDOWN:
        ROIs.clear()
        height, width, channels = frame.shape
        selected_area = np.zeros((height, width, 3), np.uint8)

        frameRect = cv2.addWeighted(frameRect, 0.7, selected_area, 0.3, 0)
        frameRect = cv2.resize(frameRect, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frameRect)

def main(argv):
    global selected_area
    global brush_size
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
        selected_area = np.zeros((height, width, 3), np.uint8)
        try:
            load_ROIs(frame_metadata[int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))])
        except Exception as e:
            print e

        cv2.putText(frame,
        str(int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))),
        (6, 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 0, 0))

        cv2.namedWindow('frame')
        cv2.cv.SetMouseCallback('frame', on_mouse, frame)

        print highlighted_area

        frame = cv2.addWeighted(frame, 0.7, selected_area, 0.3, 0)
        frame = cv2.resize(frame, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frame)

        k = 0
        while k not in (chr(27), 'u', 'n', 's', 'w', 's', 'a', 'd'):
            k = chr(cv2.waitKey(0) & 255)
            try:
                brush_size = int(k)
            except:
                print k + " was pressed"

        if len(ROIs) > 0:
            frame_metadata[int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))] = tuple(ROIs)
            
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

    log.write(collections.OrderedDict(sorted(frame_metadata.items(), key=lambda t: t[0])))
    log.close()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
   main(sys.argv[1:])