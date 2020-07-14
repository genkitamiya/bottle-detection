import numpy as np
import sys
import glob
import argparse
import ntpath
from yolo import YOLO
from PIL import Image
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
    for f in tqdm(glob.glob(pos_path)):
        img = Image.open(f)
        pred_class, _, _ = yolo.detect_image(img)
        # print(f, int(f[f.rfind("/")+1]), pred_class[0])
        cnt += int(f[f.rfind("/")+1]) == pred_class[0]
    print('正解率：{:.2f}%'.format(cnt / total_pos*100)) #Accuracy計算

    # 真陰性率計算
    total_neg = len(glob.glob(neg_path))
    true_neg = total_neg
    for f in tqdm(glob.glob(neg_path)):
        img = Image.open(f)
        pred_class, _, _ = yolo.detect_image(img)
        # print(len(pred_class))
        true_neg -= len(pred_class)
    print('真陰性率：{:.2f}%'.format(true_neg / total_neg*100))
