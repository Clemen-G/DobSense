# %%
from alignment.utils import rot, r, deg, X, Y, Z, norm, get_unit_vector
import math
import numpy as np
import logging


class TelescopeInterface:
    def __init__(self, R_azO, R_tilt, R_altO):
        self.R_azO = R_azO
        self.R_tilt = R_tilt
        self.R_altO = R_altO
        self.altO = -deg(math.atan2(self.R_altO[2, 0], self.R_altO[0, 0]))

        print("R_azO\n", self.R_azO)
        print("R_tilt\n", self.R_tilt)
        print("R_altO\n", self.R_altO)
        print(self.altO)

    def get_telescope_angles_from_alt_az_angles(self, az, alt):
        return self.get_telescope_angles(*np.squeeze(get_unit_vector(az, alt)))

    def get_telescope_angles(self, s1, s2, s3):
        print(s1, s2, s3)
        [[t11, t12, t13],
         [t21, t22, t23],
         [t31, t32, t33]] = self.R_azO.T
        [[t3, _, _],
         [_ , _, _],
         [t4, _, _]] = self.R_altO
        [[_, _ , _ ],
         [_, t1, t2],
         [_, _ , _ ]] = self.R_tilt
        # print("t1,t2: ", t1, t2)
        # print("t3,t4: ", t3, t4)
        c = s1*t13*t2 + s2*t2*t23 + s3*t2*t33
        b = s1*t1*t12 + s2*t1*t22 + s3*t1*t32
        a = -s1*t1*t11 - s2*t1*t21 - s3*t1*t31
        # print("a, b, c:", a, b, c)

        if a == 0:
            cosines = [-c/b]
        else:
            a1 = ((b/a)**2 + 1)
            b1 = 2 * (b * c)/(a**2)
            c1 = c**2 / a**2 - 1
            # print("a1, b1, c1:",a1, b1, c1)
            cosines = self._find_roots(a1, b1, c1)
            
        co_sines = []
        for c in cosines:
            s = math.sqrt(1 - c**2)
            co_sines.append([c, s])
            co_sines.append([c, -s])
        candidates = []
        for [taz_cos, taz_sin] in co_sines:
            [talt_cos, talt_sin] = self._find_talt(taz_cos, taz_sin, np.array([[s1, s2, s3]]).T)
            candidates.append([taz_cos, taz_sin, talt_cos, talt_sin])
            print("result:\n    taz", taz_cos, taz_sin,
                  "\n    talt:", talt_cos, talt_sin,
                  "\n  norms: ",
                  norm([[taz_sin, taz_cos]]),
                  norm([[talt_sin, talt_cos]]),
                  "\n  angles: ",
                  -deg(math.atan2(taz_sin, taz_cos)), " | ",
                  -deg(math.atan2(talt_sin, talt_cos)))
        return self._select_solution(candidates)

    def _find_talt(self, taz_cos, taz_sin, s):
        R_az = np.array([  # transposed by hand
            [taz_cos , taz_sin,  0],
            [-taz_sin, taz_cos,  0],
            [0       , 0      ,  1]
        ])
        # print("_find_talt - s:", s)
        v = self.R_tilt @ R_az @ self.R_azO @ s
        [[t3, _, _],
         [_ , _, _],
         [t4, _, _]] = self.R_altO
        
        # print("v: \n", v)
        v1 = v[0].item()
        v3 = v[2].item()
        # print("v1: ", v1, "v3:", v3)
        # print("t3,t4: ", t3, t4)
        talt_sin = -(v3 + t4 / t3 * v1) / (t3 + t4 / t3 * t4)
        talt_cos = (v1 + t4 * talt_sin) / t3
        return [talt_cos, talt_sin]
    
    def _select_solution(self, candidates):
        # only 2 solutions have talt_cos^2 + talt_sin^2 = 1
        # select them by ranking
        valid_solutions = sorted(candidates,
                                 key=lambda c : abs(1 - norm([c[2:]])))[0:2]
        valid_solutions = list(map(self._to_angles, valid_solutions))
        if (0 <= valid_solutions[0]["talt"] + self.altO <= 90):
            return valid_solutions[0]
        elif (0 <= valid_solutions[1]["talt"] + self.altO <= 90):
            return valid_solutions[1]
        else:
            raise Exception("No valid solution found")
    
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
        
    def _to_angles(self, solution):
        taz_cos, taz_sin, talt_cos, talt_sin = solution
        return {"taz": -deg(math.atan2(taz_sin, taz_cos)),
                  "talt": -deg(math.atan2(talt_sin, talt_cos))}

def generate_matrices(azO_X_angle=0, azO_Y_angle=0, azO_Z_angle=-10,
                    tilt_angle=0, altO_angle=-30):
    R_azO = ( rot(Z, r(azO_Z_angle)) @ rot(Y, r(azO_Y_angle)) @ rot(X, r(azO_X_angle)) ).T
    R_tilt = rot(X, r(tilt_angle)).T
    R_altO = rot(Y, r(altO_angle)).T
    return {
        "R_azO": R_azO,
        "R_tilt": R_tilt,
        "R_altO": R_altO,
    }
if __file__ == "__main__":
    s_az = 45
    s_alt = 60

    s = get_unit_vector(s_az, s_alt).reshape(-1)

    print("input s:", s)
    TelescopeInterface(**generate_matrices())\
        .get_telescope_angles(*s)
# %%
