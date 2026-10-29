# Experimental target lists

Each JSON contains `n_targets`, `description`, and `target_pids`. IDs retain their original ShapeNet spelling. Each list is sorted and contains unique IDs.

| File | Targets | Purpose |
| --- | ---: | --- |
| [rendered_targets_456.json](rendered_targets_456.json) | 456 | Complete test split represented in the released reconstruction gallery |
| [targets_145.json](targets_145.json) | 145 | View-count and SNR evaluation cohort |
| [targets_22.json](targets_22.json) | 22 | Profile comparison, prior-only references, and original sensitivity cohort |
| [targets_6.json](targets_6.json) | 6 | Shared loss-removal and no-SDF-prior ablation cohort |
| [targets_24.json](targets_24.json) | 24 | Joint geometry-refinement cohort and target list for sensitivity completion |

The lists satisfy `6 ⊂ 22 ⊂ 24 ⊂ 145 ⊂ 456`. All belong to the held-out test split and are disjoint from training IDs.

These files define cohort membership. The number of valid reconstructions for a particular condition is determined by that experiment's result records. The 24-ID list does not assert that every historical condition was originally evaluated on all 24 targets.

Image paths and per-target cohort membership are available in [renders/index.json](../renders/index.json). Source checksums and list provenance are recorded in [metadata/cohort_provenance.json](../metadata/cohort_provenance.json).
