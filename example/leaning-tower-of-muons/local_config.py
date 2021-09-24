from pathlib import Path

import numpy as np

from cosmics.io import LoadTriggered, Mask

run_name = "Run_ILC_08172020_Cosmics_48h_Ascii_build"
run_name = "Run_ILC_08042020_cosmic_it15_Ascii_build"
tree_name = "ecal"


raw_path = Path("data/raw") / f"{run_name}.root"
assert raw_path.exists()
img_path = Path("img") / run_name
data_folder = Path("data")
mask_folder = data_folder / "mask" / run_name
prebuilt_folder = data_folder / "triggered" / run_name
img_path.mkdir(exist_ok=True, parents=True)
mask_folder.mkdir(exist_ok=True, parents=True)
prebuilt_folder.mkdir(exist_ok=True, parents=True)

memory_step_uproot = "100 MB"

get_triggered_hits = LoadTriggered(
    triggered_file_folder=prebuilt_folder,
    root_file=raw_path,
    root_tree=tree_name,
    step_size=memory_step_uproot,
)

_pos_xy = np.arange(3.8, 87, 5.5)
default_pos = dict(
    x=np.concatenate([-_pos_xy[::-1], _pos_xy]),
    y=np.concatenate([-_pos_xy[::-1], _pos_xy]),
    z=np.arange(0, 14),
)


def get_mask(pos=default_pos, entry_stop=-1, step_size=memory_step_uproot):
    return Mask.from_build_file(
        mask_folder=mask_folder,
        root_file=raw_path,
        root_tree=tree_name,
        pos=pos,
        entry_stop=entry_stop,
        step_size=memory_step_uproot,
    )


if __name__ == "__main__":
    cut = " nhit_slab > 7 "
    entry_stop = -1
    # entry_stop = 100_000
    print(len(get_triggered_hits(cut, entry_stop=entry_stop)))
