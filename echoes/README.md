# Electromagnetic echo simulations

Four aircraft targets are provided: `plane3clean`, `plane4clean`, `plane5clean`, and `plane9clean`. Each target has **15 bistatic baselines**, **1024 samples per baseline**, and the following four forward methods:

1. FEKO MLFMM (full-wave).
2. FK with a fixed orthographic shadow mask perpendicular to the Tx–Rx direction.
3. Python physical optics (PO).
4. FEKO RL-GO with edge diffraction.

The transmitted excitation is a 3-GHz single-frequency field. Target motion is represented by sampling successive positions. Delivered signals are target-induced complex scattered fields with no added random noise or direct Tx–Rx field. Downstream noisy inversion experiments add their noise separately.

## Files

Each target directory contains:

- `data/four_methods_15_baselines.npz`: all four methods and associated geometry.
- `data/ddri_15_baselines.npz`: MLFMM observations and associated geometry.
- `mesh/<target>_source.obj`: the reference target geometry in its original coordinates and dimensions.

[index.json](index.json) identifies each target and file. [npz_schema.json](npz_schema.json) lists every array's shape and dtype. [sensing_parameters_15_baselines.csv](sensing_parameters_15_baselines.csv) summarizes the sensing geometry. The NPZ arrays are authoritative.

## Main arrays

Let `B=15`, `M=4`, and `L=1024`. Method order is given by `method_names`; baseline order is given by `baseline_names`.

| Key | Shape | Meaning / units |
| --- | --- | --- |
| `method_echo_exp_minus_jwt_common_reference` | `(B,M,L)` | Four-method complex fields in the `exp(-jωt)` convention |
| `method_echo_native_common_reference` | `(B,M,L)` | Four-method complex fields in the native `exp(+jωt)` convention |
| `echo_exp_minus_jwt_common_reference` | `(B,L)` | MLFMM fields in the `exp(-jωt)` convention |
| `echo_native_absolute` | `(B,L)` | MLFMM fields before the shared reference transform, native convention |
| `sample_index` | `(B,L)` | Zero-based sample index |
| `elapsed_time` | `(B,L)` | Local observation-window time in seconds |
| `target_global` | `(B,L,3)` | Target-center positions in metres |
| `tx_global`, `rx_global` | `(B,3)` | Transmitter/receiver positions in metres |
| `rotation_model_to_world` | `(B,3,3)` | Model-to-world rotation matrices |
| `incident_polarisations`, `receiver_polarisations` | `(B,L,3)` | Polarization vectors |
| `beta_deg` | `(B,L)` | Bistatic angle in degrees |
| `frequency_hz` | scalar | Excitation frequency in hertz |
| `common_reference_constant` | scalar complex | Shared field-reference multiplier in the native convention |

Position arrays use metres and time arrays use seconds. The local time origins are per-baseline observation-window origins. For a model-coordinate column vector, `x_world = R @ x_model + target_global`.

## Field and phase conventions

The complex fields use the simulation source amplitude and stored common reference. For the native convention, the MLFMM arrays satisfy

```text
echo_native_common_reference = echo_native_absolute * common_reference_constant
```

The `exp(-jωt)` arrays are the complex conjugates of their native counterparts. Accordingly, the shared multiplier is conjugated when using the minus convention. The FK renderer with a `+j` prefactor and `exp(+jkR)` uses the minus-convention observations. Read a single convention consistently across observations and the forward model.

## Read an observation

From the repository root:

```python
import numpy as np

with np.load("echoes/plane3clean/data/four_methods_15_baselines.npz",
             allow_pickle=False) as data:
    method_names = data["method_names"].tolist()
    method = method_names.index("FEKO MLFMM")
    E_obs = data["method_echo_exp_minus_jwt_common_reference"][:, method, :]
    time_s = data["elapsed_time"]
    target_positions_m = data["target_global"]
    tx_m, rx_m = data["tx_global"], data["rx_global"]
    assert E_obs.shape == (15, 1024)
```

`python tools/read_echo.py plane3clean --method fk` prints the selected method and array shapes. `python tools/verify_dataset.py` checks the release checksums, ID sets, phase-conjugation relationships, and geometry arrays.
