from utils import rot, r, X, Y, Z, norm
import math
import numpy as np

class TelescopeInterface:
    def __init__(self,azO_X_angle=5,azO_Y_angle=3,azO_Z_angle=0,tilt_angle=0,altO_angle=30):
        self.altO_angle = altO_angle
        self.R_azO = ( rot(Z, r(azO_Z_angle)) @ rot(Y, r(azO_Y_angle)) @ rot(X, r(azO_X_angle)) ).T
        self.R_tilt = rot(Y, r(tilt_angle)).T
        self.R_altO = rot(X, r(altO_angle)).T

        print("R_azO\n", self.R_azO)
        print("R_tilt\n", self.R_tilt)
        print("R_altO\n", self.R_altO)

    def _find_roots(self, a, b, c):
        def _eq(a, b, epsilon = 0.000001):
            abs(a - b) < epsilon
        if _eq(a, 0):
            if _eq(b, 0):
                raise Exception("no roots")
            else:
                return [ -c / b ]
        else:
            delta = math.sqrt(b**2 - 4 * a * c)
            return [ (-b + delta) / (2 * a), (-b - delta) / (2 * a) ]

    def _find_talt(self, taz_cos, taz_sin, s):
        R_az = np.array([  # transposed by hand
            [taz_cos , taz_sin,  0],
            [-taz_sin, taz_cos,  0],
            [0       , 0      ,  1]
        ])
        v = self.R_tilt @ R_az @ self.R_azO @ s
        [[_, _ , _ ],
         [_, t3, t4],
         [_, _ , _ ]] = self.R_altO
        
        print("v: \n", v)
        v2 = v[1].item()
        v3 = v[2].item()
        print("v2: ", v2, "v3:", v3)
        print("t3,t4: ", t3, t4)
        talt_sin = (v3 - t4 / t3 * v2) / (t3 + t4 / t3 * t4)
        talt_cos = (v2 + t4 * talt_sin) / t3
        return [talt_cos, talt_sin]
    
    def get_telescope_angles(self, s1, s2, s3):
        [[t11, t12,t13],
         [t21, t22,t23],
         [t31, t32,t33]] = self.R_azO.T
        [[_, _, _ ],
         [_, t3,t4],
         [_, _, _]] = self.R_altO
        [[t1, _, _],
         [_ , _, _],
         [t2, _, _]] = self.R_tilt
        print("t1,t2: ", t1, t2)
        print("t3,t4: ", t3, t4)
        c = -s1*t13*t2 - s2*t2*t23 - s3*t2*t33 
        b = s1*t1*t11 + s2*t1*t21 + s3*t1*t31
        a = s1*t1*t12 + s2*t1*t22 + s3*t1*t32
        print(a,b,c)

        if a == 0:
            cosines = [-c/b]
        else:
            a1 = ((b/a)**2 + 1)
            b1 = 2 * (b * c)/(a**2)
            c1 = c**2 / a**2 - 1
            print(a1,b1,c1)
            cosines = self._find_roots(a1, b1, c1)
            
        co_sines = []
        for c in cosines:
            s = math.sqrt(1 - c**2)
            co_sines.append([c, s])
            co_sines.append([c, -s])
        for [taz_cos, taz_sin] in co_sines:
            [talt_cos, talt_sin] = self._find_talt(taz_cos, taz_sin, np.array([[s1, s2, s3]]).T)
            print ("result: taz", taz_cos, taz_sin, "talt:", talt_cos, talt_sin)


def get_unit_vector(az, alt):
    return rot(Z, r(az)) @ rot(Y, r(alt)) @ np.array([1,0,0]).reshape([3,-1])

s = get_unit_vector(45, -45).reshape(-1)
print("input s:", s)
TelescopeInterface(azO_X_angle=0,
                   azO_Y_angle=0,
                   azO_Z_angle=45,
                   tilt_angle=0,
                   altO_angle=-45)\
    .get_telescope_angles(*s)
'''
# large discrepancy in cosines, investigate
TelescopeInterface(azO_X_angle=21, azO_Y_angle=10, azO_Z_angle=-5,tilt_angle=7,altO_angle=26)\
    .get_telescope_angles(-.5,0.866,0)

TelescopeInterface(azO_X_angle=.01, azO_Y_angle=10, azO_Z_angle=-5,tilt_angle=3,altO_angle=26)\
    .get_telescope_angles(-.5,0.866,0)

import utils
import sympy
from sympy.simplify.radsimp import collect
from sympy.utilities.lambdify import lambdastr
a = R_tilt @ R_az @ R_azO @ P
factored = collect(sp.expand(a[0]), (taz_cos, taz_sin))
lambdastr((taz_cos, taz_sin), factored)
# 'lambda taz_cos,taz_sin:
#     (-s1*t13*t2 - s2*t2*t23 - s3*t2*t33 
#     + taz_cos*(s1*t1*t11 + s2*t1*t21 + s3*t1*t31) 
#     + taz_sin*(s1*t1*t12 + s2*t1*t22 + s3*t1*t32))'

c = -s1*t13*t2 - s2*t2*t23 - s3*t2*t33 
b = s1*t1*t11 + s2*t1*t21 + s3*t1*t31
a = s1*t1*t12 + s2*t1*t22 + s3*t1*t32

a * taz_sin + b * taz_cos + c = 0
taz_sin = -b / a * taz_cos -c / a
1 - taz_cos^2 = (-b / a * taz_cos -c / a) ^ 2
1 - taz_cos^2 = (b/a)^2 * taz_cos^2 + 2 * (b * c)/(a^2) * taz_cos + c^2 / a^2
((b/a)^2 + 1) * taz_cos^2 + 2 * (b * c)/(a^2) * taz_cos + c^2 / a^2 - 1 = 0
'''