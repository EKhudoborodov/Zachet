from django.shortcuts import render
from django.http import StreamingHttpResponse

from yolov5.utils.general import (check_img_size, non_max_suppression, scale_coords, 
                                  check_imshow, xyxy2xywh, increment_path)
from yolov5.utils.torch_utils import select_device, time_sync
from yolov5.utils.plots import Annotator, colors
from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort
import cv2, yolov5, torch, psycopg2, datetime
from PIL import Image as im

conn = psycopg2.connect(dbname="yolo_db",
                                user="postgres", 
                                password="postgres", 
                                host="localhost", 
                                port="5432")
cursor = conn.cursor()

# Create your views here.

def index(request):
    return render(request, 'index.html')
    
#load model
model = yolov5.load('best_3.pt')
#model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
device = select_device('') # 0 for gpu, '' for cpu

# initialize deepsort

cfg = get_config()
cfg.merge_from_file("deep_sort/configs/deep_sort.yaml")
deepsort = DeepSort('osnet_x0_25',
                    device,
                    max_dist=cfg.DEEPSORT.MAX_DIST,
                    max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                    max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                    )
                    
# Get names and colors

names = model.module.names if hasattr(model, 'module') else model.names
    
def stream():
    cap = cv2.VideoCapture(0)
    #model.conf = 0.45
    #model.iou = 0.5
    #model.classes = [0,64,39]
    prev_check = 1
    #cursor.execute("INSERT INTO public.events (event_time, event_type, event_details) VALUES (%s, %s, %s);", (str(datetime.datetime.now()), 'Server', 'Server started'))
    #print("Server started")
    #conn.commit()
    while True:
        f_eyes, f_month, f_nose = 0, 0, 0
        p_eyes, p_month, p_nose = 0, 0, 0
        ret, frame = cap.read()
        if not ret:
            print("Error: failed to capture image")
            break
        results = model(frame, augment=True)
        
        # proccess
        annotator = Annotator(frame, line_width=2, pil=not ascii) 
        
        det = results.pred[0]
        if det is not None and len(det):   
            xywhs = xyxy2xywh(det[:, 0:4])
            confs = det[:, 4]
            clss = det[:, 5]
            outputs = deepsort.update(xywhs.cpu(), confs.cpu(), clss.cpu(), frame)
            if len(outputs) > 0:
                for j, (output, conf) in enumerate(zip(outputs, confs)):

                    bboxes = output[0:4]
                    id = output[4]
                    cls = output[5]

                    c = int(cls)  # integer class
                    f_eyes += c==0
                    f_month += c==1
                    f_nose += c==2
                    label = f'{id} {names[c]} {conf:.2f}'
                    #0 - Eye, 1 - Month, 2 - Nose
                    annotator.box_label(bboxes, label, color=(255*(c==0), 255*(c==1), 255*(c==2)))

        else:
            deepsort.increment_ages()
        
        im0 = annotator.result()
        out = f"{f_eyes} Eyes"*(f_eyes>1)+f"{f_eyes} Eyes"*(f_eyes==1)+" "+f"{f_month} Month"*(f_month==1)+f"{f_month} Months"*(f_month>1)+" "+f"{f_nose} Noses"*(f_nose>1)+f"{f_nose} Nose"*(f_nose==1)
        if ((f_eyes==0) & (f_month==0) & (f_nose==0)): 
            check = 1
        else:
            if ((f_eyes==2) & (f_month==1) & (f_nose==1)):
                check = 2
            elif (((f_eyes-p_eyes)>=2) & ((f_month-p_month)>=1) & ((f_nose-p_nose)>=1)):
                check = 2
                if check>=2:
                    check += 1
            elif (((f_eyes-p_eyes)<=-2) & ((f_month-p_month)<=-1) & ((f_nose-p_nose)<=-1)):
                check = 1
                if check<=1:
                    check -= 1
                
            
        """
        if test==1:
            test_time = str(datetime.datetime.now())
            cursor.execute(f"INSERT INTO public.events (event_time, event_type, event_details) VALUES ('{test_time}', 'Test', 'Test done')")
            cursor.execute(f"SELECT event_time, event_type, event_details FROM public.events WHERE event_time='{test_time}' AND event_type='Test' AND event_details='Test done'")
            records = list(cursor.fetchall())
            print(records[0])
            print('Tests done')
            test = 0
            conn.commit()
        """
        
        
        if check!=prev_check:
            try:
                if check >= 2:
                    cursor.execute("INSERT INTO public.events (event_time, event_type, event_details) VALUES (%s, %s, %s);", (str(datetime.datetime.now()), 'Detected face', out))
                    print(f"{str(datetime.datetime.now())}, Detected face")
                else:
                    out = "no detections"
                    cursor.execute("INSERT INTO public.events (event_time, event_type, event_details) VALUES (%s, %s, %s);", (str(datetime.datetime.now()), 'Lost face', out))
                    print(f"{str(datetime.datetime.now())}, Lost face")
                    stop = 1
                
                p_eyes=f_eyes
                p_month=f_month
                p_nose=f_nose
                #cursor.execute("INSERT INTO public.events (event_time, event_type, event_details, isdeleted) VALUES ('2022-07-06', 'Detected', 'fef')")
                prev_check=check
                conn.commit()
            except Exception as e:
                print(e.args)
                continue
                
        image_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')  
    cursor.execute("INSERT INTO public.events (event_time, event_type, event_details) VALUES (%s, %s, %s);", (str(datetime.datetime.now()), 'Server', 'Server stoped'))
            print('Server stoped') 
            conn.commit() 
    
def video_feed(request):
    return StreamingHttpResponse(stream(), content_type='multipart/x-mixed-replace; boundary=frame')    
