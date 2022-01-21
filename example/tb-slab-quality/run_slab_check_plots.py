#!/usr/bin/env python3
from pathlib import Path

from plotting import (
    plot_nslab_summary,
    plot_nslabs_conditioned,
    plot_slab_position,
    savefig,
)

folder = Path.home() / "data/rs"
files = {
    "050043 - better position": "3GeVMIPscan_run_050043_build3.root",
    # "050121": "3GeVMIPscan_run_050121_build3.root",
    "050123 - bad position": "3GeVMIPscan_run_050123_build3.root",
    "050126 - 22° angle": "3GeV_22degrees_run_050126_build3.root",
    "050124 - no beam": "3GeVMIPscan_run_050124_build3.root",
}


if __name__ == "__main__":
    img = Path(__file__).parent / "img"
    img.mkdir(exist_ok=True)
    plot_nslabs_conditioned(files, folder, img_folder=img)
    savefig(plot_nslab_summary(files, folder), img / "nslabs_summary.png")
    savefig(plot_slab_position(files, folder), img / "slab_position_summary.png")
