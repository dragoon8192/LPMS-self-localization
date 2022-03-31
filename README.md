# LPMS-B2 を用いた位置推定プログラム LPMS-self-localization

**LPMS-self-localization** は LPMS-B2 のデータから装置の位置を推定するプログラムである．

**LPMS-B2** は加速度，角速度，磁場それぞれについて三軸のセンサーを持つ装置である．
センサーの測定データの時間変化に加え，測定データから計算された装置自身の姿勢（向きと回転）を csv として出力できる．

LPMS-self-localization は LPMS-B2 の出力した加速度と姿勢のデータを入力としてうけとる．
回転操作とフィルター，積分計算を行い，装置の速度と位置を推定して csv として出力する．

```sh
$ < in.csv | ./lpms_self_localization.py | out.csv
```

---

# LPMS-B2

## LPMS-B2 の操作説明

まず， LPMS-B2の取り扱いについて以下に示す．
詳しくは[公式サイト](https://lp-research.com/9-axis-bluetooth-imu-lpmsb2-series/)を参照すること．

### 本体の充電

USB ケーブルによって充電を行う．装置の状態と充電状況は LED に表示される．

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

**設定** > **デバイス** > **Bluetooth とその他のデバイス** の順で選択する．
「**Bluetooth またはその他のデバイスを追加する**」 から **LPMSB2-xxxxxx** を追加する．
（接続時 PIN コードの入力を求められた場合，**1234** を入力する．）

### LPMS-Control のインストール

[インストーラー](https://lp-software-downloads.s3-ap-northeast-1.amazonaws.com/LPMS/LPMS-Control/OpenMAT-1.3.5-Setup-Build20180418.exe)をダウンロードし，指示に従う．

### LPMS-Control の設定

インストールされた LPMS-Control を起動する．

ツールバーの![Add / remove sensor](./img/icons/plus_32x32.png "Add / remove sensor")を選択する．
**Scan devices** から，上で接続したデバイスを選択し，**Add device** を実行する．

ツールバーの![Connect](./img/icons/bolt_32x32.png)を選択し，接続を行う．
ウィンドウの左側 **Connected devices** に，接続済みのデバイス一覧が表示される．
これをクリックすると，デバイスごとに計測についての設定ができる．

### 計測の実行

#### データの記録をしない計測

ツールバーの![Start measurement](./img/icons/play_24x32.png)を選択することで計測が開始し，画面のグラフが更新される．

ツールバーの![Stop measurement](./img/icons/pause_24x32.png)を選択することでグラフの更新が停止される．

#### データの記録をする計測

ツールバーの![Browse record file](./img/icons/folder_stroke_32x32.png)を選択することで，計測データの保存先を指定する．

ツールバーの![Record data](./img/icons/layers_32x28.png)を選択することでで画面のグラフが更新され，記録を開始する．

ツールバーの![Stop recording](./img/icons/x_alt_32x32.png)を選択することで記録が終了し，データが保存される．

---

# LPMS-self-localization

## 実行環境

- OS
    - Windows10
- 言語
    - Python 3.10.2

## LPMS-self-localization の操作説明

LPMS-self-localization はコマンドラインアプリケーションである．

以下，スクリプト本体である`lpms_self_localization.py`と入力ファイル`in.csv`がカレントディレクトリに存在するとして手順を解説する．
実際の環境に応じて適宜読み替えてほしい．

## LPMS-self-localization が行う処理の説明

![flowchart](./img/flowchart.svg)

