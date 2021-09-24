import numpy as np

from cosmics.io.mask_from_build_file import _write_3d_numpy


def test_mask_read_write(tmp_path):
    array_3d = np.empty((10, 9, 5), dtype=int)
    _write_3d_numpy(array_3d, tmp_path / "mask.txt")
