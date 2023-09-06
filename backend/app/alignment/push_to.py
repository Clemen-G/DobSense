# %%
import timeit

from scipy.spatial.transform import Rotation as R
from functools import reduce
import numpy as np
import sympy as sp
from sympy.utilities import lambdify
from math import pi
# %%
Origin = [0.0, 0, 0]
X = [1.0, 0, 0]
Y = [0, 1.0, 0]
Z = [0, 0, 1.0]


def rot(axis, angle):
    """Generates the matrix for a rotation about an axis

    Arguments:
        axis -- rotation axis.
        angle -- rotation angle in radians.
        Right hand convention counterclockwise

    Returns:
        A 3x3 np.array
    """
    unit_axis = np.array(axis)
    unit_axis /= np.linalg.norm(unit_axis, 2)
    return np.array(R.from_rotvec(angle * np.array(axis)).as_matrix())


def r(deg):
    """Converts an angle deg -> radians

    Arguments:
        deg -- Angle in degree

    Returns:
        angle in radians
    """
    return 2 * pi * deg/360


# %%

# Change of basis symbols declarations

t11, t12, t13, t21, t22, t23, t31, t32, t33 = sp.symbols(
    "t11 t12 t13 t21 t22 t23  t31  t32  t33", real=True)
R_azO = sp.Matrix([[t11, t12, t13],
                   [t21, t22, t23],
                   [t31, t32, t33]]).transpose()

taz_cos, taz_sin = sp.symbols("taz_cos taz_sin", real=True)
R_az = sp.Matrix([[taz_cos, -taz_sin, 0],
                 [taz_sin, taz_cos, 0],
                 [0, 0, 1]]).transpose()

t1, t2 = sp.symbols("t1 t2", real=True)
R_tilt = sp.Matrix([[t1, 0, t2],
                    [0, 1, 0],
                    [-t2, 0, t1]]).transpose()

t3, t4 = sp.symbols("t3 t4", real=True)
R_altO = sp.Matrix([[1, 0, 0],
                    [0, t3, -t4],
                    [0, t4, t3]]).transpose()

talt_cos, talt_sin = sp.symbols("talt_cos talt_sin", real=True)
R_alt = sp.Matrix([[1, 0, 0],
                   [0, talt_cos, -talt_sin],
                   [0, talt_sin, talt_cos]]).transpose()
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
T = sp.Matrix([[0], [1], [0]], real=True)
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

# %%


def ppp(arr):
    print(np.round(arr.reshape(3, 3), 3))


# coordinates is 2d array with lines
# cos(t_az), cos(t_alt), sin(t_az), sin(t_az), az_x, az_y, az_z
# where az_x, _y, _z represent the unit vector of the star in the alt-az
# reference frame
def optimize(hyperparameters, coordinates, debug=False):
    def gradient_at(gradient_err, gradient_penalties, points, theta_v):
        gradient_v = reduce(
            np.ndarray.__add__,
            [gradient_err(np.hstack((p, theta_v))) for p in points])

        if hyperparameters["n_samples_correction"]:
            gradient_v /= points.shape[0] # divide by number of points to get avg

        penalty_v = reduce(np.ndarray.__add__,
                           [g(theta_v) for g in gradient_penalties])
        gradient_v += hyperparameters["penalty_weight"] * penalty_v
        return gradient_v

    theta_v = np.zeros(len(theta))
    theta_v[0] = 1  # setting the initial R_azO to identity or it's degenerate
    theta_v[4] = 1
    theta_v[8] = 1
    theta_v[9] = 1  # setting the initial R_tilt to identity or it's degenerate
    theta_v[11] = 1  # setting the initial R_altO to identity or it's degenerate

    v = np.zeros(len(theta))
    if hyperparameters["use_optimized"]:
        g_err = gradient_optimized_err_lambda
        g_pen = [gradient_penalties_lambda]
    else:
        g_err = gradient_err_lambda
        g_pen = [gradient_R_azO_penalties_lambda,
                 gradient_R_altO_penalties_lambda,
                 gradient_R_tilt_penalties_lambda,
                 gradient_R_azO_alignment_penalties_lambda,
                 ]
    for _ in range(0, hyperparameters["num_steps"]):
        gradient = gradient_at(g_err,
                               g_pen,
                               coordinates,
                               theta_v)
        v = hyperparameters["beta"] * v + \
            (1-hyperparameters["beta"]) * gradient
        if debug:
            print(_)
            print(np.linalg.norm(gradient, 2))
        theta_v = theta_v - hyperparameters["alpha"] * v

    R_azO_s_est = theta_v[0:9].reshape(3, 3).T
    R_tilt_s_est = np.array(
        R_tilt.subs([(t1, theta_v[9]), (t2, theta_v[10])]).evalf()
    ).astype(np.float64)
    R_altO_s_est = np.array(
        R_altO.subs([(t3, theta_v[11]), (t4, theta_v[12])]).evalf()
    ).astype(np.float64)
    return R_azO_s_est, R_tilt_s_est, R_altO_s_est


def get_star_coords_from_taz(R_azO_s, R_altO_s, R_tilt_s, telescope_angles):
    """Generates points that would be transformed into [0, 1, 0]

    Arguments:
        R_azO_s: azO matrix as a change of basis matrix
        R_altO_s: altO matrix as a change of basis matrix
        R_tilt_s: altO matrix as a change of basis matrix
        telescope_angles: -- (n,2) matrix of telescope (alpha, beta) angles
        in deg

    Returns:
        (n,3) matrix where each row represents a versor that would be
        transformed into [0, 1, 0] in the given telescope setup.
    """

    points = [R_azO_s.T @ rot(Z, r(alpha)) @ R_tilt_s.T @ R_altO_s.T @ rot(X, r(beta)) @ Y
              for (alpha, beta) in telescope_angles[:]]

    return np.vstack(points)

def generate_alignment_samples(n_samples=1, base_seed=None, index=None):
    def generate_alignment_sample(azO_X_angle, azO_Y_angle, tilt_angle,
                                  altO_angle, taz_angles):

        R_azO = (rot(X, r(azO_X_angle)) @ rot(Y, r(azO_Y_angle))).T
        R_tilt = rot(Y, r(tilt_angle)).T
        R_altO = rot(X, r(altO_angle)).T

        star_coordinates = get_star_coords_from_taz(
            R_azO, R_altO, R_tilt, taz_angles)
        angle_cosines = np.hstack(
            (np.cos(r(taz_angles)), np.sin(r(taz_angles))))
        angle_cosines[:, [2, 1]] = angle_cosines[:, [1, 2]]

        taz_star_coordinates = np.hstack((angle_cosines, star_coordinates))
        return {
            "R_azO": R_azO,
            "R_altO": R_altO,
            "R_tilt": R_tilt,
            "taz_star_coordinates": taz_star_coordinates
        }
    if base_seed is None:
        base_seed = np.random.default_rng().integers(0, 100000000)
    rng = np.random.default_rng(base_seed)

    MAX_AZO_X_AMPL = 10
    MAX_AZO_Y_AMPL = 10
    MAX_TILT = 5
    MAX_ALTO = 90
    NUM_OBS_PER_ALIGNMENT = 4

    azO_X_angles = (rng.random(n_samples) - .5) * MAX_AZO_X_AMPL
    azO_Y_angles = (rng.random(n_samples) - .5) * MAX_AZO_Y_AMPL
    tilt_angles = (rng.random(n_samples) - .5) * MAX_TILT
    altO_angles = (rng.random(n_samples)) * MAX_ALTO

    samples = []
    if index is None:
        indexes = range(0, n_samples)
    else:
        indexes = [index]
    for i in indexes:
        loop_rng = np.random.default_rng(base_seed + i + 1)  # don't delete + 1
        taz_angles = loop_rng.random(size=(NUM_OBS_PER_ALIGNMENT, 2))
        taz_angles[:, 0] = (taz_angles[:, 0] - .5) * 360
        # 0 <= altO + taz <= 90
        taz_angles[:, 1] = taz_angles[:, 1] * 90 - altO_angles[i]

        alignment_sample = generate_alignment_sample(
            azO_X_angle=azO_X_angles[i],
            azO_Y_angle=azO_Y_angles[i],
            tilt_angle=tilt_angles[i],
            altO_angle=altO_angles[i],
            taz_angles=taz_angles)

        alignment_sample["index"] = i
        alignment_sample["azO_X_angle"] = azO_X_angles[i]
        alignment_sample["azO_Y_angle"] = azO_Y_angles[i]
        alignment_sample["tilt_angle"] = tilt_angles[i]
        alignment_sample["altO_angle"] = altO_angles[i]
        alignment_sample["taz_angles"] = taz_angles

        samples.append(alignment_sample)
    return samples


def norm(np_matrix):
    return np.linalg.norm(np_matrix, ord='fro')


# %%

hyperparameters = {
    "num_steps": 200,
    "alpha": .4,
    "beta": .85,
    "penalty_weight": 1,
    "n_samples_correction": True,
    "use_optimized": True
}

test_id = None
test_samples = generate_alignment_samples(200, base_seed=1, index=test_id)


def run():
    print(hyperparameters)
    for test_sample in test_samples:
        test_sample.pop('R_azO_est', None)
        test_sample.pop('R_tilt_est', None)
        test_sample.pop('R_altO_est', None)
        R_azO_est, R_tilt_est, R_altO_est = optimize(
            hyperparameters=hyperparameters,
            coordinates=test_sample["taz_star_coordinates"])
        test_sample['R_azO_est'] = R_azO_est
        test_sample['R_tilt_est'] = R_tilt_est
        test_sample['R_altO_est'] = R_altO_est
        max_norm = max(
            [norm(test_sample["R_azO"]-R_azO_est),
             norm(test_sample["R_altO"]-R_altO_est),
             norm(test_sample["R_tilt"]-R_tilt_est)])
        if max_norm > .01:
            print(test_sample["index"])
            print(round(max_norm, 3))
            if test_id is not None:
                print(test_sample)
                print("Estimated azO:")
                ppp(R_azO_est)
                print("Estimated tilt:")
                ppp(R_tilt_est)
                print("Estimated altO:")
                ppp(R_altO_est)
                print(norm(test_sample["R_azO"]-R_azO_est))
                print(norm(test_sample["R_tilt"]-R_tilt_est))
                print(norm(test_sample["R_altO"]-R_altO_est))


        # time.sleep(1)
timeit.timeit(lambda: run(), number=1)

# %%

hyperparameters = {
    "num_steps": 200,
    "alpha": .08,
    "beta": .9,
    "penalty_weight": .25,
    "n_samples_correction": False,
    "use_optimized": False
}

test_sample = generate_alignment_samples()[0]
print(test_sample)
R_azO_s_est, R_tilt_s_est, R_altO_s_est = optimize(
    hyperparameters=hyperparameters,
    coordinates=test_sample["taz_star_coordinates"])


R_azO_s, R_tilt_s, R_altO_s = test_sample["R_azO"], test_sample["R_tilt"], test_sample["R_altO"],
print("Estimated azO:")
ppp(R_azO_s_est)
print("Expected azO:")
ppp(R_azO_s)
print()
print("Estimated tilt:")
ppp(R_tilt_s_est)
print("Expected tilt:")
ppp(R_tilt_s)
print()
print("Estimated altO:")
ppp(R_altO_s_est)
print("Expected altO:")
ppp(R_altO_s)
print()

print(f"alpha: {hyperparameters['alpha']}, beta: {hyperparameters['beta']}")
print("Diff % azO:")
ppp((R_azO_s_est-R_azO_s)/R_azO_s * 100)
print("Diff % tilt:")
ppp((R_tilt_s_est-R_tilt_s)/R_tilt_s * 100)
print("Diff % altO:")
ppp((R_altO_s_est-R_altO_s)/R_altO_s * 100)


# %%

# sim_data tests
# array format: taz_cos, taz_sin, talt_cos, talt_sin, p_x, p_y, p_z

# The az point [0, 1, 0] should have taz = 0, talt=0
td_0 = np.array([0, 0, 0, 1, 0])

# The az point [1, 0, 0] should have taz = -90, talt=0
td_1 = np.array([-90, 0, 1, 0, 0])

# The az point [0, 0, 1] should have taz = 0, talt=90
td_2 = np.array([0, 90, 0, 0, 1])

for t in [td_0, td_1, td_2]:
    if not np.allclose(t[2:5], get_star_coords_from_taz(np.identity(3),
                                                        np.identity(3),
                                                        np.identity(3),
                                                        t[0:2].reshape(1, 2))):
        raise Exception()

# np.round(sim_data(np.identity(3), td_2[0:2].reshape(1, 2)), 2)

# %%


def sim_data(R_azO_s, R_altO_s, R_tilt_s, telescope_angles):
    """Generates points that would be transformed into [0, 1, 0]

    Arguments:
        R_azO_s: azO matrix as a change of basis matrix
        R_altO_s: altO matrix as a change of basis matrix
        R_tilt_s: altO matrix as a change of basis matrix
        telescope_angles: -- (n,2) matrix of telescope (alpha, beta) angles
        in deg

    Returns:
        (n,3) matrix where each row represents a versor that would be
        transformed into [0, 1, 0]
    """

    points = [R_azO_s.T @ rot(Z, r(alpha)) @ R_tilt_s.T @ R_altO_s.T @ rot(X, r(beta)) @ Y
              for (alpha, beta) in telescope_angles[:]]

    return np.vstack(points)


R_azO_s = (rot(X, r(-3.037031148852466)) @ rot(Y, r(-0.41920439513880803))).T
R_altO_s = rot(X, r(78.16003499320661)).T
R_tilt_s = rot(Y, r(1.2305044844932034)).T
# R_az0_s = np.eye(3)
# angles = np.array([[12, 60], [-47, 19], [-62, 44]])
angles = np.array([[15.74720961,  -2.43323889],  # [112, 60],
                   [90.02738723, -48.31284648],
                   [35.731123, -60.65492364]])
sim_points = sim_data(R_azO_s, R_altO_s, R_tilt_s, angles)
angle_cosines = np.hstack((np.cos(r(angles)), np.sin(r(angles))))
angle_cosines[:, [2, 1]] = angle_cosines[:, [1, 2]]

sim_points = np.hstack((angle_cosines, sim_points))

R_azO_est, R_tilt_est, R_altO_est = optimize(hyperparameters=hyperparameters,
                                             coordinates=sim_points)

print(R_azO_est - R_azO_s)
print(R_azO_est)
print(R_altO_est - R_altO_s)
print(R_tilt_est - R_tilt_s)
print
print(norm(R_azO_est - R_azO_s))
print(norm(R_altO_est - R_altO_s))
print(norm(R_tilt_est - R_tilt_s))
# %%
