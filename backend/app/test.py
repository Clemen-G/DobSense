# %%
# import declarations

import numpy as np
import timeit

from alignment.alignment_finder import AlignmentFinder
from alignment.utils import X, Y, Z, rot, r, ppp, norm
from alignment.loss_function_generators import gradient_optimized_err_lambda, \
    gradient_penalties_lambda


# %%

# test data generators

def get_star_coords_from_taz(R_azO_s, R_altO_s, R_tilt_s, telescope_angles):
    """Generates points that would be transformed into [1, 0, 0]

    Arguments:
        R_azO_s: azO matrix as a change of basis matrix
        R_altO_s: altO matrix as a change of basis matrix
        R_tilt_s: altO matrix as a change of basis matrix
        telescope_angles: -- (n,2) matrix of telescope (alpha, beta) angles
        in deg

    Returns:
        (n,3) matrix where each row represents a versor that would be
        transformed into [1, 0, 0] in the given telescope setup.
    """

    points = [R_azO_s.T @ rot(Z, r(-alpha)) @ R_tilt_s.T @ R_altO_s.T @ rot(Y, r(-beta)) @ X
              for (alpha, beta) in telescope_angles[:]]

    return np.vstack(points)


def generate_alignment_sample(azO_X_angle, azO_Y_angle, tilt_angle,
                                altO_angle, taz_angles):

    R_azO = (rot(X, r(azO_X_angle)) @ rot(Y, r(azO_Y_angle))).T
    R_tilt = rot(X, r(tilt_angle)).T
    R_altO = rot(Y, r(altO_angle)).T

    star_coordinates = get_star_coords_from_taz(
        R_azO, R_altO, R_tilt, taz_angles)
    angle_cosines = np.hstack(
        (np.cos(r(-taz_angles)), np.sin(r(-taz_angles))))
    angle_cosines[:, [2, 1]] = angle_cosines[:, [1, 2]]

    taz_star_coordinates = np.hstack((angle_cosines, star_coordinates))
    return {
        "R_azO": R_azO,
        "R_altO": R_altO,
        "R_tilt": R_tilt,
        "taz_star_coordinates": taz_star_coordinates
    }


def generate_alignment_samples(n_samples=1, base_seed=None, index=None):
    if base_seed is None:
        base_seed = np.random.default_rng().integers(0, 100000000)
    rng = np.random.default_rng(base_seed)

    MAX_AZO_X_AMPL = 10
    MAX_AZO_Y_AMPL = 10
    MAX_TILT = 5
    MAX_ALTO = 90
    NUM_OBS_PER_ALIGNMENT = 5

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


# %%

# multi-test

hyperparameters = {
    "num_steps": 200,
    "alpha": .4,
    "beta": .85,
    "penalty_weight": 1,
    "n_samples_correction": True,
}

test_id = None
test_samples = generate_alignment_samples(200, base_seed=1, index=test_id)


def run():
    print(hyperparameters)
    for test_sample in test_samples:
        test_sample.pop('R_azO_est', None)
        test_sample.pop('R_tilt_est', None)
        test_sample.pop('R_altO_est', None)
        alignment_finder = AlignmentFinder(gradient_optimized_err_lambda,
                                           gradient_penalties_lambda,
                                           hyperparameters)
        R_azO_est, R_tilt_est, R_altO_est = \
            alignment_finder.get_alignment_matrices(
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


timeit.timeit(lambda: run(), number=1)

# %%

hyperparameters = {
    "num_steps": 200,
    "alpha": .08,
    "beta": .9,
    "penalty_weight": .25,
    "n_samples_correction": False,
}

test_sample = generate_alignment_samples()[0]
print(test_sample)

alignment_finder = AlignmentFinder(gradient_optimized_err_lambda,
                                    gradient_penalties_lambda,
                                    hyperparameters)
R_azO_s_est, R_tilt_s_est, R_altO_s_est = \
            alignment_finder.get_alignment_matrices(
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

# taz = 0, talt=0 should give az point [1, 0, 0]
td_0 = np.array([0, 0, 1, 0, 0])

# taz = -90, talt=0 should give az point [0, 1, 0] 
td_1 = np.array([90, 0, 0, 1, 0])

# taz = 0, talt=-90 should give az point [0, 0, 1] 
td_2 = np.array([0, -90, 0, 0, 1])

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

alignment_finder = AlignmentFinder(gradient_optimized_err_lambda,
                                    gradient_penalties_lambda,
                                    hyperparameters)
R_azO_est, R_tilt_est, R_altO_est = \
            alignment_finder.get_alignment_matrices(
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

# test_sample = generate_alignment_samples(base_seed=1)[0]
test_sample = generate_alignment_sample(azO_X_angle=45,
                                        azO_Y_angle=30,
                                        tilt_angle=0,
                                        altO_angle=0,
                                        taz_angles=np.array([[0, 0]]))

R_azO = test_sample["R_azO"].T
R_altO = test_sample["R_altO"].T
R_tilt = test_sample["R_tilt"].T
taz_star_coordinates = test_sample["taz_star_coordinates"]
# format: cos(taz), sin(taz), cos(talt), sin(talt)
t_co_sines = taz_star_coordinates[0, 0:4].reshape((-1))
obj_az = taz_star_coordinates[0, 4:].reshape((-1, 1))
R_taz = np.array([[t_co_sines[0], -t_co_sines[1], 0],
                  [t_co_sines[1], t_co_sines[0], 0],
                  [0, 0, 1]])
R_talt = np.array([[1, 0, 0],
                  [0, t_co_sines[2], -t_co_sines[3]],
                  [0, t_co_sines[3], t_co_sines[2]]])

print(R_azO)
print(R_taz)
print(R_tilt)
print(R_altO)
print(R_talt)

print("Obj az: \n", obj_az)
# R_talt @ R_altO @ R_tilt @ R_taz @ R_azO @ obj_az
R_azO @ R_taz @ R_tilt @ R_altO @  R_talt @ obj_az
# %%
