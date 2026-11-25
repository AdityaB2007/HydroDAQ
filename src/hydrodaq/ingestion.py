from dataclasses import dataclass
from pathlib import Path
from collections.abc import Iterator
import numpy as np
import numpy.typing as npt

@dataclass(frozen=True)
class SensorSpec:
    unit: str
    sampling_rate: int
    samples_per_cycle: int

EXPECTED_CYCLES = 2205

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