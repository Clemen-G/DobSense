# %%
import numpy as np
import sympy as sp
from sympy.utilities import lambdify

# %%

# Change of basis symbols declarations

t11, t12, t13, t21, t22, t23, t31, t32, t33 = sp.symbols(
    "t11 t12 t13 t21 t22 t23  t31  t32  t33", real=True)
R_azO = sp.Matrix([[t11, t12, t13],
                   [t21, t22, t23],
                   [t31, t32, t33]]).transpose()

taz_cos, taz_sin = sp.symbols("taz_cos taz_sin", real=True)
R_az = sp.Matrix([[taz_cos, -taz_sin, 0],
                  [taz_sin, taz_cos , 0],
                  [0      , 0       , 1]]).transpose()

t1, t2 = sp.symbols("t1 t2", real=True)
R_tilt = sp.Matrix([[1, 0 , 0  ],
                    [0, t1, -t2],
                    [0, t2, t1 ]]).transpose()

t3, t4 = sp.symbols("t3 t4", real=True)
R_altO = sp.Matrix([[t3 , 0, t4],
                    [0  , 1, 0 ],
                    [-t4, 0, t3]]).transpose()

talt_cos, talt_sin = sp.symbols("talt_cos talt_sin", real=True)
R_alt = sp.Matrix([[talt_cos , 0, talt_sin],
                   [0        , 1, 0       ],
                   [-talt_sin, 0, talt_cos]]).transpose()
# %%

# Using matrices to simplify the penalties creation
R_azO_penalties_matrix = R_azO @ R_azO.T - sp.eye(3)

# avoids double-counting terms
R_azO_penalties = sum(
    [R_azO_penalties_matrix[i, j]**2
        for i in range(0, 3) for j in range(i, 3)],
    sp.Integer(0))
# R_azO_penalties = sum(
#     [p**2 for p in R_azO_penalties_matrix.values()],
#     sp.Integer(0))


R_altO_penalties = (t3**2 + t4**2 - 1)**2

# R_altO_penalties_matrix = R_altO @ R_altO.T - sp.eye(3)
# R_altO_penalties = sum(
#     [p**2 for p in R_altO_penalties_matrix.values()],
#     sp.Integer(0))


R_tilt_penalties = (t1**2 + t2**2 - 1)**2

# R_tilt_penalties_matrix = R_tilt @ R_tilt.T - sp.eye(3)
# R_tilt_penalties = sum(
#     [p**2 for p in R_tilt_penalties_matrix.values()],
#     sp.Integer(0))

Z_sym = sp.Matrix([[0], [0], [1]], real=True)
R_azO_alignment = Z_sym - R_azO.T @ Z_sym
R_azO_alignment_penalties = ((R_azO_alignment.T @ R_azO_alignment)**2)[0,0]

penalties = R_azO_penalties \
    + R_altO_penalties \
    + R_tilt_penalties \
    + R_azO_alignment_penalties
# %%

# square error function

s1, s2, s3 = sp.symbols("s1 s2 s3", real=True)
az_coordinates = [s1, s2, s3]
P = sp.Matrix([[s1], [s2], [s3]], real=True)
T = sp.Matrix([[1], [0], [0]], real=True)
err = ((T - R_alt @ R_altO @ R_tilt @ R_az @ R_azO @ P).norm())**2
optimized_err = ((R_az.T @ R_tilt.T @ R_altO.T @
                 R_alt.T @ T - R_azO @ P).norm())**2

# point_subs = [i for i in zip([p1, p2, p3], sim_points[0,])]
# err.subs([(alpha, r(45)), (beta, 0), *point_subs])

# %%

# Generation of the gradient python functions

taz_cosines = [taz_cos, taz_sin, talt_cos, talt_sin]
# space of the optimization problem
theta = [t11, t12, t13, t21, t22, t23, t31, t32, t33, t1, t2, t3, t4]

# gradient_err is determined separately bc it needs to be evaluated
# for each point
gradient_err = [err.diff(dt) for dt in theta]
gradient_optimized_err = [optimized_err.diff(dt) for dt in theta]
gradient_R_azO_penalties = [R_azO_penalties.diff(dt) for dt in theta]
gradient_R_altO_penalties = [R_altO_penalties.diff(dt) for dt in theta]
gradient_R_tilt_penalties = [R_tilt_penalties.diff(dt) for dt in theta]
gradient_R_azO_alignment_penalties = [R_azO_alignment_penalties.diff(dt)
                                      for dt in theta]
gradient_penalties = [penalties.diff(dt) for dt in theta]


def wrap_with_numpy(sympy_lambda):
    def wrapper(*args):
        if isinstance(args[0], np.ndarray):
            return np.array(sympy_lambda(*(args[0].tolist())))
        else:
            return np.array(sympy_lambda(*args))
    return wrapper


gradient_err_lambda = lambdify(taz_cosines + az_coordinates + theta,
                               gradient_err)
gradient_err_lambda = wrap_with_numpy(gradient_err_lambda)

gradient_optimized_err_lambda = lambdify(taz_cosines + az_coordinates + theta,
                                         gradient_optimized_err)
gradient_optimized_err_lambda = wrap_with_numpy(gradient_optimized_err_lambda)

gradient_R_azO_penalties_lambda = lambdify(theta,
                                           gradient_R_azO_penalties)
gradient_R_azO_penalties_lambda = wrap_with_numpy(
    gradient_R_azO_penalties_lambda)

gradient_R_altO_penalties_lambda = lambdify(theta,
                                            gradient_R_altO_penalties)
gradient_R_altO_penalties_lambda = wrap_with_numpy(
    gradient_R_altO_penalties_lambda)

gradient_R_tilt_penalties_lambda = lambdify(theta,
                                            gradient_R_tilt_penalties)
gradient_R_tilt_penalties_lambda = wrap_with_numpy(
    gradient_R_tilt_penalties_lambda)

gradient_R_azO_alignment_penalties_lambda = lambdify(theta,
                                            gradient_R_azO_alignment_penalties)
gradient_R_azO_alignment_penalties_lambda = wrap_with_numpy(
    gradient_R_azO_alignment_penalties_lambda)

gradient_penalties_lambda = lambdify(theta,
                                     gradient_penalties)
gradient_penalties_lambda = wrap_with_numpy(
    gradient_penalties_lambda)

