#! /usr/bin/env python
import sys
import pandas as pd
import numpy as np
import quaternion as q
from scipy import integrate

__version__ = '0.1.0'

def main():
    g = 9.80665
    df = pd.read_csv( sys.stdin, engine='python', sep=',\s+',
            usecols=['TimeStamp (s)', 'FrameNumber',
                'QuatW', 'QuatX', 'QuatY', 'QuatZ',
                'LinAccX (g)', 'LinAccY (g)', 'LinAccZ (g)' ])
    time = df['TimeStamp (s)'] . to_numpy()
    quat = q.as_quat_array( df[['QuatW', 'QuatX', 'QuatY', 'QuatZ']] . to_numpy() )
    linAcc = df[['LinAccX (g)', 'LinAccY (g)', 'LinAccZ (g)']] . to_numpy()

    glbLinAcc = g * q.as_vector_part( quat * q.from_vector_part( linAcc ) * quat.conjugate() )
    glbLinVel = integrate.cumtrapz( glbLinAcc, time, axis=0, initial=0 )
    glbPos = integrate.cumtrapz( glbLinVel, time, axis=0, initial=0 )

    dfGlbLinAcc = pd.DataFrame( data=glbLinAcc,
            columns=['GlbLinAccX (m/s^2)', 'GlbLinAccY (m/s^2)', 'GlbLinAccZ (m/s^2)'] )
    dfGlbLinVel = pd.DataFrame( data=glbLinVel,
            columns=['GlbLinVelX (m/s)', 'GlbLinVelY (m/s)', 'GlbLinVelZ (m/s)'] )
    dfGlbPos = pd.DataFrame( data=glbPos,
            columns=['GlbPosX (m/s)', 'GlbPosY (m/s)', 'GlbPosZ (m/s)'] )

    dfGlb = pd.concat( [ df, dfGlbLinAcc, dfGlbLinVel, dfGlbPos ], axis=1 )

    print(dfGlb)

if __name__ == '__main__':
    main()
