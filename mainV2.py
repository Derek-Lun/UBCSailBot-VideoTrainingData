import cv2
import copy
import sys
import collections
import logWrite
import constant

frame_metadata = {}
ROIs = set()
is_mouse_down = False
k = -1

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
    n = num_key_lookup(k)
    for x_ in xrange(x-n, x+n+1):
        for y_ in xrange(y-n, y+n+1):
            ROIs.add((x_, y_))

def on_mouse(event, x, y, flags, frame):
    frameRect = copy.copy(frame)
    global start_position
    global is_mouse_down

    if event == cv2.cv.CV_EVENT_LBUTTONDOWN:
        is_mouse_down = True
        select_pixels(x/constant.RESCALE_FACTOR, y/constant.RESCALE_FACTOR)
        for ROI in ROIs:
            cv2.rectangle(frameRect, ROI, ROI, (0,0,255), 1)
        frameRect = cv2.resize(frameRect, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frameRect)

    elif event == cv2.cv.CV_EVENT_LBUTTONUP:
        is_mouse_down = False

    elif event == cv2.cv.CV_EVENT_MOUSEMOVE:
        if (is_mouse_down == True):
            select_pixels(x/constant.RESCALE_FACTOR, y/constant.RESCALE_FACTOR)
            for ROI in ROIs:
                cv2.rectangle(frameRect, ROI, ROI, (0,0,255), 1)
            frameRect = cv2.resize(frameRect, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
            cv2.imshow('frame',frameRect)

    elif event == cv2.cv.CV_EVENT_RBUTTONDOWN:
        #print 'End Right Mouse Position: '+str(x)+', '+str(y)
        ROIs.clear()
        frameRect = cv2.resize(frameRect, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frameRect)

def main(argv):
    global k
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

        cv2.putText(frame,
        str(int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))),
        (25, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        2,
        (255, 0, 0))

        cv2.namedWindow('frame')
        cv2.cv.SetMouseCallback('frame', on_mouse, frame)

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