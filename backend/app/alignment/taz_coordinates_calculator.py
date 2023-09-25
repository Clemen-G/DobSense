import math
import numpy as np
import logging
from alignment.utils import deg, norm, get_unit_vector


class TazCoordinatesCalculator:
    def __init__(self, alignment_matrices) -> None:
        self.R_azO = alignment_matrices.R_azO
        self.R_tilt = alignment_matrices.R_tilt
        self.R_altO = alignment_matrices.R_altO
        self.altO = -deg(math.atan2(
            alignment_matrices.R_altO[2, 0],
            alignment_matrices.R_altO[0, 0]))

    def get_taz_from_alt_az(self, az, alt):
        """Returns the telescope angles corresponding to given alt-az
        coordinates, if the object can be pointed by the scope
        (0 <= talt <= 90)

        Args:
            az: sky object's azimuth
            alt: sky object's altitude

        Returns:
            { "taz": 123, "talt": 55 } or None
        """
        return self.get_telescope_angles(*np.squeeze(get_unit_vector(az, alt)))
    
    def get_telescope_angles(self, s1, s2, s3):
        logging.debug(s1, s2, s3)
        [[t11, t12, t13],
         [t21, t22, t23],
         [t31, t32, t33]] = self.R_azO.T
        [[t3, _, _],
         [_ , _, _],
         [t4, _, _]] = self.R_altO
        [[_, _ , _ ],
         [_, t1, t2],
         [_, _ , _ ]] = self.R_tilt
        # logging.debug("t1,t2: ", t1, t2)
        # logging.debug("t3,t4: ", t3, t4)
        c = s1*t13*t2 + s2*t2*t23 + s3*t2*t33
        b = s1*t1*t12 + s2*t1*t22 + s3*t1*t32
        a = -s1*t1*t11 - s2*t1*t21 - s3*t1*t31
        # logging.debug("a, b, c:", a, b, c)

        if a == 0:
            cosines = [-c/b]
        else:
            a1 = ((b/a)**2 + 1)
            b1 = 2 * (b * c)/(a**2)
            c1 = c**2 / a**2 - 1
            # logging.debug("a1, b1, c1:",a1, b1, c1)
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
            logging.debug("result:\n    taz", taz_cos, taz_sin,
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
        # logging.debug("_find_talt - s:", s)
        v = self.R_tilt @ R_az @ self.R_azO @ s
        [[t3, _, _],
         [_ , _, _],
         [t4, _, _]] = self.R_altO
        
        # logging.debug("v: \n", v)
        v1 = v[0].item()
        v3 = v[2].item()
        # logging.debug("v1: ", v1, "v3:", v3)
        # logging.debug("t3,t4: ", t3, t4)
        talt_sin = -(v3 + t4 / t3 * v1) / (t3 + t4 / t3 * t4)
        talt_cos = (v1 + t4 * talt_sin) / t3
        return [talt_cos, talt_sin]
    
    def _select_solution(self, candidates):
        # only 2 solutions have talt_cos^2 + talt_sin^2 = 1
        # select them by ranking
        valid_solutions = sorted(candidates,
                                 key=lambda c: abs(1 - norm([c[2:]])))[0:2]
        valid_solutions = list(map(self._to_angles, valid_solutions))
        # we attempt to pick a solution above the horizon
        # that does not require the telescope to flip over
        if (0 <= valid_solutions[0]["talt"] + self.altO <= 90):
            return valid_solutions[0]
        elif (0 <= valid_solutions[1]["talt"] + self.altO <= 90):
            return valid_solutions[1]
        # otherwise we'll return a solution that does not flip over
        # but might result in the telescope pointing below the horizon
        elif (valid_solutions[0]["talt"] + self.altO <= 90):
            return valid_solutions[0]
        elif (valid_solutions[1]["talt"] + self.altO <= 90):
            return valid_solutions[1]
        else:
            raise Exception("Unable to find a solution.")
    
    def _find_roots(self, a, b, c):
        def _eq(a, b, epsilon=0.000001):
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
