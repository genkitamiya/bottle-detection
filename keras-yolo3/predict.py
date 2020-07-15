import argparse
import ntpath
import picamera
import pygame.mixer
from datetime import datetime
from yolo import YOLO
from PIL import Image, ImageOps, ImageTk
import tkinter as tk
from time import sleep
from timeit import default_timer as timer
import pandas as pd
import os
import sys
from contextlib import redirect_stdout
# warning処理
import warnings
warnings.filterwarnings('ignore')
# 自作系
from registerutil import y_n_input
import analyze

# 撮影した写真データの保存場所
photo_filename = '/tmp/data.jpg'

def is_registered(x:int, class_dictionary:dict) -> bool:
    """
    登録済みかチェックするやつ
    """
    #return x == 39
    #return x in range(len(class_dictionary) - 1)
    return x in range(len(class_dictionary))

def shutter():
    """
    音出して写真をとる。
    ピッと鳴る。
    """
    # 音声再生
    read_sound.play()
    sleep(1)
    # 再生の終了
    read_sound.stop()
    # pi camera 用のライブラリーを使用して、画像を取得
    with picamera.PiCamera() as camera:
        camera.resolution = (300,400)
        camera.start_preview()
        sleep(2)
        camera.capture(photo_filename)

def scan():
    """
    shutterで写真を取って商品を検出する。
    予測クラス(商品ID)とscoreを返す
    """
    shutter()

    try:
        image = Image.open(photo_filename)
        image = ImageOps.flip(image)
        image = ImageOps.mirror(image)
    except:
        print('読込みエラー、再度入力お願いします。')
    else:
        output_dir = 'output/'

        time = datetime.now().strftime('%Y%m%d%H%M%S')

        start = timer()
        pred, score, r_image = yolo.detect_image(image)
        end = timer()
        print('検出にかかった時間：{:.3f}秒'.format(end - start))

        image_path = output_dir + 'result_{}.jpg'.format(time)
        r_image.save(image_path)
        show_image(image_path)

    return pred, score

def show_image(image_path:str, window_title='prediction', duration=5000, scale=2):
    """
    一定時間画像を表示
    推定結果を表示する際に使用
    window_title : 画像表示窓のタイトル
    duration : 表示時間(ms)
    scale : 画像の拡大倍率
    """

    # imageを開く
    with Image.open(image_path) as img:
        # 画像サイズ取得
        width = img.width * scale
        height = img.height * scale

        # tkwindow作成
        root = tk.Tk()
        root.title(window_title)
        root.geometry(str(width) + 'x' + str(height))

        img = img.resize((width, height), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        # canvas作成
        canvas = tk.Canvas(bg = "black", width=width, height=height)
        canvas.place(x=0, y=0)
        item = canvas.create_image(0, 0, image=img, anchor=tk.NW)
        root.after(duration, root.destroy)

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
    datastrのformat: %Y%m%d (当日日付)
    ./books 以下にsales_%Y%m%d.csvの形式で書き込み
    
    *return*
    last_index:int
      帳簿の売上商品IDの最後の数
    last_cus_id:
      帳簿のお客様IDの最後の数
    book_path:str
      帳簿の相対パス
      書き込み時に使用
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

    # -cと-fどちらも指定されている/どちらも指定されていない場合異常終了
    if (not FLAGS.camera and not FLAGS.file) or (FLAGS.camera and FLAGS.file):
        print("\
Specify one of the optional arguments: -c, -f\n\
  -c: camera mode\n\
  -f: file mode")
        sys.exit(1)

    # モデルを読み込む
    yolo = YOLO()

    # 音声ファイル初期化

    pygame.mixer.init()
    read_sound = pygame.mixer.Sound("Cash_Register-Beep01-1+6.wav")
    warn_sound = pygame.mixer.Sound("error2.wav")
    guide_voice1 = pygame.mixer.Sound("./guide_sounds/Please_press_ENTER.wav")
    guide_voice2 = pygame.mixer.Sound("./guide_sounds/Please_place_the_products_under_the_camera_and_press_enter.wav")
    guide_voice3 = pygame.mixer.Sound("./guide_sounds/Please_enter_the_item_number_you_wish_to_check_out.wav")
    guide_voice4 = pygame.mixer.Sound("./guide_sounds/Would_you_like_to_check_for_other_items.wav")
    guide_voice5 = pygame.mixer.Sound("./guide_sounds/Thank_you_Have_a_nice_day.wav")
    
    # 商品名・価格を読み込む
    cls_dic = pd.read_csv('products.csv').set_index('id').T.to_dict(orient='list')
    # {0:['GEORGIA ブラックコーヒー', 150],
    #  1:['コカ・コーラ', 120],
    #  2:['午後の紅茶レモンティー', 150],
    #  3:['ポカリスエット', 150],
    #  4:['綾鷹', 130]}
    # → 一番最後のカテゴリが「未登録」になるかも？

    # 起動時処理
    with redirect_stdout(open(os.devnull, 'w')):
        initialize_model()

    # セルフレジシステム起動
    while True:
        
        # terminalのクリア
        os.system('clear')
        
        print('\
# # # # # # # # # # # # # # # # # # # # # # # # # # # #\n\
    /MME          JMMMMMMMF  /MMMME  /MME      /MM  /ME\n\
   /M/ME            /MF     /#/     /M/ME     /M/M /VME\n\
  /M/ ME  MMMMMM   /MF     /MMME   /M/ ME    /M/ M/V ME\n\
 /MM##ME          /MF     /#/     /MM##ME   /M/  MV  ME\n\
/M/   ME         /ME     /MMMME  /M/   ME  /M/       ME\n\
# # # # # # # # # # # # # # # # # # # # # # # # # # # #\n')

        # 音声案内「エンターを押してください」
        sleep(1)
        guide_voice1.play()
        sleep(2)
        guide_voice1.stop()
        
        tmp = input('Welcome! (press enter)')
        # 'q'が入力されたら終了する
        if tmp == 'q':
            break
        # 'b'が入力されたら音声再生
        elif tmp == 'b':
            # 音声再生
            warn_sound.play()
            sleep(1)
            # 再生の終了
            pygame.mixer.music.stop()
            continue
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
                # 音声案内「商品を置いてください」
                guide_voice2.play()
                sleep(4)
                guide_voice2.stop()
                
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
            if not all([is_registered(x, cls_dic) for x in pred]):
                print('未登録商品を検出しました。再度読み込みますか？')
                key = y_n_input()
                if key:
                    continue
                else:
                    print('未登録商品はお会計されません。')
                    pred = [x for x in pred if is_registered(x, cls_dic)] # 未登録商品を削る

            # 登録済み商品検出*なし*
            if len(pred) == 0:
                print('商品を検出しませんでした。再度読み込みますか？')
                key = y_n_input()
                if key:
                    continue
                else:
                    pass

            # 登録済み商品検出*あり*
            else:
                for i, item in enumerate(pred):
                    print('商品番号{} {}の金額は¥{}'.format(i, cls_dic[item][0], cls_dic[item][1]))

                # 商品選択
                while True:
                    
                    # 音声案内「会計する商品を選んでください」
                    guide_voice3.play()
                    sleep(3)
                    guide_voice3.stop()
                    
                    key = input('お会計を行いたい商品番号を入力してください。(例：0 3 5): ')
                    
                    try:
                        prod_ids = set(map(int, key.split()))
                        # pred内のindexから商品IDに変換する
                        items = [pred[x] for x in prod_ids]
                        break
                    except:
                        # value check
                        print('商品番号の誤りを検知しました。0-{}の間の番号を入力してください'.format(len(pred)-1))
                        continue
                    
                # カゴに追加
                checkout_list.extend(items)

            # 買い物カゴの状態に応じたメッセージを表示
            if len(checkout_list) > 0:
                print('買い物カゴに次の商品が入っています。')
                for item in checkout_list:
                    print('{} ¥{}'.format(cls_dic[item][0], cls_dic[item][1]))
            else:
                print('買い物カゴは空です。')

            # 音声案内「他の商品も会計しますか」
            guide_voice4.play()
            sleep(2.5)
            guide_voice4.stop()

            # 会計終了プロセス
            print('他の商品もお会計しますか？')
            key = y_n_input()
            if key:
                continue
            else:
                break

        print('合計金額は¥{}です。'.format(sum([cls_dic[x][1] for x in checkout_list])))
        print('ありがとうございました。')
        # 音声案内「ありがとうございました」
        guide_voice5.play()
        sleep(2)
        guide_voice5.stop()

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
                                  'prodname': [cls_dic[item][0] for item in checkout_list],
                                  'prodprice': [cls_dic[item][1] for item in checkout_list],
                              },
                              columns=['saletime', 'customerID', 'prodname', 'prodprice'])

        # ファイル書き込み
        tmp_df.to_csv(book_path, mode='a', header=False)

        # last_*書き換え
        last_index = last_index+1+len(checkout_list)
        last_cus_id = last_cus_id+1

    print('Bye!')
    yolo.close_session()
    sys.exit(0)
