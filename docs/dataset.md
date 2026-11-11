# UCI Hydraulic System Dataset

## Overview

HydroDAQ initially uses the UCI **Condition Monitoring of Hydraulic Systems** dataset to develop and validate its data ingestion and analysis pipeline.

The dataset was experimentally collected using a hydraulic test rig. It contains multivariate time-series measurements from 17 sensors, alongside cycle-level annotations describing the condition of four hydraulic components and system stability.

- **Source:** UCI Machine Learning Repository, Dataset 447
- **Instances:** 2,205 operating cycles
- **Cycle duration:** 60 seconds
- **Total sensor attributes:** 43,680 per cycle
- **Data type:** Multivariate time-series
- **Missing values:** None reported in the dataset documentation

## Experimental Setup

The hydraulic test rig consists of a primary working circuit and a secondary cooling-filtration circuit connected through an oil tank.

The system repeatedly executes constant-load operating cycles lasting 60 seconds. During these cycles, process measurements are collected while the condition of four hydraulic components is quantitatively varied:

- Cooler
- Valve
- Pump
- Hydraulic accumulator

## Sensor Inventory

The dataset contains 17 measurement channels with different sampling frequencies.

| Sensor(s) | Physical quantity | Unit | Sampling rate | Samples per cycle |
|---|---|---|---:|---:|
| PS1–PS6 | Pressure | bar | 100 Hz | 6,000 |
| EPS1 | Motor power | W | 100 Hz | 6,000 |
| FS1–FS2 | Volume flow | l/min | 10 Hz | 600 |
| TS1–TS4 | Temperature | °C | 1 Hz | 60 |
| VS1 | Vibration | mm/s | 1 Hz | 60 |
| CE | Cooling efficiency (virtual) | % | 1 Hz | 60 |
| CP | Cooling power (virtual) | kW | 1 Hz | 60 |
| SE | Efficiency factor | % | 1 Hz | 60 |

Each measurement file is a matrix in which rows represent operating cycles and columns represent individual measurements within a cycle.

The total number of sensor attributes per cycle is:

- 8 channels × 60 samples = 480
- 2 channels × 600 samples = 1,200
- 7 channels × 6,000 samples = 42,000

**Total: 43,680 measurements per cycle.**

## Cycle-Level Annotations

The `profile.txt` file contains five annotations for each operating cycle. Its rows correspond directly to the rows in the sensor measurement files.

| Column | Variable | Description |
|---|---|---|
| 1 | Cooler condition | Efficiency percentage |
| 2 | Valve condition | Switching behavior percentage |
| 3 | Internal pump leakage | Leakage severity |
| 4 | Hydraulic accumulator | Pressure condition in bar |
| 5 | Stable flag | Indicates whether stable operating conditions were reached |

The documented values are:

**Cooler condition**
- 3: Close to total failure
- 20: Reduced efficiency
- 100: Full efficiency

**Valve condition**
- 100: Optimal switching behavior
- 90: Small lag
- 80: Severe lag
- 73: Close to total failure

**Internal pump leakage**
- 0: No leakage
- 1: Weak leakage
- 2: Severe leakage

**Hydraulic accumulator**
- 130: Optimal pressure
- 115: Slightly reduced pressure
- 100: Severely reduced pressure
- 90: Close to total failure

**Stable flag**
- 0: Conditions were stable
- 1: Static conditions might not have been reached yet

The first four annotations describe component degradation conditions. The fifth indicates system stability.

## File Organization

The raw dataset is stored locally under:

`data/raw/`

The directory contains:

- 17 sensor measurement files (`PS1.txt`, `EPS1.txt`, `TS1.txt`, etc.)
- `profile.txt` — cycle-level annotations
- `description.txt` — dataset overview and attribute information
- `documentation.txt` — detailed dataset documentation

The measurement and profile files contain 2,205 rows each. Measurement rows contain whitespace-separated numerical values, with the number of values determined by each sensor's sampling frequency.

The raw dataset is excluded from version control.

## HydroDAQ Ingestion Considerations

The ingestion pipeline should:

1. Read sensor measurements while preserving their native sampling frequencies.
2. Associate measurements with their corresponding operating-cycle numbers.
3. Load cycle-level annotations from `profile.txt`.
4. Validate expected row counts and samples per cycle.
5. Detect malformed or inconsistent input data.
6. Avoid unnecessarily loading the entire dataset into memory.

Sensor measurements should initially remain at their original sampling rates. Resampling, feature extraction, and signal processing will be handled as separate analysis operations.

## References

N. Helwig, E. Pignanelli, and A. Schütze, "Condition Monitoring of a Complex Hydraulic System Using Multivariate Statistics," *2015 IEEE International Instrumentation and Measurement Technology Conference (I2MTC)*, Pisa, Italy, 2015. DOI: [10.1109/I2MTC.2015.7151267](https://doi.org/10.1109/I2MTC.2015.7151267).

Dataset: [UCI Machine Learning Repository — Condition Monitoring of Hydraulic Systems](https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems).