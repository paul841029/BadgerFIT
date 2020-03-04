from tkinter import *
from PIL import Image
from PIL import ImageTk
import cv2, threading, os, time
from threading import Thread
from os import listdir
from os.path import isfile, join

import dlib
from imutils import face_utils, rotate_bound
import math


def put_sprite(num):
    global SPRITES, BTNS
    SPRITES[num] = (1 - SPRITES[num]) 
    # if SPRITES[num]:
    #     BTNS[num].config(relief=SUNKEN)
    # else:
    #     BTNS[num].config(relief=RAISED)

def draw_sprite(frame, sprite, x_offset, y_offset):
    (h,w) = (sprite.shape[0], sprite.shape[1])
    (imgH,imgW) = (frame.shape[0], frame.shape[1])

    if y_offset+h >= imgH:
        sprite = sprite[0:imgH-y_offset,:,:]

    if x_offset+w >= imgW:
        sprite = sprite[:,0:imgW-x_offset,:]

    if x_offset < 0: 
        sprite = sprite[:,abs(x_offset)::,:]
        w = sprite.shape[1]
        x_offset = 0

    for c in range(3):
            frame[y_offset:y_offset+h, x_offset:x_offset+w, c] =  \
            sprite[:,:,c] * (sprite[:,:,3]/255.0) +  frame[y_offset:y_offset+h, x_offset:x_offset+w, c] * (1.0 - sprite[:,:,3]/255.0)
    return frame

def adjust_sprite2head(sprite, head_width, head_ypos, ontop = True):
    (h_sprite,w_sprite) = (sprite.shape[0], sprite.shape[1])
    factor = 1.0*head_width/w_sprite
    sprite = cv2.resize(sprite, (0,0), fx=factor, fy=factor)
    (h_sprite,w_sprite) = (sprite.shape[0], sprite.shape[1])

    y_orig =  head_ypos-h_sprite if ontop else head_ypos 
    if (y_orig < 0):
            sprite = sprite[abs(y_orig)::,:,:] 
            y_orig = 0
    return (sprite, y_orig)


def apply_sprite(image, path2sprite,w,x,y, angle, ontop = True):
    sprite = cv2.imread(path2sprite,-1)
    sprite = rotate_bound(sprite, angle)
    (sprite, y_final) = adjust_sprite2head(sprite, w, y, ontop)
    image = draw_sprite(image,sprite,x, y_final)

def calculate_inclination(point1, point2):
    x1,x2,y1,y2 = point1[0], point2[0], point1[1], point2[1]
    incl = 180/math.pi*math.atan((float(y2-y1))/(x2-x1))
    return incl


def calculate_boundbox(list_coordinates):
    x = min(list_coordinates[:,0])
    y = min(list_coordinates[:,1])
    w = max(list_coordinates[:,0]) - x
    h = max(list_coordinates[:,1]) - y
    return (x,y,w,h)

def detectUpperBody(image):
    cascadePath = "/home/admin1/Documents/Flipkart_Hackathon/BodyDetection/haarcascades_cuda/haarcascade_upperbody.xml"
    result = image.copy()
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cascadePath)
    Rect = cascade.detectMultiScale(imageGray, scaleFactor=1.1, minNeighbors=1, minSize=(1,1)) 
    if len(Rect) <= 0:
	    return False	
    else:
	    return Rect

def get_face_boundbox(points, face_part):
    if face_part == 1:
        (x,y,w,h) = calculate_boundbox(points[17:22])
    elif face_part == 2:
        (x,y,w,h) = calculate_boundbox(points[22:27]) 
    elif face_part == 3:
        (x,y,w,h) = calculate_boundbox(points[36:42])
    elif face_part == 4:
        (x,y,w,h) = calculate_boundbox(points[42:48])
    elif face_part == 5:
        (x,y,w,h) = calculate_boundbox(points[29:36])
    elif face_part == 6:
        (x,y,w,h) = calculate_boundbox(points[0:17])
    elif face_part == 7:
        # (x,y,w,h) = calculate_boundbox(points[48:68]) #mouth
        (x,y,w,h) = calculate_boundbox(points[1:5])
    elif face_part == 8:
        (x,y,w,h) = calculate_boundbox(points[12:16])
    return (x,y,w,h)

image_path = ''

def add_sprite(img):
    global image_path
    image_path = img
    # print(img.rsplit('/',1))
    put_sprite(int(img.rsplit('/',1)[0][-1]))
    
#Principal Loop where openCV (magic) ocurs
def cvloop(run_event):
    global panelA
    global SPRITES
    global image_path
    i = 0
    video_capture = cv2.VideoCapture(0) #read from webcam
    (x,y,w,h) = (0,0,10,10) #whatever initial values

    #Filters path
    detector = dlib.get_frontal_face_detector()

    model = "data/shape_predictor_68_face_landmarks.dat"
    predictor = dlib.shape_predictor(model) # link to model: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

    while run_event.is_set(): 
        ret, image = video_capture.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = detector(gray, 0)

        for face in faces: 
            (x,y,w,h) = (face.left(), face.top(), face.width(), face.height())

            shape = predictor(gray, face)
            shape = face_utils.shape_to_np(shape)
            incl = calculate_inclination(shape[17], shape[26]) #inclination based on eyebrows

            # condition to see if mouth is open
            is_mouth_open = (shape[66][1] -shape[62][1]) >= 10 #y coordiantes of landmark points of lips

            if SPRITES[0]:
            
                apply_sprite(image,image_path,w,x,y+40, incl, ontop = True)
        

            if SPRITES[1]:
                (x1,y1,w1,h1) = get_face_boundbox(shape, 6)
                apply_sprite(image,image_path,w1,x1,y1+275, incl)


            if SPRITES[3]:
                (x3,y3,_,h3) = get_face_boundbox(shape, 1)
                apply_sprite(image,image_path,w,x,y3, incl, ontop = False)

    
            (x0,y0,w0,h0) = get_face_boundbox(shape, 6) #bound box of mouth

            if SPRITES[4]:
                (x3,y3,w3,h3) = get_face_boundbox(shape, 7) #nose
                apply_sprite(image, image_path,w3,x3-20,y3+25, incl)
                (x3,y3,w3,h3) = get_face_boundbox(shape, 8) #nose
                apply_sprite(image, image_path,w3,x3+20,y3+25, incl)
            
            if SPRITES[5]:
                findRects = []
                upperPath = "/home/admin1/Documents/Flipkart_Hackathon/BodyDetection/haarcascades_cuda/haarcascade_upperbody.xml"
                imageGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                upperCascade = cv2.CascadeClassifier(upperPath)
                upperRect = upperCascade.detectMultiScale(imageGray, scaleFactor=1.1, minNeighbors=1, minSize=(1,1)) 

                if len(upperRect) > 0:
                    findRects.append(upperRect[0])
                    print(findRects)
                
                for obj in findRects:
                    print(obj)
                    # img = cv2.rectangle(img, (obj[0],obj[1]), (obj[0]+obj[2], obj[1]+obj[3]), (0, 255, 0), 2)
                    draw_sprite(image,obj[0],obj[1])

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        panelA.configure(image=image)
        panelA.image = image

    video_capture.release()

# Initialize GUI object
root = Tk()
root.title("E-Dressing- Face")
this_dir = os.path.dirname(os.path.realpath(__file__))
btn1 = None

def try_on(image_path):
    btn1 = Button(root, text="Try it ON", command = lambda:add_sprite(image_path))
    btn1.pack(side="top", fill="both", expand="no", padx="5", pady="5")
panelA = Label(root)
panelA.pack( padx=10, pady=10)

SPRITES = [0,0,0,0,0,0]
BTNS = [btn1]

try_on(sys.argv[1])
run_event = threading.Event()
run_event.set()
action = Thread(target=cvloop, args=(run_event,))
action.setDaemon(True)
action.start()

def terminate():
        global root, run_event, action
        run_event.clear()
        time.sleep(1)
        root.destroy()

root.protocol("WM_DELETE_WINDOW", terminate)
root.mainloop() 