import time
from flask import Flask, request
import vlc
import requests
import array as arr
import numpy as np

app = Flask(__name__)

#URL = "http://disaster-chain.eastus.cloudapp.azure.com/post"
URL = "192.168.31.123:8000/post"
player = vlc.MediaPlayer("/home/pi/CFD-18/raspberry-pi/siren.mp3")
x=0
y=0
p,q=5,5
dev1 = np.zeros([4,p])
dev2 = np.zeros([4,p])
flag_device = False
@app.route('/post', methods=["POST"])
def postJsonHandler():
    global p,q #no of samples to be compared
    global x,y
    global dev1, dev2
    data = request.get_json()
    if data['deviceid'] == 1111: 
        dev1[0][x]= abs(data['values'][0])
        dev1[1][x]= abs(data['values'][1])
        dev1[2][x]= abs(data['values'][2])
        dev1[3][x]= abs(data['values'][3])	
        x = x+1
    if data['deviceid'] == 2222:  
        dev2[0][y]= abs(data['values'][0])
        dev2[1][y]= abs(data['values'][1])
        dev2[2][y]= abs(data['values'][2])
        dev2[3][y]= abs(data['values'][3])
        y= y+1
    print(dev1)
    print(dev2)
    if x > p-1: 
        x = 0
    if y > q-1:
        y = 0
    horizontal_avg_dev1=np.mean(dev1, axis=1)
    horizontal_avg_dev2=np.mean(dev2, axis=1)
    avg_dev1 = (horizontal_avg_dev1[0]+horizontal_avg_dev1[1]+horizontal_avg_dev1[2])/3
    avg_dev2 = (horizontal_avg_dev2[0]+horizontal_avg_dev2[1]+horizontal_avg_dev2[2])/3
    if (horizontal_avg_dev1[0]>1 or horizontal_avg_dev1[1] >1 or horizontal_avg_dev1[2]>1) and (horizontal_avg_dev2[0]>1 or horizontal_avg_dev2[1]>1 or horizontal_avg_dev2[0] >1):
        global flag_device
        flag_device = True
	coordinates = requests.get("http://api.ipstack.com/check?access_key=e8b0704f2fdaaa7d0f648d8e070916a3&fields=longitude,latitude").json()
	data['latitude'] =  coordinates['latitude']
	data['longitude'] =  coordinates['longitude']
        if not player.is_playing():
            player.play()
            time.sleep(5)
	r = requests.post(url=URL, json=data)
	print("Earthquake!!")
	
    else:
        print("You are safe")
    return ''


@app.route('/get', methods=["GET"])
def get():
   if  flag_device ==True:
	return "12"
	flag_device == False
   else:
	return "123"


app.run(host='0.0.0.0', port=8090, debug=True)
