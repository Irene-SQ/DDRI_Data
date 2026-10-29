# Processed aircraft SDF dataset

This is the aircraft dataset processed for the DDRI experiments. It contains source model assets, training/test signed-distance samples, surface samples, normalization parameters, and reference renderings.

The dataset contains **59,465 files** totaling **38,568,912,040 bytes** (35.92 GiB) before archive compression. Large files are provided as independent archives in the [processed-sdf-v1 release](https://github.com/Irene-SQ/DDRI_Data/releases/tag/processed-sdf-v1). The Git repository contains directory guides and the complete file inventory; downloading the repository ZIP alone does not include these large files.

## Directory layout

| Directory | Files | Contents |
| --- | ---: | --- |
| `02691156_dataset/` | 48,240 | Aircraft model assets in category `02691156` |
| `SDFdata_train/` | 5,348 | Training signed-distance samples, surface samples, and normalization data |
| `SDFdata_test/` | 1,832 | Test signed-distance samples, surface samples, normalization data, and available visualizations |
| `GT_Renders/` | 4,045 | Reference renderings |
| `GT_Renderings_Open3D/` | 0 | Empty directory retained from the source dataset |

[metadata/files.csv](metadata/files.csv) lists every data file and byte size. [metadata/dataset_summary.json](metadata/dataset_summary.json) reports directory totals.

## Download

From the repository root:

```bash
mkdir -p sdf_download
gh release download processed-sdf-v1 --repo Irene-SQ/DDRI_Data \
  --pattern 'SDF_DATA.*.tar.gz' --pattern 'SDF_DATA.SHA256SUMS' \
  --pattern 'SDF_DATA.release_manifest.json' --pattern 'SDF_DATA.files.sha256' \
  --dir sdf_download
cd sdf_download
sha256sum -c SDF_DATA.SHA256SUMS
for archive in SDF_DATA.*.tar.gz; do
    tar -xzf "$archive" -C ..
done
cd ..
sha256sum -c sdf_download/SDF_DATA.files.sha256
```

Each archive is an independent tar.gz file and extracts into `SDF_DATA/`. Extract all parts for the desired directory into the same parent folder. Archive filenames identify the directory, so training and test files can be downloaded separately. For example, `--pattern 'SDF_DATA.SDFdata_test.part*.tar.gz'` downloads only the test data; download the checksum manifest alongside it and verify the selected files with `sha256sum --ignore-missing -c SDF_DATA.SHA256SUMS`.

## Training and test IDs

- [1780 training target IDs](../cohorts/train_ids.json).
- [456 test target IDs](../cohorts/rendered_targets_456.json).
- [Experimental subsets](../cohorts/README.md): 145, 22, 6, and 24 targets.

Training and test IDs are disjoint. Original ShapeNet target identifiers are retained.

## Read samples

```python
import json
from pathlib import Path
import numpy as np

root = Path("SDF_DATA")
pid = json.loads(Path("cohorts/train_ids.json").read_text())["target_pids"][0]
with np.load(root / "SDFdata_train/SdfSamples/ShapeNetV2/02691156" / f"{pid}.npz") as data:
    positive_samples = data["pos"]
    negative_samples = data["neg"]
with np.load(root / "SDFdata_train/NormalizationParameters/ShapeNetV2/02691156" / f"{pid}.npz") as data:
    offset, scale = data["offset"], data["scale"]
```

Source geometry comes from [ShapeNet](https://shapenet.org/); the SDF preprocessing follows the [DeepSDF](https://github.com/facebookresearch/DeepSDF) data structure. Please acknowledge these sources and the DDRI manuscript. Original third-party data terms continue to apply.
