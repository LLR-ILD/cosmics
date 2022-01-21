from pathlib import Path
from typing import Dict, List, Mapping, Optional, Tuple, Union

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
import uproot

from .save import savefig

HistData = Tuple[str, np.ndarray, str]
HistDataDict = Dict[str, HistData]
PathLike = Union[str, Path]


def _to_np(ak_array: ak.Array) -> np.ndarray:
    return ak.flatten(ak_array, axis=None).to_numpy()


def get_slab_data(
    file_name: PathLike,
    folder: PathLike,
    tags: Optional[List[str]] = None,
) -> HistDataDict:
    implemented_tags = ["standard", "first3", "first2", "first2last1"]
    if tags is None:
        tags = implemented_tags
    else:
        if set(tags) != set(implemented_tags):
            raise NotImplementedError(tags, implemented_tags)

    a = uproot.open(Path(folder) / file_name)["ecal"].arrays()
    nhit_from_first_four = ak.sum(
        [
            ak.any(a.hit_slab == 0, axis=1),
            ak.any(a.hit_slab == 1, axis=1),
            ak.any(a.hit_slab == 2, axis=1),
            ak.any(a.hit_slab == 3, axis=1),
        ],
        axis=0,
    )
    nhit_from_last_two = ak.sum(
        [
            ak.any(a.hit_slab == 13, axis=1),
            ak.any(a.hit_slab == 14, axis=1),
        ],
        axis=0,
    )

    nslab_info: HistDataDict = {}
    if "standard" in tags:
        nslab_info["standard"] = (
            "no additional condition",
            _to_np(a.nhit_slab),
            "blue",
        )
    if "first3" in tags:
        nslab_info["first3"] = (
            "at least 3 out of 4 first slabs",
            _to_np(a.nhit_slab[nhit_from_first_four >= 3]),
            "red",
        )
    if "first2" in tags:
        nslab_info["first2"] = (
            "at least 2 out of 4 first slabs",
            _to_np(a.nhit_slab[nhit_from_first_four >= 2]),
            "green",
        )
    if "first2last1" in tags:
        cond = (nhit_from_first_four >= 2) & (nhit_from_last_two >= 1)
        nslab_info["first2last1"] = (
            "at least 2 out of 4 first slabs and\nat least 1 out of last 2 slabs",
            _to_np(a.nhit_slab[cond]),
            "black",
        )
    return nslab_info


def plot_nslabs_conditioned(
    files: Mapping[str, PathLike],
    folder: PathLike,
    img_folder: PathLike = "./img",
) -> None:
    bins = np.arange(3.5, 15)
    tags = ["standard", "first3", "first2", "first2last1"]
    for run_id, file_name in files.items():
        slab_data = get_slab_data(file_name, folder, tags)
        fig, ax = plt.subplots(figsize=(6, 4))
        for tag in tags:
            label, x, color = slab_data[tag]
            ax.hist(x, bins, label=label, histtype="step", color=color)
        ax.set_xlabel("#slabs hit per event")
        ax.set_ylabel("#events")
        ax.legend(title=">= 4 slabs", fontsize=10)
        ax.set_title(run_id)
        file_path = Path(img_folder) / f"nslabs_{run_id.split(' ')[0]}.png"
        file_path.parent.mkdir(exist_ok=True, parents=True)
        savefig(fig, file_path)
    print(f"{len(files)} figures created in {file_path.parent.absolute()}.")


def plot_nslab_summary(files: Mapping[str, PathLike], folder: PathLike):
    bins = np.arange(3.5, 15)
    fig, ax = plt.subplots(figsize=(6, 4))
    for run_id, file_name in files.items():
        a = (
            uproot.open(Path(folder) / file_name)["ecal"]["nhit_slab"]
            .array()
            .to_numpy()
        )
        ax.hist(
            a,
            bins=bins,
            label=f"{run_id} ({len(a)} entries)",
            histtype="step",
            linewidth=2,
        )
        ax.legend(title="run ID")
        ax.set_xlabel("#slabs hit")
        ax.set_ylabel("#events")
    return fig


def plot_slab_position(files: Mapping[str, PathLike], folder: PathLike):
    bins = np.arange(-0.5, 15)
    fig, ax = plt.subplots(figsize=(6, 4))
    for run_id, file_name in files.items():
        a = ak.flatten(
            uproot.open(Path(folder) / file_name)["ecal"]["hit_slab"].array()
        ).to_numpy()
        ax.hist(
            a,
            bins=bins,
            label=f"{run_id} ({len(a)} entries)",
            histtype="step",
            linewidth=2,
        )
        ax.legend(loc="upper left", title="run ID")
        ax.set_xlabel("slab (position)")
        ax.set_ylabel("#hits in >=4 slab events")
    return fig
