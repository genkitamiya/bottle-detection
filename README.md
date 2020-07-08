# bottle-detection
セルフレジのボトル検出するやつ
# あるもの
## keras-yolo3
- yolo検出のやつ
- 学習済みモデル
  - yolov3 (動作未確認)
  - tiny-yolo（2020/07/08 動作確認済み）

## self_checkout_DEMO
デモです！
- Self_checkout_yolo.py: セルフレジ実行スクリプトのデモ（2020/07/08 モデルをtiny-yoloに書き換え中）
## yolov3.weights & yolov3-tiny.weights
学習済みの重み

---
## 推定方法（二通り）
### A. keras.yolov3標準起動方法
```
python yolo_video.py --image
```
>- デフォルト推定モデルはtiny-yoloに変更済み（path指定だとエラーが起きたため→ 2020/07/08 確認)
>- 推定画像は**出力不可**
<br>

### B. セルフレジ用起動方法（仮）
```
python predict.py
```
>- セルフレジ用に特化するため、yolo_video.pyから不要なinput argumentsを削除
>- 推定画像の出力機能を追加（path: /output/result_[file name].jpg）
