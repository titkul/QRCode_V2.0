import time
from csv import reader, DictWriter
from json import dumps, loads, dump

from requests import ConnectionError, HTTPError
from requests import get, post
from datetime import datetime
import requests

url = 'https://api-nfq.systemkul.com/v1/'

def call_json():
    url = 'https://api-nfq.systemkul.com/v1/'
    r = get(url + 'NhanVien/Kiosk?isPaged=false', headers={'Content-Type': 'application/json',})
    data1 = loads(r.text, strict=False)['data']
    with open('data/data5.json', 'w') as f:
        dump(data1, f)  
    print("okie")

def post_data():
    with open('data/recognization.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        try:
            for row in csv_reader:
                name_student_recognite = row[0]
                date = row[1]
                idptChamCong = 2
                tempt_student = row[2]
                uuid_device = "8ffe5f2c-4fa0-4209-8196-c6a33f6f9333" 
                data_request = {
                                "canCuocCongDan": name_student_recognite,
                                "ngayGioChamCong": date,
                                "nhietDo": tempt_student,
                                "maThietBi": uuid_device
                                }
                print(data_request)
                try:
                    r = post(url + "ChamCong/QRCode", timeout=10, data=dumps(data_request), headers={'Content-Type': 'application/json', })
                    print(r.status_code)
                    try:
                        r.raise_for_status()
                    except requests.exceptions.HTTPError as errh:
                        print ("Http Error:",errh.response.text)
                    except requests.exceptions.ConnectionError as errc:
                        print ("Error Connecting:",errc)
                    except requests.exceptions.Timeout as errt:
                        print ("Timeout Error:",errt)
                    except requests.exceptions.RequestException as err:
                        print ("OOps: Something Else",err)

                except ConnectionError:
                    print("No internet connection available.")
                    return
            with open ("data/recognization.csv", mode = "w") as re_csv_file:
                fieldnames = ['ID', 'Date', 'Temperature']
                writer = DictWriter(re_csv_file, fieldnames=fieldnames)
        except:
            print("hello")

if __name__ == "__main__":
    timeconut = 21600
    start = datetime.now()
    for _  in range(10):
        try:
            time.sleep(2)
            call_json()
            break
            
        except Exception as e:
            print(e)
    while True:
        post_data()
        time.sleep(5)
        try:    
            now = datetime.now()
            if (now - start).total_seconds() > timeconut:
                print("da upload data")
                call_json()
                start = now
        except:
            print("hello")
            pass
