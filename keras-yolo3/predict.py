import sys
import argparse
import ntpath
from yolo import YOLO, detect_video
from PIL import Image

if __name__ == '__main__':
    while True:
        img = input('Input image filename:')
        try:
            image = Image.open(img)
        except:
            print('Open Error! Try again!')
            continue
        else:
            output_dir = 'output/'
            _, file_name = ntpath.split(img)
            
            r_image = YOLO().detect_image(image)
            r_image.save(output_dir + 'result_{}.jpg'.format(file_name.replace('.jpg', '')))
        
    yolo.close_session()
    