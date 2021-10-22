
from datetime import datetime
import pickle
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import random
import os
from csv import DictWriter

from gtts import gTTS
from time import sleep
import threading
from serial import Serial
import tensorflow
import detect_face
from pyzbar import pyzbar

from GUIVIDEO import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication,QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import  QThread,  pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineSettings

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

#----tensorflow version check
if tensorflow.__version__.startswith('1.'):
    import tensorflow as tf
else:
    import tensorflow.compat.v1 as tf
    tf.disable_v2_behavior()
print("Tensorflow version: ",tf.__version__)



from json import dumps, load, loads
font_cv = cv2.FONT_HERSHEY_SIMPLEX
unknownTemperature = []
unknownTime = []
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG'} 



address_congty = "24 Nguyen Binh Khiem, Da Kao Ward, District 1, Ho Chi Minh City"


class Thread(QThread):
    changePixmap = pyqtSignal(QImage, name='video')
    changeName = pyqtSignal(str, name='name')
    changeMnv = pyqtSignal(str, name='mnv')
    changeTime = pyqtSignal(str, name='time')
    changePosition = pyqtSignal(str, name='position')
    changePhoto = pyqtSignal(QImage, name='avatar')
    changePhoto2 = pyqtSignal(QImage, name='avatar2')
    changePhoto3 = pyqtSignal(QImage, name='avatar3')
    changeTemperature = pyqtSignal(str, name='temperature')

    def getCMND(self, data, id):
        for i in data:
            try:
                if id == i['canCuocCongDan']:
                    name = i['tenNV']
                    ChucVu = i['chucVu']
                    manhanvien = i['maNV']
                    return name, ChucVu, manhanvien
            except Exception as e:
                pass
                print(e)
        return None, None, None

    def getSDT(self, data, id):
        for i in data:
            try:
                if id == i['soDienThoai']:
                    name = i['tenNV']
                    ChucVu = i['chucVu']
                    manhanvien = i['maNV']
                    return name, ChucVu, manhanvien
            except Exception as e:
                pass
                print(e)
        return None, None, None



    def write_read(self, x):
        self.arduino.write(bytes(x, 'utf-8'))
        sleep(0.05)
        data = self.arduino.readline()
        return data

    def soud(self, staffName):

        os.system("mpg123 warning1.mp3")

    def soud2(self, staffName):

        os.system("mpg123 qrscan.mp3")

    def soud3(self, names):
        os.system("mpg123 succss.mp3")

    def soud5(self, names):
        os.system("mpg123 hidden.mp3")

    def soud6(self, names):
        os.system("mpg123 unknow.mp3")

    def soud4(self, names):
        myobj = gTTS(text=names, lang="vi", slow=False)
        myobj.save("s1.mp3")
    
        os.system("mpg123 s1.mp3")

    def upload_info(self, staffMnv, data_time, temperature, mnv_number):
        with open ("hrdata/data/recognization.csv", mode = "+a") as re_csv_file:
            fieldnames = ['ID', 'Date' , 'Temperature', "Mnv"]
            writer = DictWriter(re_csv_file, fieldnames=fieldnames)
            writer.writerow({'ID': staffMnv, 'Date': str(data_time), 'Temperature': temperature, "Mnv": mnv_number})
        with open ("hrdata/data/recognizationbakup.csv", mode = "+a") as re_csv_file1:
            fieldnames = ['ID', 'Date' , 'Temperature' ,  "Mnv"]
            writer = DictWriter(re_csv_file1, fieldnames=fieldnames)
            writer.writerow({'ID': staffMnv, 'Date': str(data_time), 'Temperature': temperature, "Mnv": mnv_number}) 

    def image_info(self, frame_s, info_name, data_time, core_acc):
        if not os.path.exists(os.path.join("images", "{}".format(info_name))):
            os.makedirs(os.path.join("images", "{}".format(info_name)))
        cv2.imwrite("images/{}/{}-{:.2f}-{}.png".format(info_name,info_name, core_acc, data_time), 
                    cv2.cvtColor(frame_s, cv2.COLOR_RGB2BGR))   
    def processing_time():
        print("hello")

    def run(self):
        f = open('hrdata/data/data5.json')
        self.data = load(f)

        self.temperature = 17
        self.threshold = 70
        self.color = (0,255,0)
        self.minsize = 550  # minimum size of face
        self.threshold = [0.6, 0.7, 0.7]  # three steps's threshold
        self.factor = 0.709  # scale factor
        with tf.Graph().as_default():
            config = tf.ConfigProto(log_device_placement=False,
                                    allow_soft_placement=False
                                    )
            config.gpu_options.per_process_gpu_memory_fraction = 0
            sess = tf.Session(config=config)
            with sess.as_default():
                self.pnet, self.rnet, self.onet = detect_face.create_mtcnn(sess, None)
        self.cap = cv2.VideoCapture(0) 
        
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.cap.set(28, 0)
        self.cap.set(3, 1280) 
        self.cap.set(4, 720)
        self.start_time_upload_data = time.time()
        self.start_time_temp = time.time()
        self.start_time_qrcode = time.time()
        self.demwaring = 0
        self.checkQRcode = 0 
        while (self.cap.isOpened()):     
            if  (time.time()-self.start_time_upload_data >45):
                try:
                    f = open('hrdata/data/data5.json')
                    self.data = load(f)
                except:
                    pass
                self.start_time_upload_data = time.time()
            self.ret, self.frame = self.cap.read()
            if self.ret:
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                try:
                    self.bounding_boxes, self.points = detect_face.detect_face(self.frame, self.minsize, self.pnet, self.rnet, self.onet, self.threshold, self.factor)
                    self.nrof_faces = self.bounding_boxes.shape[0]
                    if self.checkQRcode == 1:
                        cv2.rectangle(self.frame, (320,180), (960,540), self.color, 2)
                        self.cap.set(28, 100)
                        barcodes = pyzbar.decode(self.frame)
                        try:
                            for barcode in barcodes:
                                (x, y, w, h) = barcode.rect
                                cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                                barcodeData = barcode.data.decode("utf-8")
                                barcodeType = barcode.type
                                text = "{} ({})".format(barcodeData, barcodeType)
                                datacheck = text.split("*")
                                if len(datacheck) > 2:
                                    t4_s = threading.Thread(target=self.soud5, args=(datacheck, ))
                                    t4_s.start()
                                    self.start_time_qrcode = time.time()
                                    self.checkQRcode = 2
                                    self.cap.set(28, 0)
                                    break
                                else:
                                    texts = text.split("|")
                                    if len(texts[1]) != 0:
                                        self.timeDetect = datetime.now().strftime("%H:%M:%S")
                                        self.checkNameCC, self.positionCC , self.staffMnvCC = self.getCMND(self.data, texts[0])
                                        if str(self.checkNameCC) == 'None':
                                            self.checkNameDT, self.positionDT , self.staffMnvDT = self.getSDT(self.data,texts[5].split("<<")[1].split(" ")[0])
                                            if str(self.checkNameDT) == "None":
                                                t6_s = threading.Thread(target=self.soud6, args=(texts[1], ))
                                                t6_s.start()
                                                self.changeTemperature.emit(str(self.temperature))
                                                un_img_save_4 = Image.open("img.png")
                                                width, height = un_img_save_4.size
                                                x = (width - height) // 2
                                                img_cropped = un_img_save_4.crop((x, 0, x + height, height))
                                                mask = Image.new('L', img_cropped.size)
                                                mask_draw = ImageDraw.Draw(mask)
                                                width, height = img_cropped.size
                                                mask_draw.ellipse((10, 10, width-10, height-10), fill=255)
                                                img_cropped.putalpha(mask)
                                                un_img_save_4 = img_cropped.resize((128, 128), Image.ANTIALIAS)
                                                un_img_save_4.save("unknowImage/unknow_people_1.png")
                                                photo3 = QImage('unknowImage/unknow_people_1.png')
                                                self.changePhoto3.emit(photo3) 
                                            else:
                                                self.staffName = self.checkNameDT
                                                self.position = self.positionDT
                                                self.staffMnv = self.staffMnvDT
                                                t3_s = threading.Thread(target=self.soud3, args=(texts[1], ))
                                                t3_s.start()
                                                t5_s = threading.Thread(target=self.upload_info, args=(texts[0], str(datetime.now()), self.temperature,  self.staffMnv ))
                                                t5_s.start()  
                                                self.changeName.emit(str(self.staffName))
                                                self.changeMnv.emit(str(self.staffMnv))
                                                self.changePosition.emit(str(self.position))
                                                self.changeTemperature.emit(str(self.temperature))
                                                self.changeTime.emit(str(self.timeDetect))
                                                photo2 = QImage('recogniteImage/people_recognite_3.png')
                                                self.changePhoto2.emit(photo2)
                                                photo = QImage('recogniteImage/people_recognite_1.png')
                                                self.changePhoto.emit(photo) 
                                        else:
                                            self.staffName = self.checkNameCC
                                            self.position = self.positionCC
                                            self.staffMnv = self.staffMnvCC
                                            t3_s = threading.Thread(target=self.soud3, args=(texts[1], ))
                                            t3_s.start()
                                            t5_s = threading.Thread(target=self.upload_info, args=(texts[0], str(datetime.now()), self.temperature,  self.staffMnv ))
                                            t5_s.start()                                            
                                            self.changeName.emit(str(self.staffName))
                                            self.changeMnv.emit(str(self.staffMnv))
                                            self.changePosition.emit(str(self.position))
                                            self.changeTemperature.emit(str(self.temperature))
                                            self.changeTime.emit(str(self.timeDetect))
                                            photo2 = QImage('recogniteImage/people_recognite_3.png')
                                            self.changePhoto2.emit(photo2)
                                            photo = QImage('recogniteImage/people_recognite_1.png')
                                            self.changePhoto.emit(photo)  
                                        self.checkQRcode = 2
                                        self.start_time_qrcode = time.time()
                                        self.cap.set(28, 0)
                                        break
                                cv2.putText(self.frame, text, (x, y - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        except Exception as ess:
                            print(ess)
                        if ((time.time() - self.start_time_qrcode )> 10):
                            print("QRcode {}".format(self.checkQRcode))
                            self.start_time_qrcode = time.time()
                            self.checkQRcode = 0
                    elif (self.checkQRcode == 2):
                        if  time.time() - self.start_time_qrcode > 4:
                            self.checkQRcode = 0
                            self.start_time_qrcode = time.time()
                            self.cap.set(28, 0)
                            print("QRcode ############ {}".format(self.checkQRcode))
                    else:
                        self.cap.set(28, 0)
                        if self.nrof_faces > 0:
                            if (self.nrof_faces > 1):
                                cv2.putText(self.frame, "Over 2 people", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                                continue
                            if self.demwaring == 1:
                                if ((time.time() - self.start_time_temp )> 2):
                                    print("Nhiet do {}".format(self.demwaring))
                                    self.start_time_temp = time.time()
                                    self.demwaring = 0
                            else:    
                                while True:
                                    try:
                                        num = '?'
                                        value = self.write_read(num).decode("utf8","ignore")
                                        x_max = float(value)
                                        self.temperature = round(0.1455*x_max + 32.108,2)  

                                        if (self.temperature > 37.5):
                                            if (self.temperature > 38.5):
                                                self.temperature= 38.5 
                                            self.demwaring = 1
                                            self.temperature= 37.5  
                                            self.start_time = time.time()
                                            t1_s = threading.Thread(target=self.soud, args=( time.time(), ))
                                            t1_s.start()
                                        if (self.temperature < 35.5):
                                            self.temperature= 35.5              
                                        break
                                    except Exception as es:
                                        print(es)
                                        self.temperature = "None"
                                        try:
                                            self.arduino = Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
                                        except Exception as e:
                                            print(e)
                                        break
                            #Yeu cau scanQr
                            if self.checkQRcode == 0:
                                self.checkQRcode = 1
                                t2_s = threading.Thread(target=self.soud2, args=( time.time(), ))
                                t2_s.start()

                            img_save_1 = Image.open("recogniteImage/people_recognite_1.png")  # image extension *.png,*.jpg
                            img_save_1.save("recogniteImage/people_recognite_3.png")
    
                            cv2.imwrite('img.png', cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
                            # cv2.imwrite('img2.png', cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
                            img_save_4 = Image.open("img.png")
                            width, height = img_save_4.size
                            x = (width - height) // 2
                            img_cropped = img_save_4.crop((x, 0, x + height, height))
                            mask = Image.new('L', img_cropped.size)
                            mask_draw = ImageDraw.Draw(mask)
                            width, height = img_cropped.size
                            mask_draw.ellipse((10, 10, width-10, height-10), fill=255)
                            img_cropped.putalpha(mask)
                            img_save_4 = img_cropped.resize((128, 128), Image.ANTIALIAS)
                            img_save_4.save("recogniteImage/people_recognite_1.png")
                        else:
                            cv2.putText(self.frame, "No face", (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 3)

                except Exception as e:
                    print(e)
                    image = Image.fromarray(self.frame)
                    draw = ImageDraw.Draw(image)
                    font = ImageFont.truetype('utils1/simkai.ttf', 60)
                    draw.text((20, 100), 'No having face true', fill=(255, 0, 0), font=font)
                    self.frame = np.asarray(image) 
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR) 
                cv2.putText(self.frame, str(datetime.now().strftime("%Y/%m/%d , %H:%M:%S")), (80,60), font_cv, 1, (0, 0, 255), 2, cv2.LINE_AA)
                rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
                if ord('q') == cv2.waitKey(10):
                    cap.release()
                    cv2.destroyAllWindows()
                    exit(0)
class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.position = QtWidgets.QLabel(self.centralwidget)
        self.address = QtWidgets.QLabel(self.centralwidget)
        self.munkown = QtWidgets.QLabel(self.centralwidget)
        self.mnv_old = QtWidgets.QLabel(self.centralwidget)
        self.qr_yte_scan = QtWidgets.QLabel(self.centralwidget)
        self.qr_sup_scan = QtWidgets.QLabel(self.centralwidget)
        self.temp = QtWidgets.QLabel(self.centralwidget)
        self.time_log = QtWidgets.QLabel(self.centralwidget)
        self.name_nv = QtWidgets.QLabel(self.centralwidget)
        self.mnv = QtWidgets.QLabel(self.centralwidget)
        self.photo = QtWidgets.QLabel(self.centralwidget)
        self.photo_title = QtWidgets.QLabel(self.centralwidget)
        self.company_name = QtWidgets.QLabel(self.centralwidget)
        self.logo = QtWidgets.QLabel(self.centralwidget)
        self.video = QtWidgets.QLabel(self.centralwidget)
        self.photo2 = QtWidgets.QLabel(self.centralwidget)
        self.photo3 = QtWidgets.QLabel(self.centralwidget)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layout1 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.qrcode = QtWidgets.QLabel(self.centralwidget)
        self.qr_yte = QtWidgets.QLabel(self.centralwidget)
        try:
            self.arduino = Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
        except Exception as e:
            print(e)

        th = Thread(self.centralwidget)
        th.changePixmap.connect(lambda image: self.setImage(image))
        th.changeName.connect(lambda name: self.setName(name))
        th.changeMnv.connect(lambda mnv: self.setMnv(mnv))
        th.changePosition.connect(lambda position: self.setPosition(position))
        th.changeTime.connect(lambda time: self.setTime(time))
        th.changePhoto.connect(lambda photo: self.setPhoto(photo))
        th.changePhoto2.connect(lambda photo2: self.setPhoto2(photo2))
        th.changePhoto3.connect(lambda photo3: self.setPhoto3(photo3))
        th.changeTemperature.connect(lambda temp: self.setTemperature(temp))
        th.start()

    @pyqtSlot(QImage, name='video')
    def setImage(self, image):
        image = QPixmap.fromImage(image)
        image = image.scaled(640, 480, Qt.KeepAspectRatio)
        self.video.setPixmap(image)

    @pyqtSlot(QImage, name='avatar')
    def setPhoto(self, photo):
        photo = QPixmap.fromImage(photo)
        self.photo.setStyleSheet("background-color: none")        
        self.photo.setPixmap(photo)

    @pyqtSlot(QImage, name='avatar2')
    def setPhoto2(self, photo2):
        photo2 = QPixmap.fromImage(photo2)
        self.photo2.setPixmap(photo2)

    @pyqtSlot(QImage, name='avatar3')
    def setPhoto3(self, photo3):
        photo3 = QPixmap.fromImage(photo3)
        self.photo3.setPixmap(photo3)

    @pyqtSlot(QImage, name='avatar6')
    def setPhoto6(self, qrcode):
        qrcode = QPixmap.fromImage(qrcode)
        self.qrcode.setPixmap(qrcode)

    @pyqtSlot(QImage, name='avatar7')
    def setPhoto7(self, qr_yte):
        qr_yte = QPixmap.fromImage(qr_yte)
        self.qr_yte.setPixmap(qr_yte)

    @pyqtSlot(str, name='time')
    def setTime(self, time):
        self.time_log.setText('Time: ' + time)

    @pyqtSlot(str, name='temperature')
    def setTemperature(self, temperature):
        if temperature != "None":
            if (float(temperature) >= 37.5):
                beep = lambda x: os.system("echo -n '\a';sleep 0.2;" * x)
                self.temp.setStyleSheet("background-color: red;  border: 1px solid black;") 
                self.temp.setText('Temperature: > ' + temperature + '°C')
            else:
                self.temp.setStyleSheet("background-color: none;  border: 1px solid none;")
                self.temp.setText('Temperature: ' + temperature + '°C')
        else:
            self.temp.setStyleSheet("background-color: red;  border: 1px solid black;") 
            self.temp.setText('Temperature: ' + temperature)

    @pyqtSlot(str, name='name')
    def setName(self, name):
        self.name_nv.setText('Full name: ' + name)

    @pyqtSlot(str, name='mnv')
    def setMnv(self, name):
        self.mnv.setText('N.o Code: ' + name)

    @pyqtSlot(str, name='position')
    def setPosition(self, position):
        self.position.setText('Position: ' + position)


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1080, 1920)
        MainWindow.setMinimumSize(QtCore.QSize(1080, 1920))
        MainWindow.setMaximumSize(QtCore.QSize(1080, 1920))
        MainWindow.setSizeIncrement(QtCore.QSize(1080, 1920))
        MainWindow.setBaseSize(QtCore.QSize(1080, 1920))
        font = QtGui.QFont('Arial', 10)
        self.browser = window1()
        font.setPointSize(8)
        MainWindow.setFont(font)
        self.centralwidget.setObjectName("centralwidget")
        self.video.setGeometry(QtCore.QRect(20, 150, 720, 810))
        self.video.setMinimumSize(QtCore.QSize(720, 810))
        self.video.setMaximumSize(QtCore.QSize(720, 810))
        self.video.setText("")
        self.video.setScaledContents(True)

        self.photo_title.setGeometry(QtCore.QRect(20, 10, 720, 100))
        self.photo_title.setText("")
        self.photo_title.setPixmap(QtGui.QPixmap("Image/NFQ.png"))
        self.photo_title.setScaledContents(True)

        self.logo.setGeometry(QtCore.QRect(760, 10, 91, 91))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("Image/logo_nfq.jpg"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")

        self.company_name.setGeometry(QtCore.QRect(860, 10, 250, 41))
        font_company = QtGui.QFont('Arial', 18)
        font_company.setBold(True)
        self.company_name.setFont(font_company)

        self.photo.setGeometry(QtCore.QRect(830, 180, 191, 201))
        self.photo.setText("")
        self.photo.setPixmap(QtGui.QPixmap("Image/circled_user_male_480px.png"))
        self.photo.setScaledContents(True)

        self.photo2.setGeometry(QtCore.QRect(780, 620, 131, 131))
        self.photo2.setText("")
        self.photo2.setStyleSheet("background-color: green")
        self.photo2.setPixmap(QtGui.QPixmap("Image/circled_user_male_480px.png"))
        self.photo2.setScaledContents(True)

        self.photo3.setGeometry(QtCore.QRect(930, 620, 141, 131))       
        self.photo3.setText("")
        self.photo3.setStyleSheet("background-color: red")
        self.photo3.setPixmap(QtGui.QPixmap("Image/circled_user_male_480px.png"))
        self.photo3.setScaledContents(True)
        
        self.mnv_old.setGeometry(QtCore.QRect(810, 760, 161, 31))
        font = QtGui.QFont('Arial', 12)
        font.setItalic(False)
        font.setBold(True)
        self.mnv_old.setFont(font)

        self.qr_sup_scan.setGeometry(QtCore.QRect(795, 950, 161, 31))
        font = QtGui.QFont('Arial', 12)
        font.setItalic(True)
        self.qr_sup_scan.setFont(font)

        self.qrcode.setGeometry(QtCore.QRect(780, 810, 131, 131))
        self.qrcode.setPixmap(QtGui.QPixmap("Image/qrcongty.jpg"))
        self.qrcode.setText("")
        self.qrcode.setObjectName("qrcode")
        self.qrcode.setScaledContents(True)

        self.munkown.setGeometry(QtCore.QRect(960, 760, 161, 31))
        font = QtGui.QFont('Arial', 12)
        font.setBold(True)
        font.setItalic(False)
        self.munkown.setFont(font)

        self.qr_yte.setGeometry(QtCore.QRect(930, 810, 141, 131))
        self.qr_yte.setPixmap(QtGui.QPixmap("Image/QRNFQ.jpg"))
        self.qr_yte.setText("")
        self.qr_yte.setObjectName("qr_yte")
        self.qr_yte.setScaledContents(True)

        self.qr_yte_scan.setGeometry(QtCore.QRect(930, 950, 161, 31))
        font = QtGui.QFont('Arial', 12)
        font.setItalic(True)
        self.qr_yte_scan.setFont(font)

        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 1080, 1040, 720))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.web = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.web.setObjectName("web")

        
        self.layout1.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.layout1.setContentsMargins(0, 0, 0, 0)
        self.layout1.setObjectName("layout1")
        self.layout1.addWidget(self.browser)

        self.name_nv.setGeometry(QtCore.QRect(770, 490, 291, 50))
        self.name_nv.setWordWrap(True)
        # self.name_nv.setGeometry(QtCore.QRect(770, 490, 291, 31))
        font = QtGui.QFont('Arial', 15)
        font.setBold(True)
        self.name_nv.setFont(font)


        self.mnv.setGeometry(QtCore.QRect(770, 570, 241, 31))
        font = QtGui.QFont('Arial', 12)
        font.setItalic(True)
        self.mnv.setFont(font)

        self.position.setGeometry(QtCore.QRect(770, 540, 301, 16))
        font = QtGui.QFont('Arial', 12)
        font.setItalic(True)
        self.position.setFont(font)

        self.time_log.setGeometry(QtCore.QRect(830, 420, 161, 21))
        font = QtGui.QFont('Arial', 12)
        self.time_log.setFont(font)

        self.temp.setGeometry(QtCore.QRect(830, 450, 161, 21))
        font = QtGui.QFont('Arial', 12)
        self.temp.setFont(font)

        self.address.setGeometry(QtCore.QRect(860, 70, 220, 50))
        self.address.setWordWrap(True)
        font_address = QtGui.QFont('Arial', 8)
        font_address.setItalic(True)
        self.address.setFont(font_address)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1080, 19))

        MainWindow.setMenuBar(self.menubar)

        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def video_run(self):
        pass

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.company_name.setText(_translate("MainWindow", "NFQ Vietnam Co."))
        self.name_nv.setText(_translate("MainWindow", "Full name : "))
        self.time_log.setText(_translate("MainWindow", "Time:"))
        self.temp.setText(_translate("MainWindow", "Temperature:"))
        self.position.setText(_translate("MainWindow", "Position:"))
        self.address.setText(_translate("MainWindow", "Address: {}".format(address_congty)))
        self.mnv.setText(_translate("MainWindow", "N.o Code:"))
        self.mnv_old.setText(_translate("MainWindow", "KNOW"))
        self.qr_yte_scan.setText(_translate("MainWindow", "Medical declaration"))
        self.qr_sup_scan.setText(_translate("MainWindow", "Titkul Support"))
        self.munkown.setText(_translate("MainWindow", "UNKOWN"))
        self.web.setText(_translate("MainWindow", ""))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
