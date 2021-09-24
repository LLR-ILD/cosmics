from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import awkward as ak
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import tqdm.auto as tqdm
import uproot


def fill_batch_is_masked(batch, is_masked, pos, tqdm_bar=None):
    for (x_id, x) in enumerate(pos["x"]):
        mask_x = batch.hit_x == x
        batch_y_1 = batch.hit_y[mask_x]
        batch_z_1 = batch.hit_z[mask_x]
        batch_m_1 = batch.hit_isMasked[mask_x]
        for (y_id, y) in enumerate(pos["y"]):
            mask_y = batch_y_1 == y
            batch_z_2 = batch_z_1[mask_y]
            batch_m_2 = batch_m_1[mask_y]
            for (z_id, z) in enumerate(pos["z"]):
                if is_masked[x_id, y_id, z_id] != -1:
                    continue
                mask_z = batch_z_2 == z
                batch_m = batch_m_2[mask_z]
                is_mask_values = ak.flatten(batch_m)
                if len(is_mask_values):
                    is_masked[x_id, y_id, z_id] = is_mask_values[0]
                    if tqdm_bar:
                        tqdm_bar.update()
    return is_masked


def get_is_masked(
    tree,
    pos: Dict[str, np.ndarray],
    entry_stop: int = -1,
    step_size: str = "250 MB",
) -> np.ndarray:
    is_masked = np.full((len(pos["x"]), len(pos["y"]), len(pos["z"])), -1)
    keys = ["hit_x", "hit_y", "hit_z", "hit_isMasked"]
    n_raw = entry_stop if entry_stop >= 0 else tree.num_entries
    with tqdm.tqdm(desc="Cells found", total=is_masked.size) as cell_bar:
        with tqdm.tqdm(desc="Events", total=n_raw) as event_bar:
            for batch in tree.iterate(keys, entry_stop=entry_stop, step_size=step_size):
                is_masked = fill_batch_is_masked(batch, is_masked, pos, cell_bar)
                event_bar.update(len(batch))
    return is_masked


_shape_str = "# Array shape (z, y, x): "


def _write_3d_numpy(data: np.ndarray, file_name) -> None:
    """https://stackoverflow.com/questions/3685265/how-to-write-a-multidimensional-array-to-a-text-file"""
    with open(file_name, "w") as f:
        # I'm writing a header here just for the sake of readability
        # Any line starting with "#" will be ignored by numpy.loadtxt
        zyx_data = np.transpose(data)
        f.write(_shape_str + str(zyx_data.shape) + "\n")
        for i, yx_data in enumerate(zyx_data):
            f.write(f"# New slice: {i}\n")
            np.savetxt(f, yx_data, fmt="%+i")
    # Just to check that the written file can be recovered.
    _loaded_data = _read_3d_numpy(file_name)
    assert _loaded_data.shape == data.shape
    assert np.all(_loaded_data == data)


def _read_3d_numpy(file_name) -> np.ndarray:
    """https://stackoverflow.com/questions/3685265/how-to-write-a-multidimensional-array-to-a-text-file"""
    with open(file_name) as f:
        txt = f.read()
        tuple_start = txt.find(_shape_str) + len(_shape_str) + 1  # + 1 for "("
        tuple_stop = txt[tuple_start:].find(")") + tuple_start
        str_tuple = txt[tuple_start:tuple_stop]
        shape = [int(str_number) for str_number in str_tuple.split(",")]
        assert len(shape) == 3
    read_data = np.transpose(np.loadtxt(file_name).reshape(shape))
    return read_data


class Mask:
    def __init__(
        self,
        values: np.ndarray,
        pos: Optional[Dict[str, np.ndarray]] = None,
    ) -> None:
        self.values = values
        self.x, self.y, self.z = self._get_positions(pos)
        self.bins_x = self.bins(self.x)
        self.bins_y = self.bins(self.y)
        self.bins_z = self.bins(self.z)

    @classmethod
    def bins(cls, x):
        x_first = x[0] - (x[1] - x[0]) / 2
        x_last = x[-1] + (x[-1] - x[-2]) / 2
        x_mid = (x[1:] + x[:-1]) / 2
        return np.concatenate(([x_first], x_mid, [x_last]))

    def _get_positions(
        self,
        pos: Optional[Dict[str, np.ndarray]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if pos is None:
            assert len(self.values.shape) == 3
            x = np.arange(self.values.shape[0])
            y = np.arange(self.values.shape[1])
            z = np.arange(self.values.shape[2])
        else:
            x = pos["x"]
            y = pos["y"]
            z = pos["z"]
        return x, y, z

    def plot_layer(self, i, ax=None):
        if ax is None:
            _, ax = plt.subplots()
        colors = {"white": "undefined", "yellow": "unmasked", "black": "masked"}
        ax.pcolormesh(
            self.bins_x,
            self.bins_y,
            self.values[:, :, i],
            cmap=mpl.colors.ListedColormap(colors),
            vmin=-1,
            vmax=1,
        )
        ax.set_title(f"Layer {i}")
        ax.set_aspect("equal")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend(
            title="Channel mask",
            handles=[mpl.patches.Patch(color=c, label=l) for c, l in colors.items()],
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
        )
        return ax

    def save_plots(self, save_folder: Union[str, Path] = None):
        for i in range(self.values.shape[-1]):
            fig, ax = plt.subplots()
            self.plot_layer(i, ax)
            fig.tight_layout()
            if save_folder is not None:
                fig.savefig(Path(save_folder) / f"mask_{i:02}.png", dpi=300)

    @classmethod
    def from_build_file(
        cls,
        mask_folder: Union[str, Path],
        root_file: Union[str, Path],
        root_tree: str,
        pos: Dict[str, np.ndarray],
        entry_stop: int = -1,
        step_size: str = "100 MB",
    ) -> "Mask":
        mask_file = Path(mask_folder) / "mask.txt"
        if mask_file.exists():
            values = _read_3d_numpy(mask_file)
            mask = Mask(values, pos)
        else:
            print("Mask file not found, will be created.")
            root_file_object = uproot.open(root_file)
            tree = root_file_object[root_tree]
            values = get_is_masked(tree, pos, entry_stop, step_size)
            _write_3d_numpy(values, mask_file)
            mask = Mask(values, pos)
            mask.save_plots(mask_folder)
        return mask
