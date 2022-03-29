# LPMS-B2 を用いた位置推定プログラム

## 概要

LPMS-B2 は加速度，角速度，磁場それぞれについて三軸のセンサーを持ち，装置の姿勢を計算して csv として出力できる．

このプログラムは LPMS-B2 のデータから位置を推定する．

## 実行環境

- OS
    - Windows10
- 言語
    - Python 3.10.2

## LPMS-B2 の操作説明

詳しくは[公式サイト](https://lp-research.com/9-axis-bluetooth-imu-lpmsb2-series/)を参照．

### 本体の充電

|      |LED         |色|バッテリー|
|------|:----------:|--|---------:|
|未接続|点滅        |青|> 10%     |
|      |            |赤|< 10%     |
|接続  |ゆっくり点滅|青|> 10%     |
|      |            |赤|< 10%     |
|充電中|点灯        |緑|> 90%     |
|      |            |青|20% ~ 90% |
|      |            |赤|< 20%     |

### Windows 設定

「設定」 > 「デバイス」 > 「Bluetooth とその他のデバイス」のの順で選択する．
「Bluetooth またはその他のデバイスを追加する」から「LPMSB2-xxxxxx」を追加する．

### LPMS-Control のインストール

[インストーラー](https://lp-software-downloads.s3-ap-northeast-1.amazonaws.com/LPMS/LPMS-Control/OpenMAT-1.3.5-Setup-Build20180418.exe)をダウンロードし，指示に従う．

### LPMS-Control の設定

LPMS-Control を起動し，ツールバーの![Add / remove sensor](./img/icons/plus_32x32.png "Add / remove sensor")を選択する．

「Scan devices」から，上で接続したデバイスを選択し，「Add device」を実行する．

ツールバーの![Connect](./img/icons/bolt_32x32.png)を選択し，接続を行う．

:::note info
ウィンドウの左側「Connected devices」に，接続済みのデバイス一覧が表示される．
これをクリックすると，デバイスごとに計測についての設定ができる．
:::

### 計測の実行

#### データの記録をしない計測

ツールバーの![Start measurement](./img/icons/play_24x32.png)を選択することで計測が開始し，画面のグラフが更新される．

ツールバーの![Stop measurement](./img/icons/pause_24x32.png)を選択することでグラフの更新が停止される．

#### データの記録をする計測

ツールバーの![Browse record file](./img/icons/folder_stroke_32x32.png)を選択することで，計測データの保存先を指定する．

ツールバーの![Record data](./img/icons/layers_32x28.png)を選択することでで画面のグラフが更新され，記録を開始する．

ツールバーの![Stop recording](./img/icons/x_alt_32x32.png)を選択することで記録が終了し，データが保存される．
