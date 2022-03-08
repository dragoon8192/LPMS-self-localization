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
    df . plot( ax=ax, x='TimeStamp (s)' )
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
    index = df.index
    vect = df[vectCols].to_numpy()
    quat = q.as_quat_array( df[quatCols].to_numpy() )
    rotatedVect = q.as_vector_part( quat.conjugate() * q.from_vector_part( vect ) * quat )
    return pd.DataFrame( data=rotatedVect, index=index, columns=returnCols )

def main():
    TimeStamp   = 'TimeStamp (s)'
    Quats       = ['QuatW', 'QuatX', 'QuatY', 'QuatZ']
    LinAccs     = ['LinAccX (g)', 'LinAccY (g)', 'LinAccZ (g)']
    GlbLinAccs  = ['GlbLinAccX (m/s^2)', 'GlbLinAccY (m/s^2)', 'GlbLinAccZ (m/s^2)']
    GlbLinVels  = ['GlbLinVelX (m/s)', 'GlbLinVelY (m/s)', 'GlbLinVelZ (m/s)']
    GlbPoss     = ['GlbPosX (m)', 'GlbPosY (m)', 'GlbPosZ (m)']

    # 標準入力の csv から、必要な列を DataFrame に
    df = pd.read_csv( sys.stdin, engine='python', sep=',\s+',
            usecols=['TimeStamp (s)',
                'QuatW', 'QuatX', 'QuatY', 'QuatZ',
                'LinAccX (g)', 'LinAccY (g)', 'LinAccZ (g)' ] )
    # TimeStamp 列を Float から DateTime に変換し、 index に指定
    df.index = pd.to_datetime( df[ TimeStamp ], unit='s' ) . rename('DateTime')

    # 重力加速度
    g = 9.80665
    # データのサンプリング周期として TimeStamp の差分の最頻値を取る
    samplingCycle = str( round( 1000 * df[ TimeStamp ] . diff() . mode() [0] ) ) + 'ms'

    dfTime = df['TimeStamp (s)']
    time = dfTime.to_numpy()
    dfQuat = df[['QuatW', 'QuatX', 'QuatY', 'QuatZ']]
    quat = q.as_quat_array( dfQuat . to_numpy() )
    linAcc = df[['LinAccX (g)', 'LinAccY (g)', 'LinAccZ (g)']] . to_numpy()

    glbLinAcc = g * q.as_vector_part( quat.conjugate() * q.from_vector_part( linAcc ) * quat )
    glbLinVel = integrate.cumtrapz( glbLinAcc, time, axis=0, initial=0 )
    glbPos = integrate.cumtrapz( glbLinVel, time, axis=0, initial=0 )

    dfGlbLinAcc = pd.DataFrame( data=glbLinAcc,
            columns=['GlbLinAccX (m/s^2)', 'GlbLinAccY (m/s^2)', 'GlbLinAccZ (m/s^2)'] )
    dfGlbLinVel = pd.DataFrame( data=glbLinVel,
            columns=['GlbLinVelX (m/s)', 'GlbLinVelY (m/s)', 'GlbLinVelZ (m/s)'] )
    dfGlbPos = pd.DataFrame( data=glbPos,
            columns=['GlbPosX (m)', 'GlbPosY (m)', 'GlbPosZ (m)'] )

    # dfGlb = pd.concat( [ df, dfGlbLinAcc, dfGlbLinVel, dfGlbPos ], axis=1 )

    # fig, ax = plot6( dfGlb )

    # dfPlt = pd.concat( [ dfTime, dfGlbLinAcc ], axis=1 )
    # fig, ax = plot1(dfPlt)
    # fig.savefig('out/tmp.png')
    glbLinAcc2 = g * dfQuatRotation( df, LinAccs, Quats, GlbLinAccs ) . resample( samplingCycle ) . interpolate( method='quadratic' )



    print( glbLinAcc2 )
    print( dfGlbLinAcc )

    # stdout
    # dfGlb.to_csv( sys.stdout )

if __name__ == '__main__':
    main()
