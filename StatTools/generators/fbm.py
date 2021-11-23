from functools import reduce, partial
from numpy import int64, save, nonzero, where, uint8, array, max, min, ndarray
from numpy.random import randn, normal
from math import floor
from ctypes import c_double
from StatTools.auxiliary import SharedBuffer
from PIL import Image
from random import gauss
# from memory_profiler import profile


def add_h_values(vector: ndarray, k: int, h: float):
    return array([v + (pow(0.5, k * (h - 1)) * gauss(0, 1)) if v != 0 else 0 for v in vector])


def quant_array(vector: ndarray, min_val: float, max_val: float):
    return ((vector - min_val) / (max_val - min_val) * 255).astype(uint8)


# @profile()
def FBMotion(h: float, field_size: int):
    """
    This is the algorithm. It need C version for sure.
    """


    n = 2 ** field_size + 1
    shape = n, n

    F = SharedBuffer(shape, c_double)

    F[0, 0], F[0, -1], F[-1, 0], F[-1, -1] = randn(4)
    for k in range(1, field_size + 1):
        m = 2 ** k

        fl = floor(n / m)

        l1 = fl + 1 - 1
        s = fl * 2
        l2 = floor((m - 1) * n / m) + 1

        for i in range(l1, l2, s):
            for j in range(l1, l2, s):
                v1 = F[i - fl, j - fl]
                v2 = F[i - fl, j + fl]
                v3 = F[i + fl, j - fl]
                v4 = F[i + fl, j + fl]

                F[i, j] = (v1 + v2 + v3 + v4) / 4

        for i in range(0, n + 1, s):
            for j in range(fl, l2, s):
                F[i, j] = (F[i, j - fl] + F[i, j + fl]) / 2

        for j in range(0, n + 1, s):
            for i in range(fl, l2, s):
                F[i, j] = (F[i - fl, j] + F[i + fl, j]) / 2

        F.apply_in_place(func=partial(add_h_values, k=k, h=h), by_1st_dim=True)

    max_val = max(F.to_array())
    min_val = min(F.to_array())
    F.apply_in_place(func=partial(quant_array, min_val=min_val, max_val=max_val), by_1st_dim=True)

    z = array(F.to_array(), dtype=uint8)
    return z


if __name__ == '__main__':
    r = FBMotion(1.6, 9)
    im = Image.fromarray(r)
    im.save("filename.jpeg")
