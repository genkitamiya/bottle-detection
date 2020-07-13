import numpy as np
import sys
import glob
import argparse
import ntpath
from yolo import YOLO
from PIL import Image
from contextlib import redirect_stdout
# warning処理
import warnings
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    # モデルを読み込む
    yolo = YOLO()
    path = './samples_test/*.jpg'
    test_files = glob.glob(path)
    preds = []
    for f in test_files:
        img = Image.open(f)
        pred_class, _, _ = yolo.detect_image(img)
        preds.append(pred_class)

    print(preds)
