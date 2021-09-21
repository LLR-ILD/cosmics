import numpy as np
from scipy.optimize import least_squares


class LineFromPlanes:
    """It is favorable to single out `z` as the parametrising variable.
    x, y behave equivalently, while z is anyways somewhat different:

    - z is not continuously read out, but per layer with gaps.
    - The range of z parameters is different.
    - The cosmics that we are looking for do not penetrate the detector uniformly.
      Instead, they favor the z-axis direction.
    """

    def __init__(self, dim, init=(1, 1, 0), print_info=True):
        def plane_lsq(p, z, x_or_y, y_or_x):
            return self.plane_form(p, z, x_or_y) - y_or_x

        xi, yi, zi = dim["x"], dim["y"], dim["z"]
        res_x = least_squares(plane_lsq, init, args=(zi, yi, xi), loss="soft_l1")
        res_y = least_squares(plane_lsq, init, args=(zi, xi, yi), loss="soft_l1")
        self.res_x, self.res_y = res_x, res_y

        def f_m(p1, p2):
            return (p1[0] + p1[1] * p2[0]) / (1 - p1[1] * p2[1])

        def f_c(p1, p2):
            return (p1[1] * p2[2] + p1[2]) / (1 - p1[1] * p2[1])

        self.m_x, self.c_x = f_m(res_x.x, res_y.x), f_c(res_x.x, res_y.x)
        self.m_y, self.c_y = f_m(res_y.x, res_x.x), f_c(res_y.x, res_x.x)

        if print_info:
            print("Plane fit status:", res_x.status, res_y.status)
            print(f"x = {self.m_x:.2f}*z + {self.c_x:.2f}")
            print(f"y = {self.m_y:.2f}*z + {self.c_y:.2f}")

    @classmethod
    def plane_form(cls, p, z, x_or_y):
        return p[0] * z + p[1] * x_or_y + p[2]

    def __call__(self, z):
        return self.m_x * z + self.c_x, self.m_y * z + self.c_y

    def get_line_points(self, pos, n_points=100):
        p_line = {k: np.linspace(pos[k][0], pos[k][-1], n_points) for k in ["z"]}
        p_line["x"], p_line["y"] = self.__call__(p_line["z"])
        mask_x = (p_line["x"] > pos["x"][0]) & (p_line["x"] < pos["x"][-1])
        mask_y = (p_line["y"] > pos["y"][0]) & (p_line["y"] < pos["y"][-1])
        mask = mask_x & mask_y
        p_line = {k: v[mask] for k, v in p_line.items()}
        return p_line
