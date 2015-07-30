import cv2
import copy
import sys
import collections
import logWrite

frame_metadata = {}
ROIs = set()
is_mouse_down = false

def on_mouse(event, x, y, flags, frame):
    frameRect = copy.copy(frame)
    global start_position
    is_mouse_down = true
    if event == cv2.cv.CV_EVENT_LBUTTONDOWN:
        ROIs.add((x/4, y/4))
        for ROI in ROIs:
            cv2.rectangle(frameRect, ROI, ROI, (0,0,255), 1)
        frameRect = cv2.resize(frameRect, (0,0), fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frameRect)

    elif event == cv2.cv.CV_EVENT_MOUSEMOVE:
        if (is_mouse_down == true):
            ROIs.add((x/4, y/4))
            for ROI in ROIs:
                cv2.rectangle(frameRect, ROI, ROI, (0,0,255), 1)
            frameRect = cv2.resize(frameRect, (0,0), fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
            cv2.imshow('frame',frameRect)

    elif event == cv2.cv.CV_EVENT_LBUTTONUP:
        is_mouse_down = false

    elif event == cv2.cv.CV_EVENT_RBUTTONDOWN:
        #print 'End Right Mouse Position: '+str(x)+', '+str(y)
        ROIs.clear()
        frameRect = cv2.resize(frameRect, (0,0), fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frameRect)

def main(argv):
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

        frame = cv2.resize(frame, (0,0), fx=4, fy=4, interpolation=cv2.INTER_NEAREST)

        cv2.imshow('frame',frame)

        k=-1
        while k not in (27, ord('u'), ord('n'), ord('s'), 2490368, 2621440, 2555904):
            k = cv2.waitKey(0)
            print str(k) + " was pressed"

        if k==27:    # Esc key to stop
            break
        elif k==ord('u'):
            ROIs.clear()
            frame_metadata[int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))] = "undefined"
            print "undefined"
        elif k==ord('n'):
            ROIs.clear()
            frame_metadata[int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))] = "nothing interesting"
            print "nothing interesting"
        elif k==2490368: # up arrow for fast reverse
            cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)) - 25)
        elif k==2621440: # down arrow for fast forward
            cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)) + 23)
        elif k==2555904: # right arrow for next frame
            pass

        if len(ROIs) > 0:
            frame_metadata[int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))] = tuple(ROIs)
   
    log.write(collections.OrderedDict(sorted(frame_metadata.items(), key=lambda t: t[0])))
    log.close()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
   main(sys.argv[1:])