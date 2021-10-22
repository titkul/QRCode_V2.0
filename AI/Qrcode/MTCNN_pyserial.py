import cv2
import time
import tensorflow
import detect_face
import numpy as np
import os
import time
from pyzbar import pyzbar

import threading
from time import sleep
from serial import Serial
from gtts import gTTS



os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

#----tensorflow version check
if tensorflow.__version__.startswith('1.'):
    import tensorflow as tf
else:
    import tensorflow.compat.v1 as tf
    tf.disable_v2_behavior()
print("Tensorflow version: ",tf.__version__)
arduino = Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)

def soud(staffName):

    os.system("mpg123 warning1.mp3")

def soud2(staffName):

    os.system("mpg123 qrcode.mp3")

def soud3(names):
    os.system("mpg123 thanhcong.mp3")

def soud5(names):
    os.system("mpg123 anthongtin.mp3")

def soud4(names):
    myobj = gTTS(text=names, lang="vi", slow=False)
    myobj.save("s1.mp3")
  
    os.system("mpg123 s1.mp3")



def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    sleep(0.05)
    data = arduino.readline()
    return data


def face_detection_MTCNN(detect_multiple_faces=False):

    frame_count = 0
    FPS = "Initialing"
    no_face_str = "No faces detected"

    color = (0,255,0)
    minsize = 400  # minimum size of face
    threshold = [0.6, 0.7, 0.7]  # three steps's threshold
    factor = 0.709  # scale factor
    temperature= 17
    with tf.Graph().as_default():
        config = tf.ConfigProto(log_device_placement=False,
                                allow_soft_placement=False
                                )
        config.gpu_options.per_process_gpu_memory_fraction = 0
        sess = tf.Session(config=config)
        with sess.as_default():
            pnet, rnet, onet = detect_face.create_mtcnn(sess, None)
    cap = cv2.VideoCapture(0)
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    start_time_temp = time.time()
    start_time_qrcode = time.time()
    demwaring = 0
    checkQRcode = 0 
    while (cap.isOpened()):
        ret, img = cap.read()
        if ret is True:
            img_rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            bounding_boxes, points = detect_face.detect_face(img_rgb, minsize, pnet, rnet, onet, threshold, factor)
            nrof_faces = bounding_boxes.shape[0]
            if checkQRcode == 1:
                barcodes = pyzbar.decode(img)
                try:
                    for barcode in barcodes:
                        (x, y, w, h) = barcode.rect
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        barcodeData = barcode.data.decode("utf-8")
                        barcodeType = barcode.type
                        # draw the barcode data and barcode type on the image
                        text = "{} ({})".format(barcodeData, barcodeType)
                        # print(text)
                        datacheck = text.split("*")
                        if len(datacheck) > 2:
                            t4_s = threading.Thread(target=soud5, args=(datacheck, ))
                            t4_s.start()
                            checkQRcode = 0
                            break
                        else:
                            text = str(text.split("|")[1])
                            if len(text) != 0:
                                t3_s = threading.Thread(target=soud4, args=(text, ))
                                t3_s.start()
                                checkQRcode = 0
                                break
                        cv2.putText(img, text, (x, y - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                except Exception as ess:
                    print(ess)
                if ((time.time() - start_time_qrcode )> 10):
                    print("QRcode {}".format(checkQRcode))
                    start_time_qrcode = time.time()
                    checkQRcode = 0
            else:
                if nrof_faces > 0:
                    points = np.array(points)
                    points = np.transpose(points, [1, 0])
                    points = points.astype(np.int16)
                    if demwaring == 1:
                        if ((time.time() - start_time_temp )> 2):
                            print("Nhiet do {}".format(demwaring))
                            start_time_temp = time.time()
                            demwaring = 0
                    else:    
                        while True:
                            try:
                                num = '?'
                                value = write_read(num).decode("utf8","ignore")
                                x_max = float(value)
                                temperature = round(0.1455*x_max + 32.108,2)  
                                if (temperature > 37.5):
                                    demwaring = 1
                                    temperature= 37.5  
                                    start_time = time.time()
                                    t1_s = threading.Thread(target=soud, args=( time.time(), ))
                                    t1_s.start()
                                if (temperature < 35.5):
                                    temperature= 35.5              
                                break
                            except Exception as es:
                                print(es)
                                temperature = "None"
                                try:
                                    arduino = Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
                                except Exception as e:
                                    print(e)
                                break
                    #Yeu cau scanQr
                    if checkQRcode == 0:
                        checkQRcode = 1
                        t2_s = threading.Thread(target=soud2, args=( time.time(), ))
                        t2_s.start()
                    det = bounding_boxes[:, 0:4]
                    det_arr = []
                    img_size = np.asarray(img.shape)[0:2]
                    if nrof_faces > 1:
                        if detect_multiple_faces:
                            for i in range(nrof_faces):
                                det_arr.append(np.squeeze(det[i]))
                        else:
                            bounding_box_size = (det[:, 2] - det[:, 0]) * (det[:, 3] - det[:, 1])
                            img_center = img_size / 2
                            offsets = np.vstack(
                                [(det[:, 0] + det[:, 2]) / 2 - img_center[1], (det[:, 1] + det[:, 3]) / 2 - img_center[0]])
                            offset_dist_squared = np.sum(np.power(offsets, 2.0), 0)
                            index = np.argmax(
                                bounding_box_size - offset_dist_squared * 2.0)  # some extra weight on the centering
                            det_arr.append(det[index, :])
                    else:
                        det_arr.append(np.squeeze(det))

                    det_arr = np.array(det_arr)
                    det_arr = det_arr.astype(np.int16)

                    for i, det in enumerate(det_arr):
                        #det = det.astype(np.int32)
                        cv2.rectangle(img, (det[0],det[1]), (det[2],det[3]), color, 2)

                else:
                    cv2.putText(img, no_face_str, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            # cv2.putText(img, FPS, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            #----image display
            cv2.imshow("Information", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("get image failed")
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    face_detection_MTCNN(detect_multiple_faces=True)
