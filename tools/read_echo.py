"""Read a method's complex echo sequences and associated sensing geometry."""
from pathlib import Path
import argparse
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
METHODS = {
    'fullwave': 'FEKO MLFMM',
    'fk': 'FK (fixed T-R orthographic mask)',
    'po': 'Python PO',
    'rlgo': 'FEKO RL-GO + edge diffraction',
}


def load_echo(target, method='fullwave', convention='minus', root=ROOT):
    if target not in ('plane3clean', 'plane4clean', 'plane5clean', 'plane9clean'):
        raise ValueError('Unknown target')
    if method not in METHODS or convention not in ('minus', 'plus'):
        raise ValueError('Unknown method or convention')
    path = Path(root)/'echoes'/target/'data/four_methods_15_baselines.npz'
    with np.load(path, allow_pickle=False) as data:
        index = data['method_names'].tolist().index(METHODS[method])
        key = ('method_echo_exp_minus_jwt_common_reference' if convention == 'minus'
               else 'method_echo_native_common_reference')
        result = {k: data[k].copy() for k in (
            'baseline_names', 'sample_index', 'elapsed_time', 'target_global',
            'tx_global', 'rx_global', 'rotation_model_to_world',
            'incident_polarisations', 'receiver_polarisations', 'frequency_hz',
            'speed_of_light', 'common_reference_constant')}
        result['E_obs'] = data[key][:, index, :].copy()
    if convention == 'minus':
        result['common_reference_constant'] = result['common_reference_constant'].conj()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target')
    parser.add_argument('--method', choices=METHODS, default='fullwave')
    parser.add_argument('--convention', choices=['minus', 'plus'], default='minus')
    args = parser.parse_args()
    result = load_echo(args.target, args.method, args.convention)
    print(METHODS[args.method], 'exp(-jwt)' if args.convention == 'minus' else 'exp(+jwt)')
    for name, array in result.items():
        print(name, array.shape, array.dtype)
