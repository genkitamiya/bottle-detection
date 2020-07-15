import numpy as np
import sys
import glob
import picamera
import argparse
import ntpath
from yolo import YOLO
from PIL import Image, ImageOps, ImageTk
from datetime import datetime
from contextlib import redirect_stdout
from tqdm import tqdm
# warning処理
import warnings
warnings.filterwarnings('ignore')

def eval():
    pos_path = './test/positive/*.jpg'
    neg_path = './test/negative/*.jpg'

    # 正解率計算
    total_pos = len(glob.glob(pos_path))
    cnt = 0
    result = ""
    for f in tqdm(sorted(glob.glob(pos_path))):
        img = Image.open(f)
        pred_class, score, image = yolo.detect_image(img)
        # print(f, int(f[f.rfind("/")+1]), pred_class[0])
        result += "{}, {}, {} \n".format(f, pred_class, score)
        cnt += int(f[f.rfind("/")+1]) == pred_class[0]
    with open("test/posresults_{}.txt".format(datetime.now().strftime("%Y%m%d%H%M")), mode="w") as f:
        f.write(result)
    print('正解率：{:.2f}%'.format(cnt / total_pos*100)) #Accuracy計算

    # 真陰性率計算
    total_neg = len(glob.glob(neg_path))
    true_neg = total_neg
    result = ""
    neg_iter = tqdm(sorted(glob.glob(neg_path)))
    for f in neg_iter:
        img = Image.open(f)
        pred_class, score, image = yolo.detect_image(img)
        result += "{}, {}, {} \n".format(f, pred_class, score)
        neg_iter.set_description("{}: class {}, score {}".format(f, pred_class, score))
        true_neg -= len(pred_class)
    with open("test/negresults_{}.txt".format(datetime.now().strftime("%Y%m%d%H%M")), mode="w") as f:
        f.write(result)
    print('真陰性率：{:.2f}%'.format(true_neg / total_neg*100))

if __name__ == '__main__':
    # モデルを読み込む
    yolo = YOLO()

    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    """
    コマンドライン引数
    """
    parser.add_argument(
        '-c', '--camera', default=False, action="store_true",
        help='カメラ検出モード'
    )

    parser.add_argument(
        '-f', '--file', default=False, action="store_true",
        help='ファイル検出モード'
    )

    FLAGS = parser.parse_args()

    if FLAGS.file:
        eval()

    elif FLAGS.camera:
        while True:
            key = input('商品をスキャンします。「Enter」を押して下さい')

            if key == 'q':
                break

            photo_filename = '/tmp/data.jpg'

            with picamera.PiCamera() as camera:
                camera.resolution = (300,400)
                camera.start_preview()
                camera.capture(photo_filename)
            #try:
            image = Image.open(photo_filename)
            image = ImageOps.flip(image)
            image = ImageOps.mirror(image)
            #except:
                #print('読込みエラー、再度入力お願いします。')

            #else:
            output_dir = 'output/'

            time = datetime.now().strftime('%Y%m%d%H%M%S')

            pred, score, r_image = yolo.detect_image(image)

            image_path = output_dir + 'result_{}.jpg'.format(time)
            r_image.save(image_path)
            predict.show_image(image_path)
