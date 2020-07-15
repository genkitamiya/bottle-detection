# bottle-detection
raspiとraspicameraを用いて飲料商品を自動検出するセルフレジシステム。<br>
<br>
検出可能な商品は下記５種：

- コカ・コーラ
- 午後の紅茶レモンティー
- ジョージアコーヒー
- ポカリスエット
- 綾鷹


機能一覧：

- 商品の検出（複数可）
- 検出商品の商品名及び金額表示
- １日の売上金額のcsv書き出し
- 売上の分析（売上推移、商品毎の売上、など）

## モデル
Keras適合のtiny-yolov3を実装（[github](https://github.com/qqwweee/keras-yolo3.git))。YOLO作者が公開している（[YOLO website](http://pjreddie.com/darknet/yolo/)）学習済みモデルを初期重みとし、検出対象商品の画像データセットを転移学習させた。

---
# 起動方法
self-checkout.pyを実行
```
python self-checkout.py --camera # カメラ検出モード（-cでも可）
python self-checkout.py --file # ファイル検出モード（-fでも可）
```
>- Bounding Box付き推定画像を出力（path: /output/result_[file name].jpg）
>- カメラ・jpgファイル入力に対応

## 売上分析
self-checkout.py実行後、'Welcome! (press enter)'画面で's'を入力すると起動される。
