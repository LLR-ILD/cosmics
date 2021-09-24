"""Load (or create) only those events passing a trigger/cut."""
import time
from pathlib import Path
from typing import Union

import awkward as ak
import psutil
import tqdm.auto as tqdm
import uproot


def _check_step_size_is_reasonable(step_size: Union[str, int, float]) -> None:
    step_size = str(step_size)
    number = float(step_size[:-2])
    if step_size.endswith("GB"):
        number = float(step_size[:-2]) * 1024 ** 3
    elif step_size.endswith("MB"):
        number = float(step_size[:-2]) * 1024 ** 2
    elif step_size.endswith("kB"):
        number = float(step_size[:-2]) * 1024 ** 1
    else:
        print("The step size should be specified in terms of MB/GB.", step_size)
        return
    memory_available = psutil.virtual_memory().available
    if number > memory_available / 20:
        # The value is chosen by personal experience with our cosmics files
        # and might not always be reasonable.
        print(
            "The batch size seems too large for this machine's memory: "
            f"{step_size=} with {memory_available / 1024 ** 3:.2f} GB available."
        )


class LoadTriggered:
    def __init__(
        self,
        triggered_file_folder: Union[str, Path],
        root_file: Union[str, Path],
        root_tree: str,
        step_size: str = "100 MB",
    ) -> None:
        self._triggered_file_folder = Path(triggered_file_folder)
        self._root_file = Path(root_file)
        self._root_tree = root_tree
        self._step_size = step_size
        self._symbol_name_map = {
            ">": "_greater_than_",
            "<": "_smaller_than_",
        }

    def trigger_to_filename(self, trigger: str):
        """Seems to be necessary for saving as a parquet file."""
        for k, v in self._symbol_name_map.items():
            trigger = trigger.replace(k, v)
        return trigger

    def _load_events(self, filename: Path, entry_stop: int) -> ak.Array:
        events = ak.from_parquet(filename)
        if len(events) < entry_stop:
            print(f"WARNING: {entry_stop} triggered requested, got {len(events)}.")
        events = events[:entry_stop]
        return events

    def _select_events(
        self,
        trigger_cleaned: str,
        filename: Path,
        entry_stop: int,
    ) -> ak.Array:
        time_start_building = time.time()
        print(f"No prebuilt file build for trigger: {trigger_cleaned}. Please wait.")
        if entry_stop != -1:
            print(
                f"Only partial reading ({entry_stop} events) was chosen. "
                "In this setting, the created arrays will not be saved to disk. "
                "As it is a new query, `entry_stop` refers to pre-trigger events. "
            )
        root_file_object = uproot.open(self._root_file)
        tree = root_file_object[self._root_tree]

        triggered_batches = []
        batch_iter = tree.iterate(entry_stop=entry_stop, step_size=self._step_size)
        _check_step_size_is_reasonable(self._step_size)
        swap_baseline = psutil.swap_memory().used
        n_raw = entry_stop if entry_stop >= 0 else tree.num_entries
        with tqdm.tqdm(
            batch_iter,
            desc="Raw events",
            total=n_raw,
            postfix={"n_triggered": 0, "mem [%]": psutil.virtual_memory().percent},
        ) as p_bar:
            for batch in batch_iter:
                triggered_batches.append(
                    ak.packed(batch[ak.numexpr.evaluate(trigger_cleaned, batch)])
                )
                if psutil.swap_memory().used - swap_baseline > 0.25 * 1024 ** 3:
                    swap_baseline = 1024 ** 5  # Ensures this is printed only once.
                    p_bar.write(
                        "Warning: No more free memory. Using swap now. "
                        "This is much slower."
                    )
                p_bar.set_postfix(
                    {
                        "n_triggered": len(triggered_batches[-1]),
                        "mem [%]": psutil.virtual_memory().percent,
                    }
                )
                p_bar.update(len(batch))
        events = ak.flatten(ak.concatenate(triggered_batches), axis=0)
        if entry_stop == -1:
            ak.to_parquet(events, filename)
        building_time = time.time() - time_start_building
        print(f"Selecting the events took {int(building_time)}s.")
        return events

    def __call__(
        self,
        trigger: str,
        entry_stop: int = -1,
    ) -> ak.Array:
        trigger_cleaned = trigger = "".join(trigger.split())  # Remove whitespace.
        file_stem = f"{self.trigger_to_filename(trigger_cleaned)}.parquet"
        filename = self._triggered_file_folder / file_stem
        if filename.exists():
            events = self._load_events(filename, entry_stop)
        else:
            events = self._select_events(trigger_cleaned, filename, entry_stop)
        return events
