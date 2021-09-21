from pathlib import Path

import numpy as np

from cosmics.io import LoadTriggered

run_name = "Run_ILC_08172020_Cosmics_48h_Ascii_build"
run_name = "Run_ILC_08042020_cosmic_it15_Ascii_build"

raw_path = Path("data/raw") / f"{run_name}.root"
prebuilt_path = Path("data/triggered") / run_name
img_path = Path("img") / run_name
assert raw_path.exists()
prebuilt_path.mkdir(exist_ok=True, parents=True)
img_path.mkdir(exist_ok=True, parents=True)

get_triggered_hits = LoadTriggered(
    triggered_file_folder=prebuilt_path,
    root_file=raw_path,
    root_tree="ecal",
    step_size="250 MB",
)

_pos_xy = np.arange(3.8, 87, 5.5)
default_pos = dict(
    x=np.concatenate([-_pos_xy[::-1], _pos_xy]),
    y=np.concatenate([-_pos_xy[::-1], _pos_xy]),
    z=np.arange(0, 14),
)


if __name__ == "__main__":
    cut = " nhit_slab > 7 "
    entry_stop = -1
    # entry_stop = 100_000
    print(len(get_triggered_hits(cut, entry_stop=entry_stop)))
