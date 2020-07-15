import numpy as np
import sys
import glob
import argparse
import ntpath
from yolo import YOLO
from PIL import Image
from datetime import datetime
from contextlib import redirect_stdout
from tqdm import tqdm
# warning処理
import warnings
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    # モデルを読み込む
    yolo = YOLO()
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
