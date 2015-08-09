import cv2
import numpy as np
import copy, sys, os, collections
import logWrite
import constant

frame_metadata = {}
ROIs = set()
is_mouse_down = False
selected_area = None
highlighted_area = None
brush_size = 1

def load_ROIs(ROIs_):
    if not isinstance(ROIs_, tuple):
        return

    for ROI in ROIs_:
        ROIs.add(ROI)
        cv2.rectangle(selected_area, ROI, ROI, (0,0,255), 1)

def select_pixels(x, y):
    for x_ in xrange(x-brush_size+1, x+brush_size):
        for y_ in xrange(y-brush_size+1, y+brush_size):
            ROIs.add((x_, y_))
            cv2.rectangle(selected_area, (x_, y_), (x_, y_), (0,0,255), 1)

def highlight_pixels(x, y):
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

def is_frame_file(f):
    return f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg')

def read_frames_from_video(cap):
    while cap.isOpened:
        success, frame = cap.read()
        if success:
            yield frame
        else:
            break

def get_frames(frame_location):
    frames = [0,]
    is_dir = os.path.isdir(frame_location)

    if is_dir:
        frames = [cv2.imread(os.path.join(frame_location, f)) for f in os.listdir(frame_location) if is_frame_file(f)]
    else:
        cap = cv2.VideoCapture(frame_location)
        if not cap.isOpened():
            print "Error: failed to read video file ", frame_location
            sys.exit()
        frames = [f for f in read_frames_from_video(cap)]
        cap.release

    return frames

def get_new_frame_num(offset):
    global max_frame_num
    global current_frame_num

    new_frame_num = current_frame_num + offset

    if new_frame_num < 1:
        new_frame_num = 1
    elif new_frame_num > max_frame_num:
        new_frame_num = max_frame_num

    return new_frame_num    

def main(argv):
    global brush_size
    global selected_area
    global highlighted_area

    global max_frame_num
    global current_frame_num

    if len(sys.argv) != 2:
        print "Usage: main.py <frame location>"
        sys.exit()

    frame_location = sys.argv[1]
    frames = get_frames(frame_location)
    max_frame_num = len(frames) - 1

    if len(frames) == 0:
        print "Error: failed to read frames from ", frame_location
        sys.exit()

    log = logWrite.logWrite()
    log.new(str(sys.argv[1]))

    current_frame_num = 1

    while True:
        ROIs.clear()
        
        frame = frames[current_frame_num]

        try:
            height, width, channels = frame.shape
        except:
            print current_frame_num
        highlighted_area = np.zeros((height, width, 3), np.uint8)
        selected_area = np.zeros((height, width, 3), np.uint8)
        try:
            load_ROIs(frame_metadata[current_frame_num])
        except Exception as e:
            # print "Warning: Failure to load ROIs that were previously chosen for this frame."
            # print e
            pass

        cv2.putText(frame,
        str(current_frame_num),
        (6, 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 0, 0))

        cv2.namedWindow('frame')
        cv2.cv.SetMouseCallback('frame', on_mouse, frame)

        frame = cv2.addWeighted(frame, 0.7, selected_area, 0.3, 0)
        frame = cv2.resize(frame, (0,0), fx=constant.RESCALE_FACTOR, fy=constant.RESCALE_FACTOR, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('frame',frame)

        k = 0
        while k not in (chr(27), 'u', 'n', 's', 'w', 's', 'a', 'd', 'q'):
            k = chr(cv2.waitKey(0) & 255)
            try:
                brush_size = int(k)
            except:
                print k + " was pressed"

        if len(ROIs) > 0:
            frame_metadata[current_frame_num] = tuple(ROIs)
            
        if k==chr(27) or k=='q':    # Esc key or 'q' to stop
            break
        elif k=='u':
            ROIs.clear()
            frame_metadata[current_frame_num] = "UNCERTAIN"
            print "UNCERTAIN"
            current_frame_num = get_new_frame_num(1)
        elif k=='n':
            ROIs.clear()
            frame_metadata[current_frame_num] = "EMPTY"
            print "EMPTY"
            current_frame_num = get_new_frame_num(1)
        elif k=='w':
            current_frame_num = get_new_frame_num(-constant.FRAME_SKIP)
        elif k=='s':
            current_frame_num = get_new_frame_num(constant.FRAME_SKIP)
        elif k=='a':
            current_frame_num = get_new_frame_num(-1)
        elif k=='d':
            current_frame_num = get_new_frame_num(1)

    log.write(collections.OrderedDict(sorted(frame_metadata.items(), key=lambda t: t[0])))
    log.close()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(sys.argv[1:])