# %%
import sys
import numpy as np
from exceptions import UserException
from functools import reduce
from http import HTTPStatus
from threading import Thread, Lock
from alignment.utils import r, get_unit_vector
import logging

class AlignmentFinder():
    def __init__(self, gradient_optimized_err_lambda,
                 gradient_penalties_lambda, hyperparameters):
        self.gradient_optimized_err_lambda = gradient_optimized_err_lambda
        self.gradient_penalties_lambda = gradient_penalties_lambda
        self.hyperparameters = hyperparameters
        self.num_params = 13
        self.current_coordinates = None
        self.lock = Lock()

    def start_alignment_procedure(self, alignment_points):
        self._validate_input(alignment_points)
        self._set_current_coordinates(alignment_points)

        t = Thread(target=self.align,
                   name="alignment_procedure_thread",
                   kwargs={"coordinates": self.current_coordinates})
        t.start()

    def align(self, coordinates):
        res = self.get_alignment_matrices(coordinates)
        self.current_coordinates = None

        print("R_azO estimate\n", np.round(res[0], 3))
        print("R_tilt estimate\n", np.round(res[1], 3))
        print("R_altO estimate\n", np.round(res[2], 3))
    
    def get_alignment_matrices(self, coordinates, debug=False):
        """Determines the change of base matrices associated to the current telescope setup.

        Args:
            coordinates: numpy array shape=(7, n), where one row is
            cos(t_az), cos(t_alt), sin(t_az), sin(t_az), az_x, az_y, az_z
            t_* represent the telescope angles, az_* are alt-az coords of the object.
            az_* must form a unit vector.
            debug: prints additional debug. Defaults to False.
        """
        def gradient_at(gradient_err, gradient_penalties, points, theta_v):
            gradient_v = reduce(
                np.ndarray.__add__,
                [gradient_err(np.hstack((p, theta_v))) for p in points])

            if self.hyperparameters["n_samples_correction"]:
                gradient_v /= points.shape[0] # divide by number of points to get avg

            penalty_v = reduce(np.ndarray.__add__,
                            [g(theta_v) for g in gradient_penalties])
            gradient_v += self.hyperparameters["penalty_weight"] * penalty_v
            return gradient_v

        theta_v = np.zeros(self.num_params)
        theta_v[0] = 1  # setting the initial R_azO to identity or it's degenerate
        theta_v[4] = 1
        theta_v[8] = 1
        theta_v[9] = 1  # setting the initial R_tilt to identity or it's degenerate
        theta_v[11] = 1  # setting the initial R_altO to identity or it's degenerate

        v = np.zeros(self.num_params)
        g_err = self.gradient_optimized_err_lambda
        g_pen = [self.gradient_penalties_lambda]

        for _ in range(0, self.hyperparameters["num_steps"]):
            gradient = gradient_at(g_err,
                                g_pen,
                                coordinates,
                                theta_v)
            v = self.hyperparameters["beta"] * v + \
                (1 - self.hyperparameters["beta"]) * gradient
            if debug:
                print(_)
                print(np.linalg.norm(gradient, 2))
            theta_v = theta_v - self.hyperparameters["alpha"] * v

        R_azO_s_est = theta_v[0:9].reshape(3, 3).T
        t1 = theta_v[9]
        t2 = theta_v[10]
        t3 = theta_v[11]
        t4 = theta_v[12]
        R_tilt_s_est = np.array([[1, 0  , 0 ],
                                 [0, t1 , t2],
                                 [0, -t2, t1]])
        R_altO_s_est = np.array([[t3, 0, -t4],
                                 [0 , 1, 0  ],
                                 [t4, 0, t3 ]])
        # R_tilt_s_est = np.array(
        #     R_tilt.subs([(t1, theta_v[9]), (t2, theta_v[10])]).evalf()
        # ).astype(np.float64)
        # R_altO_s_est = np.array(
        #     R_altO.subs([(t3, theta_v[11]), (t4, theta_v[12])]).evalf()
        # ).astype(np.float64)
        return R_azO_s_est, R_tilt_s_est, R_altO_s_est
    
    def _validate_input(self, alignment_points):
        if len(set((s["object_id"] for s in alignment_points))) < 3:
            raise UserException(http_code=400,
                                user_message="Alignment requires at least 3 distinct objects")
    
    def _set_current_coordinates(self, alignment_points):
        alignment_points = [[
                -p['taz_coords']['taz'],
                -p['taz_coords']['talt'],
                p['alt_az_coords']['az'],
                p['alt_az_coords']['alt']]
                for p in alignment_points]
        alignment_points = np.array(alignment_points)
        taz_co_sines = np.hstack((
            (np.cos(r(alignment_points[:, 0:2])),
             np.sin(r(alignment_points[:, 0:2])))))
        # taz_co_sines format: cos taz, sin taz, cos talt, sin talt
        taz_co_sines[:, [2, 1]] = taz_co_sines[:, [1, 2]]
        az_unit_vectors = np.array(
            [np.squeeze(get_unit_vector(az, alt))
                for (az, alt) in alignment_points[:, 2:]])
        current_coordinates = np.hstack((taz_co_sines, az_unit_vectors))
        with self.lock:
            if self.current_coordinates != None:
                raise UserException(http_code=HTTPStatus.CONFLICT,
                    user_message="Another alignment is currently running")
            self.current_coordinates = current_coordinates


