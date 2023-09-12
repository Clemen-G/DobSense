# %%
from alignment.utils import rot, r, deg, X, Y, Z, norm, get_unit_vector
from alignment.alignment_finder import AlignmentMatrices
from alignment.taz_coordinates_calculator import TazCoordinatesCalculator


class TelescopeInterface:
    def __init__(self, alignment_matrices, key_reader):
        print(alignment_matrices)
        self.alignment_matrices = alignment_matrices
        self.key_reader = key_reader
        key_reader.callback = self.handle_event
        self.event_listener = None
        self.taz = 0
        self.talt = 0

    def get_taz_from_alt_az(self, alt, az):
        return (TazCoordinatesCalculator(self.alignment_matrices)
                    .get_taz_from_alt_az(alt, az))

    def handle_event(self, ch):
        if ch not in ["h", "j", "k", "l"]:
            return

        if ch == "h":
            self.taz -= 1
        elif ch == "l":
            self.taz += 1
        elif ch == "k":
            self.talt += 1
        else:
            self.talt -= 1
        print(self.taz, self.talt)
        if self.event_listener is not None:
            self.event_listener(self.taz, self.talt)


def generate_matrices(azO_X_angle=0, azO_Y_angle=0, azO_Z_angle=-10,
                      tilt_angle=0, altO_angle=-30):
    R_azO = (rot(Z, r(azO_Z_angle)) @
             rot(Y, r(azO_Y_angle)) @
             rot(X, r(azO_X_angle))).T
    R_tilt = rot(X, r(tilt_angle)).T
    R_altO = rot(Y, r(altO_angle)).T

    return AlignmentMatrices(R_azO, R_tilt, R_altO)


if __file__ == "__main__":
    s_az = 45
    s_alt = 60

    s = get_unit_vector(s_az, s_alt).reshape(-1)

    print("input s:", s)
    TelescopeInterface(generate_matrices())\
        .get_telescope_angles(*s)
# %%
