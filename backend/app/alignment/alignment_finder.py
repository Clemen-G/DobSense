# %%
import numpy as np

from functools import reduce

class AlignmentFinder():
    def __init__(self, gradient_optimized_err_lambda,
                 gradient_penalties_lambda, hyperparameters):
        self.gradient_optimized_err_lambda = gradient_optimized_err_lambda
        self.gradient_penalties_lambda = gradient_penalties_lambda
        self.hyperparameters = hyperparameters
        self.num_params = 13

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