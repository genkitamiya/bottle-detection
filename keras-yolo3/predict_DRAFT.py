import numpy as np
import sys
import argparse
import ntpath
import matplotlib.pyplot as plt
import picamera
import pygame.mixer
import analyze
import subprocess
from datetime import datetime
from yolo import YOLO
from PIL import Image, ImageOps, ImageTk
import tkinter as tk
from time import sleep
from timeit import default_timer as timer
import pandas as pd
from datetime import datetime
import os
from contextlib import redirect_stdout
# warning処理
import warnings
warnings.filterwarnings('ignore')

photo_filename = '/tmp/data.jpg'

def is_registered(x):
    # 登録済みかチェックするやつ
    # return x == 39
    return x in range(len(class_dic))

def shutter():

    # 音声再生
    read_sound.play(1)
    sleep(0.5)
    # 再生の終了
    read_sound.stop()
    # pi camera 用のライブラリーを使用して、画像を取得
    with picamera.PiCamera() as camera:
        camera.resolution = (300,400)
        camera.start_preview()
        sleep(0.5)
        camera.capture(photo_filename)

def scan():
    shutter()
    try:
        image = Image.open(photo_filename)
        image = ImageOps.flip(image)
        image = ImageOps.mirror(image)
    except:
        print('読込みエラー、再度入力お願いします。')
    else:
        output_dir = 'output/'
        _, file_name = ntpath.split(photo_filename)

        time = datetime.now().strftime('%Y%m%d%H%M%S')

        start = timer()
        pred, score, r_image = yolo.detect_image(image)
        end = timer()
        print('検出にかかった時間：{:.3f}秒'.format(end - start))

        image_path = output_dir + 'result_{}.jpg'.format(time)
        r_image.save(image_path)
        show_image(image_path)

    return pred, score

def show_image(image_path:str):

    width = 300*2
    height = 400*2

    # tkwindow作成
    root = tk.Tk()
    root.title('prediction')
    root.geometry(str(width) + 'x' + str(height))
    
    # imageを開く
    with Image.open(image_path) as img:
        img = img.resize((width, height), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        # canvas作成
        canvas = tk.Canvas(bg = "black", width=width, height=height)
        canvas.place(x=0, y=0)
        item = canvas.create_image(0, 0, image=img, anchor=tk.NW)
        root.after(5000, root.destroy)
        # 表示
        root.mainloop()

def initialize_model():
    """
    システム起動時処理
    yoloの準備運動
    """
    image = Image.open('../samples/output.jpg')
    _, _, _ = yolo.detect_image(image)

def check_book(datestr:str):
    """
    当日分の帳簿の存在確認など
    datastrのformat: %Y%m%d
    ./books 以下にsales_%Y%m%d.csvの形式で書き込み
    """
    book_path = './books/sales_' + datestr + '.csv'
    # 本日分の帳簿の存在確認
    if os.path.isfile(book_path):
        tmp_df = pd.read_csv(book_path, index_col=0)
        # 記帳済み確認
        if len(tmp_df.index) > 0:
            # 帳簿最終行のindex
            last_index = len(tmp_df.index) - 1
            # 帳簿最終行の顧客ID
            last_cus_id = int(tmp_df.tail(1)['customerID'].values)
        else:
            # ファイルだけ作成されて記帳されていない場合
            last_index = -1
            last_cus_id = -1
    else:
        # 帳簿CSV新規作成
        tmp_df = pd.DataFrame(index=[], columns=['saletime', 'customerID', 'prodname', 'prodprice'])
        tmp_df.to_csv(book_path)
        last_index = -1
        last_cus_id = -1

    return last_index, last_cus_id, book_path

if __name__ == '__main__':
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

    # parser.add_argument(
    #     '-s', '--sales', default=False, action="store_true",
    #     help='売上帳簿出力'
    # )

    FLAGS = parser.parse_args()

    # モデルを読み込む
    yolo = YOLO()

    # 音声ファイル初期化

    pygame.mixer.init()
    read_sound = pygame.mixer.Sound("Cash_Register-Beep01-1+6.wav")
    warn_sound = pygame.mixer.Sound("error2.wav")

    # 商品名・価格を読み込む
    class_dic = pd.read_csv('products.csv').set_index('id').T.to_dict(orient='list')
    # {0:['GEORGIA ブラックコーヒー', 150],
    #  1:['コカ・コーラ', 120],
    #  2:['午後の紅茶レモンティー', 150],
    #  3:['ポカリスエット', 150],
    #  4:['綾鷹', 130]}

    # セルフレジシステム起動
    while True:
        # 起動時処理
        with redirect_stdout(open(os.devnull, 'w')):
            initialize_model()

        tmp = input('Welcome!(press enter)')
        # 'q'が入力されたら終了する
        if tmp == 'q':
            break
        # 'b'が入力されたら音声再生
        elif tmp == 'b':
            # 音声再生
            warn_sound.play(1)
            sleep(1)
            # 再生の終了
            pygame.mixer.music.stop()
        # 's'が入力されたら売上分析を開始
        elif tmp == 's':
            """
            売上分析モード
            """
            analyze.initiate('./books/')
            continue

        # 会計開始
        checkout_list = []
        while True:

            if FLAGS.camera:
                """
                カメラ検出
                """
                key = input('商品をスキャンします。「Enter」を押して下さい')
                pred, score = scan()

            elif FLAGS.file:
                """
                データファイル検出
                """
                img = input('ファイルパスを入力してください: ')
                try:
                    image = Image.open(img)
                except:
                    print('読込みエラー、再度入力お願いします。')
                    continue
                else:
                    output_dir = 'output/'
                    _, file_name = ntpath.split(img)

                    start = timer()
                    pred, score, r_image = yolo.detect_image(image)
                    end = timer()
                    print('検出にかかった時間：{:.3f}秒'.format(end - start))

                    image_path = output_dir + 'result_{}.jpg'.format(file_name.replace('.jpg', ''))
                    r_image.save(image_path)
                    show_image(image_path)

            # 未登録商品検出(消すかも)
            if not all([is_registered(x) for x in pred]):
                key = input('未登録商品を検出しました。再度読み込みますか？ \nはい[y]、いいえ[n]？')
                if key == 'y':
                    continue
                else:
                    print('未登録商品はお会計されません。')
                    pred = [x for x in pred if is_registered(x)] # 未登録商品を削る

            # 登録済み商品検出*なし*
            if len(pred) == 0:
                key = input('商品を検出しませんでした。再度読み込みますか？ \nはい[y]、いいえ[n]？')
                if key == 'y':
                    continue
                else:
                    pass

            # 登録済み商品検出*あり*
            else:
                for i, item in enumerate(pred):
                    print('商品番号{} {}の金額は¥{}'.format(i, class_dic[item][0], class_dic[item][1]))

                # 商品選択
                while True:
                    key = input('お会計を行いたい商品番号を入力してください。(例：0 3 5): ')
                    prod_ids = set(map(int, key.split()))
                    # prod_idがpredに対してOutOfIndexでないかチェック
                    if not all([prod_id in range(len(pred)) for prod_id in prod_ids]):
                        print('商品番号の誤りを検知しました。0-{}の間の番号を入力してください'.format(len(pred)-1))
                        continue
                    # 全部範囲内ならbreak
                    break

                # pred内のindexから商品IDに変換する
                items = [pred[x] for x in prod_ids]
                # カゴに追加
                checkout_list.extend(items)

            # 買い物カゴの状態に応じたメッセージを表示
            if len(checkout_list) > 0:
                print('買い物カゴに次の商品が入っています。')
                for item in checkout_list:
                    print('{} ¥{}'.format(class_dic[item][0], class_dic[item][1]))
            else:
                print('買い物カゴは空です。')

            # 会計終了プロセス
            key = input('他の商品もお会計しますか？ \nはい[y]、いいえ[n]？')
            if key=='y':
                continue
            else:
                break
        print('合計金額は¥{}です。'.format(sum([class_dic[x][1] for x in checkout_list])))
        print('ありがとうございました。')

        # 記帳
        sale_date = datetime.now()
        sale_date_str = sale_date.strftime('%Y%m%d')
        # 帳簿チェック
        last_index, last_cus_id, book_path = check_book(sale_date_str)

        # DataFrame作成
        tmp_df = pd.DataFrame(index=range(last_index+1, last_index+1+len(checkout_list)),
                              data={
                                  'saletime': [sale_date.strftime('%Y/%m/%d %H:%M:%S')] * len(checkout_list),
                                  'customerID': [last_cus_id+1] * len(checkout_list),
                                  'prodname': [class_dic[item][0] for item in checkout_list],
                                  'prodprice': [class_dic[item][1] for item in checkout_list],
                              },
                              columns=['saletime', 'customerID', 'prodname', 'prodprice'])

        # ファイル書き込み
        tmp_df.to_csv(book_path, mode='a', header=False)

        # last_*書き換え
        last_index = last_index+1+len(checkout_list)
        last_cus_id = last_cus_id+1

    print('Bye!')
    yolo.close_session()
