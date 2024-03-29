#! /usr/bin/env python
import sys
import argparse
import pandas as pd
import numpy as np
import quaternion
from scipy import fftpack as fft
from scipy import integrate
from scipy import signal
from matplotlib import pyplot as plt

def main():
    # 重力加速度
    g : float = 9.80665
    # 列名
    sTimeStamp       = 'TimeStamp (s)'
    sTimeStampMicroS = 'TimeStamp (micro s)'
    sQuats           = ['QuatW', 'QuatX', 'QuatY', 'QuatZ']
    sLinAccs         = ['LinAccX (g)', 'LinAccY (g)', 'LinAccZ (g)']
    sGlbAccs         = ['GlbAccX (m/s^2)', 'GlbAccY (m/s^2)', 'GlbAccZ (m/s^2)']
    sGlbVels         = ['GlbVelX (m/s)', 'GlbVelY (m/s)', 'GlbVelZ (m/s)']
    sGlbPoss         = ['GlbPosX (m)', 'GlbPosY (m)', 'GlbPosZ (m)']

    # 引数の処理
    parser = argparse.ArgumentParser( description='LPMS の出力した csv から位置を推定し， csv として出力します．' )
    parser.add_argument( 'input', type=argparse.FileType('r'), nargs='?', default=sys.stdin,
            help='入力ファイルを指定します． 指定がなければ標準入力を受け取ります．' )
    parser.add_argument( '-o', '--output', type=argparse.FileType('w'), default=sys.stdout,
            help='推定された加速度，速度，位置のデータを csv として出力する先を指定します． 指定がなければ標準出力に出力されます．' )
    parser.add_argument( '-p', '--plot',
            help='プロット (png) の出力先を選びます． 指定がなければ出力しません．' )
    parser.add_argument( '-f', '--freq', type=int,
            help='入力データのサンプリング周波数 (Hz) を指定します． 指定がなければデータから推定します．' )
    parser.add_argument( '-i', '--interpolate',
            help='抜け値の補完メソッドを指定します． pandas.DataFrame.interpolate によって補完が行われます． 指定がなければ線形補完です．', default='linear' )
    parser.add_argument( '--no-noize-reduction', action='store_true',
            help='ノイズ除去を無効化します．')
    # parser.add_argument( '--acc-filter', nargs=2, default=[0.1, 0.3], type=float,
    #         help='加速度に対するハイパスフィルターの阻止域端周波数 [Hz] と通過域端周波数 [Hz] を指定します． 指定がなければ 0.1, 0.3 とします．')
    # parser.add_argument( '--no-acc-filter', action='store_true',
    #         help='加速度に対するハイパスフィルターを無効化します．')
    # parser.add_argument( '--vel-filter', nargs=2, default=[0.1, 0.3], type=float,
    #         help='速度に対するハイパスフィルターの阻止域端周波数 [Hz] と通過域端周波数 [Hz] を指定します． 指定がなければ 0.1, 0.3 とします．')
    # parser.add_argument( '--no-vel-filter', action='store_true',
    #         help='速度に対するハイパスフィルターを無効化します．')
    # parser.add_argument( '--pos-filter', nargs=2, default=[0.1, 0.3], type=float,
    #         help='位置に対するハイパスフィルターの阻止域端周波数 [Hz] と通過域端周波数 [Hz] を指定します． 指定がなければ 0.1, 0.3 とします．')
    # parser.add_argument( '--no-pos-filter', action='store_true',
    #         help='位置に対するハイパスフィルターを無効化します．')
    args = parser.parse_args()

    # 標準入力の csv から、必要な列を DataFrame に
    dfInput = pd.read_csv( args.input, engine='python', sep=',\s+' )
    # TimeStamp 列を float (s) から int (micro s) に変換し、 index に指定
    timeStampMicroS : pd.Index = round( dfInput[ sTimeStamp ] * 1000000 ) . rename( sTimeStampMicroS ) . astype(int)
    dfInput.index = timeStampMicroS
    if args.freq == None:
        # データのサンプリング周期 (micro s) として TimeStamp (micro s) の差分の最頻値を取る
        samplingCycle : int = int( timeStampMicroS. diff() . mode() [0] )
        # サンプリング周波数 (Hz)
        samplingFreq  : int = int( 1000000 / samplingCycle )
    else:
        samplingFreq  : int = args.freq
        samplingCycle : int = int( 1000000 / samplingFreq )
    samplingTime : int = timeStampMicroS. iloc[-1]

    # クォータニオンによる回転を行い，グローバル座標での加速度を得る
    glbAcc = g * dfQuatRotation( dfInput, sLinAccs, sQuats, sGlbAccs )
    # データの抜けを args に従い補完
    glbAcc = glbAcc . reindex( range( 0, samplingTime + 1, samplingCycle ) ) . interpolate( method=args.interpolate , axis='index' )
    # 絶対値が 0.1 m/s^2 未満のノイズを除去
    if not args.no_noize_reduction:
        glbAcc = dfNoizeReduction( glbAcc, 0.1 )
    # フィルタリングと時間積分を繰り返して速度と位置を得る
    # if not args.no_acc_filter:
    #     glbAcc = dfFilter( glbAcc, samplingFreq, args.acc_filter[1], args.acc_filter[0], 'high' )
    glbVel = dfIntegrate( glbAcc, sGlbVels )
    # if not args.no_vel_filter:
    #     glbVel = dfFilter( glbVel, samplingFreq, args.vel_filter[1], args.vel_filter[0], 'high' )
    glbPos = dfIntegrate( glbVel, sGlbPoss )
    # if not args.no_pos_filter:
    #     glbPos = dfFilter( glbPos, samplingFreq, args.pos_filter[1], args.pos_filter[0], 'high' )

    # csv を出力
    dfOutput = pd.concat( [ glbAcc, glbVel, glbPos ], axis=1 )
    dfOutput.index = ( dfOutput.index / 1000000 ) . rename( sTimeStamp )
    dfOutput . to_csv( args.output )

    # plot 用
    if args.plot != None:
        fftAcc = abs( dfFFT( glbAcc, samplingFreq ) )
        fftVel = abs( dfFFT( glbVel, samplingFreq ) )
        fftPos = abs( dfFFT( glbPos, samplingFreq ) )
        fig, ax = plot6( [glbAcc, glbVel, glbPos, fftAcc, fftVel, fftPos ] )
        fig.savefig( args.plot )

def dfQuatRotation( df : pd.DataFrame, vectCols : list, quatCols : list, newColNames : list ):
    # DataFrame の vect ( 3列 ) を quat ( 4列 ) で回転する
    index = df.index
    vect = df[vectCols].to_numpy()
    quat = quaternion.as_quat_array( df[quatCols].to_numpy() )
    rotatedVect = quaternion.as_vector_part( quat.conjugate() * quaternion.from_vector_part( vect ) * quat )
    # 回転したベクトルに新しい列名をつけて DataFrame として返す
    return pd.DataFrame( data=rotatedVect, index=index, columns=newColNames )

def dfNoizeReduction( df : pd.DataFrame, threshold : float ):
    index = df.index
    columns = df.columns
    arr = df.to_numpy()
    def func( xs ):
        norm = np.linalg.norm( xs )
        if norm >= threshold:
            return xs
        else:
            return np.zeros(3)
    arrRed = np.apply_along_axis( func, 1, arr)
    return pd.DataFrame( data=arrRed, index=index, columns=columns )

def dfIntegrate( df : pd.DataFrame, newColNames : list ):
    # DataFrame を index/1000000 で積分する
    # index の単位を micro s とすることで時間積分となる
    index = df.index
    arr = df.to_numpy()
    arrInt = integrate.cumtrapz( arr, x=index.to_numpy() / 1000000, axis=0, initial=0 )
    return pd.DataFrame( data=arrInt, index=index, columns=newColNames )

def dfFFT( df : pd.DataFrame, fSample ):
    # index を float (Hz) に
    index = pd.Index( np.linspace( 0, fSample, len(df) ), name='Frequency (Hz)' )
    columns = df.columns
    arr = df.to_numpy()
    arrFFT = fft.fft( arr, axis=0 )
    # ナイキスト周波数以降は切り捨て
    return pd.DataFrame( data=arrFFT, index=index, columns=columns ) . query('index <= ' + str( fSample/2 ))

def dfFilter( df : pd.DataFrame, fSample, fPass, fStop, bType ):
    # バターワースフィルタリングを行う
    index = df.index
    columns = df.columns
    arr = df.to_numpy()
    fNiquist = fSample / 2
    wPass = fPass / fNiquist
    wStop = fStop / fNiquist
    gPass = 3
    gStop = 40
    N, Wn = signal.buttord( wPass, wStop, gPass, gStop )
    b, a = signal.butter( N, Wn, bType)
    arrFilt = signal.filtfilt(b, a, arr, axis=0)
    return pd.DataFrame( data=arrFilt, index=index, columns=columns )

def plotInit():
    # plot 初期化
    # フォント指定
    plt.rcParams['font.size'] = 10
    plt.rcParams['font.family'] = 'Times New Roman'
    # 目盛を内側に
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

def plot1(df):
    # 1つのプロットを出力する
    plotInit()
    fig, ax= plt.subplots()
    df.plot(ax=ax)
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    return fig, ax

def plot6(dfs):
    # 6つのプロットを並べる
    plotInit()
    # Figure インスタンスを作成
    fig, axes = plt.subplots(2, 3, figsize=(12,7))
    i = 0
    for axarr in axes:
        for ax in axarr:
            dfs[i].plot(ax=ax)
            i += 1
            ax.xaxis.set_ticks_position('both')
            ax.yaxis.set_ticks_position('both')
    return fig, axes

if __name__ == '__main__':
    main()
