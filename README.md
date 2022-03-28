# LPMS-B2 を用いた位置推定プログラム

## 概要

LPMS-B2 は加速度，角速度，磁場それぞれについて三軸のセンサーを持ち，装置の姿勢を計算して csv として出力できる．

このプログラムは LPMS-B2 のデータから位置を推定する．

## LPMS-B2 について

詳しくは[公式サイト](https://lp-research.com/9-axis-bluetooth-imu-lpmsb2-series/)を参照．



## LPMS-B2 の操作説明

### 本体の充電

|      |LED         |色|バッテリー|
|------|------------|--|----------|
|未接続|点滅        |青|>10%      |
|      |            |赤|<10%      |
|接続  |ゆっくり点滅|青|>10%      |
|      |            |赤|<10%      |
|充電中|点灯        |緑|>90%      |
|      |            |青|20% ~ 90% |
|      |            |赤|<20%      |

### Windows 設定

「設定」 > 「デバイス」 > 「Bluetooth とその他のデバイス」のの順で選択する．
「Bluetooth またはその他のデバイスを追加する」から「LPMSB2-xxxxxx」を追加する．

### LPMS - Control のインストール

<https://lp-software-downloads.s3-ap-northeast-1.amazonaws.com/LPMS/LPMS-Control/OpenMAT-1.3.5-Setup-Build20180418.exe> からインストーラーをダウンロードし，指示に従う．


