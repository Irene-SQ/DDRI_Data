"""Verify release integrity, exact cohort membership, and echo consistency."""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT/'metadata/files.json').read_text())
    for item in manifest['files']:
        path = ROOT/item['path']
        if path.stat().st_size != item['bytes']:
            raise ValueError(f'Size mismatch: {path}')
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'Checksum mismatch: {path}')
    cohorts = {}
    for n in (6, 22, 24, 145, 456):
        name = f'targets_{n}' if n != 456 else 'rendered_targets_456'
        obj = json.loads((ROOT/'cohorts'/f'{name}.json').read_text())
        ids = obj['target_pids']
        assert len(ids) == len(set(ids)) == obj['n_targets'] == n
        cohorts[n] = set(ids)
    assert cohorts[6] < cohorts[22] < cohorts[24] < cohorts[145] < cohorts[456]
    renders = json.loads((ROOT/'renders/index.json').read_text())
    assert len(renders['images']) == 456
    assert {r['target_id'] for r in renders['images']} == cohorts[456]
    for row in renders['images']:
        path = ROOT/'renders'/row['image']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        expected = {f'targets_{n}' for n in (6, 22, 24, 145) if row['target_id'] in cohorts[n]}
        assert set(row['cohorts']) == expected
    echo_index = json.loads((ROOT/'echoes/index.json').read_text())
    assert len(echo_index['targets']) == 4
    for target in echo_index['targets']:
        with np.load(ROOT/'echoes'/target['data'], allow_pickle=False) as data:
            native = data['method_echo_native_common_reference']
            assert native.shape == (15, 4, 1024)
            assert len(set(data['baseline_names'].tolist())) == 15
            assert len(set(data['method_names'].tolist())) == 4
            for key in data.files:
                if data[key].dtype.kind in 'fc':
                    assert np.isfinite(data[key]).all(), key
            np.testing.assert_array_equal(data['method_echo_exp_minus_jwt_common_reference'], native.conj())
            np.testing.assert_array_equal(data['echo_native_common_reference'], native[:, 0])
            np.testing.assert_allclose(data['echo_native_absolute']*data['common_reference_constant'],
                                       native[:, 0], rtol=1e-12, atol=1e-13)
            assert np.all(np.diff(data['elapsed_time'], axis=1) > 0)
            np.testing.assert_array_equal(data['sample_index'], np.broadcast_to(np.arange(1024), (15, 1024)))
            for b in range(15):
                rotation = data['rotation_model_to_world'][b]
                np.testing.assert_allclose(rotation.T @ rotation, np.eye(3), atol=1e-10)
                np.testing.assert_allclose(np.linalg.det(rotation), 1, atol=1e-10)
                for key in ('tx', 'rx'):
                    expected = (data[f'{key}_global'][b]-data['target_global'][b]) @ rotation
                    np.testing.assert_allclose(expected, data[f'{key}_target_frame'][b], atol=1e-9)
            mesh = ROOT/'echoes'/target['target']/str(data['model_path'])
            assert hashlib.sha256(mesh.read_bytes()).hexdigest() == str(data['model_sha256'])
        with np.load(ROOT/'echoes'/target['fullwave_data'], allow_pickle=False) as full:
            np.testing.assert_array_equal(full['echo_native_common_reference'], native[:, 0])
    print('PASS: file checksums, 456 images, five cohort lists, and four 15-baseline echo datasets.')


if __name__ == '__main__':
    main()
