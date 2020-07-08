import numpy as np
import cv2
import picamera
from time import sleep

#cap = cv2.VideoCapture(0)

photo_filename = '/tmp/data.jpg'

def shutter():
    photofile = open(photo_filename, 'wb')
    print(photofile)

    # pi camera 用のライブラリーを使用して、画像を取得
    with picamera.PiCamera() as camera:
        camera.resolution = (300,400)
        camera.capture(photofile)

if __name__ == '__main__':
    fgbg = cv2.createBackgroundSubtractorMOG2()
    shutter()
    img = cv2.imread(photo_filename, cv2.COLOR_BGR2RGB)
    fgmask = fgbg.apply(img)
    sleep(10)
    shutter()
    img2 = cv2.imread(photo_filename, cv2.COLOR_BGR2RGB)
    fgmask = fgbg.apply(img2)
    
    cv2.imwrite('forsale.jpg', fgmask)
