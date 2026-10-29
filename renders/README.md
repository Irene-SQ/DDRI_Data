# Reconstruction and ground-truth overlays

This collection contains **456 DDRI reconstruction/ground-truth overlay images obtained with a fixed 1-m lateral localization error**. **Red shows the predicted surface; green shows the ground-truth surface points.** The IDs match the complete held-out ShapeNet airplane test split. Each image retains its original pixels.

## Observation and inversion settings

| Parameter | Value |
| --- | --- |
| Unseen aircraft targets | 456 |
| Views | 6 |
| SNR | 10 dB |
| Tx–Rx baseline length | 10 km |
| Nominal crossing position | 1 km |
| Target height | 50 m |
| Wavelength | 0.2 m |
| Trajectory angle | 20° |
| Target speed | 200 m/s |
| Along-track span | 400 m, from −200 m to +200 m |
| Complex samples per view | 1024 |
| Lateral position error supplied to inversion | +1 m along the y-axis |
| Additional height error | 0 m |
| Additional attitude perturbation | 0° |

The saved simulated echoes use the nominal trajectory. The inversion trajectory includes the fixed +1-m y-offset. DDRI optimizes the shape variables using this supplied geometry. Thus, the images show reconstruction under a geometry mismatch. The 50-m target height is an operating parameter; the injected height error is zero.

## Files and experiment identity

`images/<target_id>.png` contains the prediction/ground-truth overlay for that target, copied from the original `<target_id>_overlap.png` evaluation output. `index.json` records the observation settings, image paths, cohort membership, and SHA-256 checksums. The collection includes all 456 available overlays, including imperfect reconstructions.

For these visual comparisons, the prediction is isotropically scaled to match the longest ground-truth bounding-box extent, and the prediction and reference are centered independently. Thus, the overlays compare aligned shape geometry; the original 1-m sensing-geometry error is an inversion condition, not an image translation.

Settings and image checksums are in [index.json](index.json). This rendering campaign has its own observation configuration; cohort membership links the same target identities across experiments.

In particular, selecting the 145 IDs from this gallery retrieves their images under the **1-km, 1-m-error setting**. The view-count/SNR experiment uses its own results and settings.

## Browse the renderings

- [Targets 1–64](gallery/page_01.md)
- [Targets 65–128](gallery/page_02.md)
- [Targets 129–192](gallery/page_03.md)
- [Targets 193–256](gallery/page_04.md)
- [Targets 257–320](gallery/page_05.md)
- [Targets 321–384](gallery/page_06.md)
- [Targets 385–448](gallery/page_07.md)
- [Targets 449–456](gallery/page_08.md)
