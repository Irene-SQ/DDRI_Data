# DDRI_Data

Data accompanying **Diffraction-Driven Inversion for 3-D Aircraft Shape Reconstruction From Sparse Multistatic Forward Scatter Radar Echoes**.

This repository provides three collections:

1. **Electromagnetic echo simulations:** four watertight aircraft targets, each with 15 bistatic baselines and 1024 complex samples per baseline. The supplied methods are FEKO MLFMM, Fresnel–Kirchhoff (FK), Python physical optics (PO), and FEKO RL-GO with edge diffraction.
2. **Reconstruction overlays and target IDs:** reconstruction/ground-truth overlays for all 456 held-out aircraft in the six-view, 10-dB, 1-km experiment with a **1-m lateral localization error**, plus JSON lists for the 1780 training targets and the 145-, 22-, 6-, and 24-target experimental cohorts.
3. **Processed SDF dataset:** aircraft model assets, training/test signed-distance and surface samples, normalization parameters, and reference renderings. Approximately 35.9 GiB before compression, distributed through GitHub Releases.

## Contents

| Directory | Contents |
| --- | --- |
| [echoes/](echoes/README.md) | Complex echoes, sensing geometry, four target meshes, and array documentation |
| [renders/](renders/README.md) | 456 reconstruction/ground-truth overlays, a JSON image index, and paginated galleries |
| [cohorts/](cohorts/README.md) | Target ID lists and relationships between experimental cohorts |
| [SDF_DATA/](SDF_DATA/README.md) | Processed dataset directory guide, inventory, and release download instructions |
| `metadata/` | Source provenance and file inventory |
| `tools/` | NumPy echo reader and dataset verifier |

The echoes, overlays, and ID lists are included directly in the repository. Clone it or use GitHub's **Code → Download ZIP**. Download the processed SDF files separately using [SDF_DATA/README.md](SDF_DATA/README.md).

```bash
git clone https://github.com/Irene-SQ/DDRI_Data.git
cd DDRI_Data
python -m pip install -r requirements.txt
python tools/verify_dataset.py
python tools/read_echo.py plane3clean --method fullwave
```

## Read target lists

```python
import json
from pathlib import Path

cohort = json.loads(Path("cohorts/targets_22.json").read_text())
target_ids = cohort["target_pids"]
assert len(target_ids) == cohort["n_targets"]
image = Path("renders/images") / f"{target_ids[0]}.png"
```

The cohort files identify targets. Each experiment's observation settings remain separate; the released 456-image gallery uses the configuration documented in [renders/README.md](renders/README.md).

## Sources and citation

The 456 aircraft IDs originate from the [ShapeNet](https://shapenet.org/) airplane category (`ShapeNetV2/02691156`). Please acknowledge ShapeNet and the DDRI paper when using these results. The electromagnetic files identify the four simulation targets as `plane3clean`, `plane4clean`, `plane5clean`, and `plane9clean`.

The final publication citation and DOI will be added when available.
