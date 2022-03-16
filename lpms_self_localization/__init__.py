#! /usr/bin/env python
import sys
import pandas as pd
import numpy as np
import quaternion
from scipy import fftpack as fft
from scipy import integrate
from scipy import signal
from matplotlib import pyplot as plt

__version__ = '0.1.0'

def plotInit():
    # plot 初期化
    # フォント指定
    plt.rcParams['font.size'] = 10
    plt.rcParams['font.family'] = 'Times New Roman'
    # 目盛を内側に
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

def plot1(df):
    plotInit()
    fig, ax= plt.subplots()
    # df . plot( ax=ax, x='TimeStamp (s)' )
    df.plot(ax=ax)
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    return fig, ax

def plot6(dfs):
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

def dfQuatRotation( df : pd.DataFrame, vectCols : list, quatCols : list, newColNames : list ):
    # DataFrame の vect ( 3列 ) を quat ( 4列 ) で回転する
    index = df.index
    vect = df[vectCols].to_numpy()
    quat = quaternion.as_quat_array( df[quatCols].to_numpy() )
    rotatedVect = quaternion.as_vector_part( quat.conjugate() * quaternion.from_vector_part( vect ) * quat )
    return pd.DataFrame( data=rotatedVect, index=index, columns=newColNames )

def dfIntegrate( df : pd.DataFrame, newColNames : list ):
    # DataFrame を index/1000000 で積分する
    # index の単位を micro s とすることで時間積分となる
    index = df.index
    arr = df.to_numpy()
    arrInt = integrate.cumtrapz( arr, x=index.to_numpy() / 1000000, axis=0, initial=0 )
    return pd.DataFrame( data=arrInt, index=index, columns=newColNames )

def dfFFT( df : pd.DataFrame, newIndexName):
    index = df.index . rename( newIndexName )
    columns = df.columns
    arr = df.to_numpy()
    arrFFT = fft.fft( arr, axis=0 )
    return pd.DataFrame( data=arrFFT, index=index, columns=columns )

def dfFilter( df : pd.DataFrame, fs ):
    return df

def main():
    # 重力加速度
    g = 9.80665
    # 列名
    sTimeStamp   = 'TimeStamp (s)'
    sQuats       = ['QuatW', 'QuatX', 'QuatY', 'QuatZ']
    sLinAccs     = ['LinAccX (g)', 'LinAccY (g)', 'LinAccZ (g)']
    sGlbLinAccs  = ['GlbLinAccX (m/s^2)', 'GlbLinAccY (m/s^2)', 'GlbLinAccZ (m/s^2)']
    sGlbVels     = ['GlbVelX (m/s)', 'GlbVelY (m/s)', 'GlbVelZ (m/s)']
    sGlbPoss     = ['GlbPosX (m)', 'GlbPosY (m)', 'GlbPosZ (m)']
    # 補完方法
    method = 'linear'

    # 標準入力の csv から、必要な列を DataFrame に
    dfInput = pd.read_csv( sys.stdin, engine='python', sep=',\s+' )

    # TimeStamp 列を float (s) から int (micro s) に変換し、 index に指定
    timeStampMicroS= round( dfInput[ sTimeStamp ] * 1000000 ) . rename( 'TimeStamp (micro s)' ) . astype(int)
    dfInput.index = timeStampMicroS
    # データのサンプリング周期として TimeStamp (micro s) の差分の最頻値を取る
    samplingCycle = int( timeStampMicroS. diff() . mode() [0] )
    samplingFreq = int( 1000000 / samplingCycle )
    samplingTime = timeStampMicroS. iloc[-1]
    # クォータニオンによる回転を行い，グローバル座標での加速度を得る
    glbLinAcc = g * dfQuatRotation( dfInput, sLinAccs, sQuats, sGlbLinAccs )
    # データの抜けを補完
    glbLinAcc = glbLinAcc . reindex( range( 0, samplingTime + 1, samplingCycle ) ) . interpolate( method=method , axis='index' )
    # 時間積分
    glbVel = dfIntegrate( glbLinAcc, sGlbVels )
    glbPos = dfIntegrate( glbVel, sGlbPoss )

    # stdout に csv
    # pd.concat( [ glbLinAcc, glbVel, glbPos ], axis=1 ) . to_csv( sys.stdout )

    fftLinAcc = abs( dfFFT( glbLinAcc, 'Frequency (nHz)' ) )
    fftVel = abs( dfFFT( glbVel, 'Frequency (nHz)' ) )
    fftPos = abs( dfFFT( glbPos, 'Frequency (nHz)' ) )
    fig, ax = plot6( [glbLinAcc, glbVel, glbPos, fftLinAcc.query('index <= 1000000'), fftVel.query('index <= 1000000'), fftPos.query('index <= 1000000')] )
    fig.savefig('out/tmp.png')

if __name__ == '__main__':
    main()
