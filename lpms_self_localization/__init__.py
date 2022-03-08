#! /usr/bin/env python
import sys
import pandas as pd
import numpy as np
import quaternion as q
from scipy import integrate
from scipy import interpolate
from matplotlib import pyplot as plt

__version__ = '0.1.0'

def plotInit():
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

def plot6(df):
    plotInit()
    # Figure インスタンスを作成
    fig, axes = plt.subplots(2, 3, figsize=(12,7))
    df[['TimeStamp (s)', 'GlbLinAccX (m/s^2)', 'GlbLinAccY (m/s^2)', 'GlbLinAccZ (m/s^2)']] . plot( ax=axes[0][0], x='TimeStamp (s)' )

    for axarr in axes:
        for ax in axarr:
            ax.xaxis.set_ticks_position('both')
            ax.yaxis.set_ticks_position('both')
    return fig, axes

def dfQuatRotation( df : pd.DataFrame, vectCols : list, quatCols : list, returnCols : list ):
    # DataFrame の vect ( 3列 ) を quat ( 4列 ) で回転する
    index = df.index
    vect = df[vectCols].to_numpy()
    quat = q.as_quat_array( df[quatCols].to_numpy() )
    rotatedVect = q.as_vector_part( quat.conjugate() * q.from_vector_part( vect ) * quat )
    return pd.DataFrame( data=rotatedVect, index=index, columns=returnCols )

def dfIntegrate( df : pd.DataFrame, returnCols : list ):
    # DataFrame を index/1000000 で積分する
    # index の単位を ns とすることで時間積分となる
    index = df.index
    arr = df.to_numpy()
    arrInt = integrate.cumtrapz(arr, x=index.to_numpy() / 1000000, axis=0, initial=0 )
    return pd.DataFrame( data=arrInt, index=index, columns=returnCols )

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
    method = 'cubic'

    # 標準入力の csv から、必要な列を DataFrame に
    df = pd.read_csv( sys.stdin, engine='python', sep=',\s+' )

    # TimeStamp 列を float (s) から int (ns) に変換し、 index に指定
    ns = round( df[ sTimeStamp ] * 1000000 ) . rename( 'TimeStamp (ns)' ) . astype(int)
    df.index = ns
    # データのサンプリング周期として TimeStamp (ns) の差分の最頻値を取る
    samplingCycle = int( ns . diff() . mode() [0] )
    samplingTime = ns . iloc[-1]
    # クォータニオンによる回転を行い，グローバル座標での加速度を得る
    glbLinAcc = g * dfQuatRotation( df, sLinAccs, sQuats, sGlbLinAccs )
    # データの抜けを補完
    glbLinAcc = glbLinAcc . reindex( range( 0, samplingTime + 1, samplingCycle ) ) . interpolate( method=method , axis='index' )
    # 時間積分
    glbVel = dfIntegrate( glbLinAcc, sGlbVels )
    glbPos = dfIntegrate( glbVel, sGlbPoss )

    dfReturn = pd.concat( [ glbLinAcc, glbVel, glbPos ], axis=1 )
    # stdout
    # dfReturn.to_csv( sys.stdout )

    fig, ax = plot1( glbPos )
    fig.savefig('out/tmp.png')

if __name__ == '__main__':
    main()
