import sys
import argparse
import ntpath
import picamera
from yolo import YOLO
from PIL import Image

photo_filename = '/tmp/data.jpg'

def shutter():
    photofile = open(photo_filename, 'wb')
    print(photofile)

    # pi camera 用のライブラリーを使用して、画像を取得
    with picamera.PiCamera() as camera:
        #camera.resolution = (640,480)
        camera.resolution = (300,400)
        camera.start_preview()
        sleep(1.000)
        camera.capture(photofile)

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

    FLAGS = parser.parse_args()

    # モデルを読み込む
    yolo = YOLO()

    if FLAGS.camera:
        """
        カメラ検出
        """
        while True:
            key = input('商品をスキャンする場合は「Enter」を押して下さい')
            shutter()
            try:
                image = Image.open(photo_filename)
            except:
                print('読込みエラー、再度入力お願いします。')
                continue
            else:
                output_dir = 'output/'
                _, file_name = ntpath.split(photo_filename)

                pred, score, r_image = yolo.detect_image(image)
                r_image.save(output_dir + 'result_{}.jpg'.format(file_name.replace('.jpg', '')))


    elif FLAGS.file:
        """
        データファイル検出
        """
        while True:
            img = input('ファイルパスを入力してください: ')
            try:
                image = Image.open(img)
            except:
                print('読込みエラー、再度入力お願いします。')
                continue
            else:
                output_dir = 'output/'
                _, file_name = ntpath.split(img)

            pred, score, r_image = yolo.detect_image(image)
            r_image.save(output_dir + 'result_{}.jpg'.format(file_name.replace('.jpg', '')))

    yolo.close_session()
