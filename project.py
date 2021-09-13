import tensorflow.keras
import numpy as np
import cv2
import RPi.GPIO as GPIO
import time

pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings (False)
GPIO.setup(pin, GPIO.OUT)
p = GPIO.PWM(pin,50)
p.start(7.5)
time.sleep(0)
p.ChangeDutyCycle(0)


# 모델 위치
model = tensorflow.keras.models.load_model('keras_model.h5')
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_frontalface_alt2.xml')
# 카메라를 제어할 수 있는 객체
capture = cv2.VideoCapture(0)

# 카메라 길이 너비 조절
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# 이미지 처리하기
def preprocessing(frame):
    #frame_fliped = cv2.flip(frame, 1)
    # 사이즈 조정 티쳐블 머신에서 사용한 이미지 사이즈로 변경해준다.
    size = (224, 224)
    frame_resized = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
   
    # 이미지 정규화
    # astype : 속성
    frame_normalized = (frame_resized.astype(np.float32) / 127.0) - 1

    # 이미지 차원 재조정 - 예측을 위해 reshape 해줍니다.
    # keras 모델에 공급할 올바른 모양의 배열 생성
    frame_reshaped = frame_normalized.reshape((1, 224, 224, 3))
    #print(frame_reshaped)
    return frame_reshaped

# 예측용 함수
def predict(frame):
    prediction = model.predict(frame)
    return prediction

while True:
    ret, frame = capture.read()

    if cv2.waitKey(100) > 0:
        p.stop()
        GPIO.cleanup()
        break

    preprocessed = preprocessing(frame)
    prediction = predict(preprocessed)
    if ((prediction[0,0] > prediction[0,1]) and (prediction[0,0] > prediction[0,2])):
        print('park')
        cv2.putText(frame, 'park', (0, 25), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0))
        ret, img = capture.read()
        faces = faceCascade.detectMultiScale(img)
        for (x,y,w,h) in faces:
           
           
            locate_x = x
            locate_y = y
            length = w
            height = h
               
            cv2.rectangle(img,(x, y, w, h), (0,255,0),2)
            print(faces)
            if(((locate_x+(length/2))<140) and ((locate_x+(length/2))> 0)):        
                p.ChangeDutyCycle(10.5)
                time.sleep(0.02)
                p.ChangeDutyCycle(0)
                time.sleep(0.5)
               
            elif((locate_x+(length/2))>180):                
                p.ChangeDutyCycle(0.1)  
                time.sleep(0.02)
                p.ChangeDutyCycle(0)
                time.sleep(0.5)
                           
            elif ((locate_x+(length/2)) == 0):
                continue
           
        cv2.imshow('video', img)
       

    elif ((prediction[0,1] > prediction[0,0]) and (prediction[0,1] > prediction[0,2])):
        cv2.putText(frame, 'go', (0, 25), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0))
        print('go')
       
    else :
        print('blank')
        cv2.putText(frame, 'blank', (0, 25), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0))        

    cv2.imshow("VideoFrame", frame)