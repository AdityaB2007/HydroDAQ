from dataclasses import dataclass
from pathlib import Path
from collections.abc import Iterator
from itertools import zip_longest
import numpy as np
import numpy.typing as npt

@dataclass(frozen=True)
class SensorSpec:
    unit: str
    sampling_rate: int
    samples_per_cycle: int

EXPECTED_CYCLES = 2205

VALID_COOLER_CONDITIONS = frozenset({3, 20, 100})
VALID_VALVE_CONDITIONS = frozenset({73, 80, 90, 100})
VALID_PUMP_LEAKAGE = frozenset({0, 1, 2})
VALID_ACCUMULATOR_PRESSURES = frozenset({90, 100, 115, 130})
VALID_STABLE_FLAGS = frozenset({0, 1})


@dataclass(frozen=True)
class CycleProfile:
    cooler_condition: int
    valve_condition: int
    pump_leakage: int
    accumulator_pressure: int
    stable_flag: int

    def __post_init__(self) -> None:
        checks = (
            ("cooler_condition", self.cooler_condition, VALID_COOLER_CONDITIONS),
            ("valve_condition", self.valve_condition, VALID_VALVE_CONDITIONS),
            ("pump_leakage", self.pump_leakage, VALID_PUMP_LEAKAGE),
            ("accumulator_pressure", self.accumulator_pressure, VALID_ACCUMULATOR_PRESSURES),
            ("stable_flag", self.stable_flag, VALID_STABLE_FLAGS),
        )
        for field_name, value, valid_values in checks:
            if value not in valid_values:
                raise ValueError(
                    f"Invalid {field_name}: {value} (expected one of {sorted(valid_values)})"
                )

    @property
    def is_stable(self) -> bool:
        return self.stable_flag == 0

SENSOR_SPECS = {
    **{
        f"PS{i}": SensorSpec("bar", 100, 6000)
        for i in range(1, 7)
    },
    "EPS1": SensorSpec("W", 100, 6000),
    "FS1": SensorSpec("l/min", 10, 600),
    "FS2": SensorSpec("l/min", 10, 600),
    **{
        f"TS{i}": SensorSpec("°C", 1, 60)
        for i in range(1, 5)
    },
    "VS1": SensorSpec("mm/s", 1, 60),
    "CE": SensorSpec("%", 1, 60),
    "CP": SensorSpec("kW", 1, 60),
    "SE": SensorSpec("%", 1, 60),
}

def iter_sensor_cycles(
    sensor_name: str,
    data_dir: str | Path,
    expected_cycles: int | None = EXPECTED_CYCLES,
) -> Iterator[tuple[int, npt.NDArray[np.float64]]]:
    """Yield (cycle_number, measurements) for a sensor."""

    if sensor_name not in SENSOR_SPECS:
        raise ValueError(f"Unknown sensor: {sensor_name}")

    file_path = Path(data_dir) / f"{sensor_name}.txt"
    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    expected_samples = SENSOR_SPECS[sensor_name].samples_per_cycle

    cycle_count = 0
    with file_path.open("r", encoding="utf-8") as file:
        for cycle_number, line in enumerate(file, start=1):
            if expected_cycles is not None and cycle_number > expected_cycles:
                raise ValueError(
                    f"{sensor_name}: expected {expected_cycles} cycles, "
                    f"got more than {expected_cycles}"
                )
            cycle_count = cycle_number

            try:
                measurements = np.array(line.split(), dtype=np.float64)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid measurement in {sensor_name}, "
                    f"cycle {cycle_number}"
                ) from exc

            if measurements.size != expected_samples:
                raise ValueError(
                    f"{sensor_name}, cycle {cycle_number}: "
                    f"expected {expected_samples} measurements, "
                    f"got {measurements.size}"
                )

            if not np.all(np.isfinite(measurements)):
                raise ValueError(
                    f"Non-finite measurement in {sensor_name}, "
                    f"cycle {cycle_number}"
                )

            yield cycle_number, measurements

    if cycle_count == 0:
        raise ValueError(f"{sensor_name}: file is empty")

    if expected_cycles is not None and cycle_count != expected_cycles:
        raise ValueError(
            f"{sensor_name}: expected {expected_cycles} cycles, "
            f"got {cycle_count}"
        )


def iter_profiles(
    data_dir: str | Path,
    expected_cycles: int | None = EXPECTED_CYCLES,
) -> Iterator[tuple[int, CycleProfile]]:
    """Yield (cycle_number, CycleProfile) from profile.txt."""

    file_path = Path(data_dir) / "profile.txt"
    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    cycle_count = 0
    with file_path.open("r", encoding="utf-8") as file:
        for cycle_number, line in enumerate(file, start=1):
            if expected_cycles is not None and cycle_number > expected_cycles:
                raise ValueError(
                    f"profile: expected {expected_cycles} cycles, "
                    f"got more than {expected_cycles}"
                )
            cycle_count = cycle_number

            parts = line.split()
            if len(parts) != 5:
                raise ValueError(
                    f"profile, cycle {cycle_number}: "
                    f"expected 5 columns, got {len(parts)}"
                )

            try:
                values = [int(part) for part in parts]
                profile = CycleProfile(*values)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid profile entry in cycle {cycle_number}: {exc}"
                ) from exc

            yield cycle_number, profile

    if cycle_count == 0:
        raise ValueError("profile: file is empty")

    if expected_cycles is not None and cycle_count != expected_cycles:
        raise ValueError(
            f"profile: expected {expected_cycles} cycles, "
            f"got {cycle_count}"
        )


def iter_labeled_sensor_cycles(
    sensor_name: str,
    data_dir: str | Path,
    expected_cycles: int | None = EXPECTED_CYCLES,
) -> Iterator[tuple[int, npt.NDArray[np.float64], CycleProfile]]:
    """Yield (cycle_number, measurements, profile) paired by cycle number."""

    sensor_iter = iter_sensor_cycles(sensor_name, data_dir, expected_cycles=expected_cycles)
    profile_iter = iter_profiles(data_dir, expected_cycles=expected_cycles)

    for sensor_item, profile_item in zip_longest(sensor_iter, profile_iter):
        if sensor_item is None or profile_item is None:
            raise ValueError(
                f"Cycle count mismatch between {sensor_name} and profile.txt"
            )

        sensor_cycle, measurements = sensor_item
        profile_cycle, profile = profile_item
        if sensor_cycle != profile_cycle:
            raise ValueError(
                f"Cycle number mismatch between {sensor_name} "
                f"({sensor_cycle}) and profile.txt ({profile_cycle})"
            )

        yield sensor_cycle, measurements, profile