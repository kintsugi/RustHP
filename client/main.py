import numpy as np
import cv2
import pyscreenshot as ImageGrab
import math
from time import sleep
from socketIO_client import SocketIO, LoggingNamespace

class ItemChecker:
    
    bbox2 = []
    
    def MatchImage(self, imagename, threshold):
        img = np.array(ImageGrab.grab()).astype(np.uint8)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_templ = cv2.Sobel(cv2.imread(imagename, cv2.IMREAD_GRAYSCALE), -1, 1, 1)
        roi = gray_img[bbox2[0][1]:bbox2[1][1], bbox2[0][0]:bbox2[1][0]]

        w,h=gray_templ.shape[::-1]
        method = 'cv2.TM_CCOEFF_NORMED'  

        gray_img2 = cv2.Sobel(roi, -1, 1, 1)
        meth = eval(method)
            
        res = cv2.matchTemplate(gray_img2,gray_templ,meth)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        if max_val>threshold:
            return True
        
        return False
     
    def region_select_callback(self,event,x,y,flags,param):
        global bbox2
        
        if event == cv2.EVENT_LBUTTONDOWN:
            bbox2 = [(x,y)]
        elif event == cv2.EVENT_LBUTTONUP:
            bbox2.append((x,y))       
            cv2.rectangle(param, bbox2[0], bbox2[1], (0, 255, 0), 2)
            cv2.destroyAllWindows()
        
    def GetBarBounds(self):
        img = np.array(ImageGrab.grab())
        cv_img = img.astype(np.uint8)
        
        cv2.namedWindow("Capture", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Capture", cv2.WND_PROP_FULLSCREEN, 1)
        cv2.setMouseCallback("Capture", self.region_select_callback, cv_img)
        
        while True:
            cv2.imshow("Capture", cv_img)
            key = cv2.waitKey(1)
            
            if key == ord("c"):
                cv2.destroyAllWindows()
                break
                
        sleep(0.1)
 
    def HasPistol(self):
        return self.MatchImage('pistol.jpg', 0.2)
        
    def HasPipe(self):
        return self.MatchImage('pipe.jpg', 0.2)
        
    def HasAK(self):
        return self.MatchImage('AK.jpg', 0.2)
        
    def HasBolt(self):
        return self.MatchImage('bolt.jpg', 0.2)

class ValueFinder:
    
    HP = 0
    Hunger = 0
    Thirst = 0
    bbox = []
  
    def roundup(self, x):
        return int(math.ceil(x / 10.0)) * 10
  
    def HPSet(self):
        self.HP = (self.GetStatusValues('health') / 6960.0)*100
        sleep(0.1)
        
    def HungerSet(self):
        self.Hunger = (self.GetStatusValues('hunger') / 6960.0)*100
        sleep(0.1)
        
    def ThirstSet(self):
        self.Thirst = (self.GetStatusValues('thirst') / 6720.0)*100
        sleep(0.1)
        
    def GetStatusBounds(self):
        img = np.array(ImageGrab.grab())
        cv_img = img.astype(np.uint8)
        
        cv2.namedWindow("Capture", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Capture", cv2.WND_PROP_FULLSCREEN, 1)
        cv2.setMouseCallback("Capture", self.region_select_callback, cv_img)
        
        while True:
            cv2.imshow("Capture", cv_img)
            key = cv2.waitKey(1)
            
            if key == ord("c"):
                cv2.destroyAllWindows()
                break
                
        sleep(0.1)
        
    def GetStatusValues(self, bar):
        img = np.array(ImageGrab.grab().convert('HSV')).astype(np.uint8)
        roi = img[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0]]
        
        boundaries = [
            ([50, 100, 100], [65, 255, 255]),
            ([140, 150, 120], [150, 255, 255]),
            ([10, 150, 150], [20, 255, 255])
        ]
        
        if bar == 'health':
            (lower,upper)=boundaries[0]
        elif bar == 'thirst':
            (lower,upper)=boundaries[1]
        elif bar == 'hunger':
            (lower,upper)=boundaries[2]
        else:
            (lower,upper)=boundaries[0]
        
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
            
        mask = cv2.inRange(roi, lower, upper)
        output = cv2.bitwise_and(roi, roi, mask = mask)
        
        h,s,v = cv2.split(output)
        return cv2.countNonZero(v)
        
    def region_select_callback(self,event,x,y,flags,param):
        global bbox
        
        if event == cv2.EVENT_LBUTTONDOWN:
            bbox = [(x,y)]
        elif event == cv2.EVENT_LBUTTONUP:
            bbox.append((x,y))       
            cv2.rectangle(param, bbox[0], bbox[1], (0, 255, 0), 2)
            cv2.destroyAllWindows()

def GeneratePayload(username, vf, ic):
    payload = {}
    vf.HPSet()
    vf.ThirstSet()
    vf.HungerSet()
    payload['username'] = username
    payload['health'] = vf.HP
    payload['hunger'] = vf.Hunger
    payload['thirst'] = vf.Thirst
    sleep(0.1)
    payload['bolt'] = ic.HasBolt()
    payload['AK'] = ic.HasAK()
    payload['pistol'] = ic.HasPistol()
    payload['pipe'] = ic.HasPipe()
    return payload
    
    
if __name__ == '__main__':
    username = raw_input("Username: ")
    
    vf = ValueFinder()
    vf.GetStatusBounds()
    
    ic = ItemChecker()
    ic.GetBarBounds()
    
    host = 'localhost'
    port = 3000
    
    socketIO = SocketIO(host, port, LoggingNamespace)
    
    while(True):
        payload = GeneratePayload(username, vf, ic)
        socketIO.emit('playerupdate', payload)
        socketIO.wait(seconds=1)
    