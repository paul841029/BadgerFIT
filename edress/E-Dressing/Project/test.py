from tkinter_scroll import *
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

ACTIVE_IMAGES=[0 for i in range(100)]
def put_sprite(num, k):
    global SPRITES, BTNS
    SPRITES[num] = (1 - SPRITES[num]) 
    if SPRITES[num]:
        ACTIVE_IMAGES[num] = k
        BTNS[num].config(relief=SUNKEN)
    else:
        BTNS[num].config(relief=RAISED)

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

def apply_sprite2feature(image, sprite_path, haar_filter, x_offset, y_offset, y_offset_image, adjust2feature, desired_width, x, y, w, h):
    sprite = cv2.imread(sprite_path,-1)
    (h_sprite,w_sprite) = (sprite.shape[0], sprite.shape[1])

    xpos = x + x_offset
    ypos = y + y_offset
    factor = 1.0*desired_width/w_sprite

    sub_img = image[y + y_offset_image:y+h,x:x+w,:]

    feature = apply_Haar_filter(sub_img, haar_filter, 1.3 , 10, 10)
    if len(feature)!=0:
        xpos, ypos = x, y + feature[0,1] #adjust only to feature in y axis (eyes)

        if adjust2feature:
            size_mustache = 1.2 #how many times bigger than mouth
            factor = 1.0*(feature[0,2]*size_mustache)/w_sprite
            xpos =  x + feature[0,0] - int(feature[0,2]*(size_mustache-1)//2) #centered respect to width
            ypos = y + y_offset_image + feature[0,1] - int(h_sprite*factor) #right on top

    sprite = cv2.resize(sprite, (0,0), fx=factor, fy=factor)
    image = draw_sprite(image,sprite,xpos,ypos)

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

def apply_Haar_filter(img, haar_cascade,scaleFact = 1.05, minNeigh = 3, minSizeW = 30):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    features = haar_cascade.detectMultiScale(
        gray,
        scaleFactor=scaleFact,
        minNeighbors=minNeigh,
        minSize=(minSizeW, minSizeW),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    return features


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
        (x,y,w,h) = calculate_boundbox(points[1:17])
    elif face_part == 7:
         (x,y,w,h) = calculate_boundbox(points[0:6])
    elif face_part == 8:
        (x,y,w,h) = calculate_boundbox(points[11:17])
    return (x,y,w,h)

def cvloop(run_event):
    global ctr_mid
    global SPRITES
    i = 0
    video_capture = cv2.VideoCapture(0)
    video_capture.set(3,2048)
    video_capture.set(4,2048)
    (x,y,w,h) = (0,0,10,10) 
    detector = dlib.get_frontal_face_detector()
    fullbody = cv2.CascadeClassifier('data/haarcascade_fullbody.xml')
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
            incl = calculate_inclination(shape[17], shape[26])
            is_mouth_open = (shape[66][1] -shape[62][1]) >= 10
            
            if SPRITES[3]:#Tiara
                apply_sprite(image, IMAGES[3][ACTIVE_IMAGES[3]],w+45,x-20,y+20, incl, ontop = True)

            #Necklaces
            if SPRITES[1]:
                (x1,y1,w1,h1) = get_face_boundbox(shape, 6)
                apply_sprite(image, IMAGES[1][ACTIVE_IMAGES[1]],w1,x1,y1+150, incl,  ontop = False)
            
            #Goggles
            if SPRITES[6]:
                (x3,y3,_,h3) = get_face_boundbox(shape, 1)
                apply_sprite(image, IMAGES[6][ACTIVE_IMAGES[6]],w,x,y3-10, incl, ontop = False)

            #Earrings
            (x0,y0,w0,h0) = get_face_boundbox(shape, 6) #bound box of mouth
            if SPRITES[2]:
                (x3,y3,w3,h3) = get_face_boundbox(shape, 7) #nose
                apply_sprite(image, IMAGES[2][ACTIVE_IMAGES[2]],w3,x3-40,y3+30, incl,ontop=False)
                (x3,y3,w3,h3) = get_face_boundbox(shape, 8) #nose
                apply_sprite(image, IMAGES[2][ACTIVE_IMAGES[2]],w3,x3+40,y3+75, incl) 

#            if SPRITES[5]:
#                apply_sprite(image, IMAGES[5][ACTIVE_IMAGES[5]],w,x,y, incl, ontop = True)
            
            #Frocks
            if SPRITES[5]:
                (x1,y1,w1,h1) = get_face_boundbox(shape, 8)
                apply_sprite(image, IMAGES[5][ACTIVE_IMAGES[5]],w1+580,x1-350,y1+80, incl,  ontop = False)

            #Tops
            if SPRITES[4]:
                # (x,y,w,h) = (0,0,10,10)
                # apply_sprite2feature(image, IMAGES[7][ACTIVE_IMAGES[7]], fullbody, w//4, 2*h//3, h//2, True, w//2, x, y, w, h)
                (x1,y1,w1,h1) = get_face_boundbox(shape, 8)
                apply_sprite(image, IMAGES[4][ACTIVE_IMAGES[4]],w1+350,x1-230,y1+100, incl,  ontop = False)
            
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        ctr_mid.configure(image=image)
        ctr_mid.image = image

    video_capture.release()

root = Tk()
root.title('TryOn')
app=FullScreenApp(root)

top_frame = Frame(root, bg='#077bd4', width=50, height=50, pady=3)
center = Frame(root, bg='white', width=50, height=40, padx=3, pady=3)
btm_frame = Frame(root, bg='#077bd4', width=50, height=50, pady=3)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame.grid(row=0, sticky="ew")
center.grid(row=1, sticky="nsew")
btm_frame.grid(row=4, sticky="ew")
logo = ImageTk.PhotoImage(Image.open('logo.png').resize((120,60)))
model_label = Label(top_frame,image=logo)

model_label.grid(row=0, columnspan=3)

center.grid_rowconfigure(0, weight=1)
center.grid_columnconfigure(1, weight=1)

ctr_left = Label(center,bg='white', width=50, height=190)
ctr_mid = Label(center,bg='white',width=100, height=160, padx=0, pady=0)

ctr_left.grid(row=0, column=0, sticky="ns")
ctr_mid.grid(row=0, column=1, sticky="nsew")

scrollable_body = Scrollable(ctr_left, width=15)
SPRITES=[0 for i in range(10)]
BTNS=[]
IMAGES ={i:[] for i in range(10)}
PHOTOS ={i:[] for i in range(10)}
for img in sys.argv[1:]:
    IMAGES[int(img.rsplit('/',1)[0][-1])].append(img)
    image=ImageTk.PhotoImage(Image.open(img).resize((150,100)))
    PHOTOS[int(img.rsplit('/',1)[0][-1])].append(image)
for index in range(9):
    if len(PHOTOS[index]) > 0:
        for k,photo in enumerate(PHOTOS[index]):
            btn= Button(scrollable_body, highlightbackground='white', text=IMAGES[index][k].rsplit('/',1)[1].replace('.png','')[:-1],bg='white', image=photo, command = lambda index=index, k=k: put_sprite(index,k), compound=LEFT, width='300', height='200')
            btn.pack(side="top", fill="both", expand="no", padx="5", pady="5")
            BTNS.append(btn)
scrollable_body.update()

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