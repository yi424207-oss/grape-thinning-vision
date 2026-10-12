"""Recompute aggregate metrics from saved detections; never relabel predictions."""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from evaluate import score

R = Path(__file__).resolve().parents[1]


def clean(q):
    return {k: v for k, v in q.items() if k != 'per_image'}


def bootstrap(q, grouping, seed=20261012, repeats=10000):
    """Cluster-resample capture-number groups, not individual berry boxes."""
    groups = defaultdict(list)
    for row in q['per_image']:
        groups[grouping(row['file'])].append(row)
    totals = []
    for rows in groups.values():
        totals.append([sum(x['tp'] for x in rows),
                       sum(x['predicted'] - x['tp'] for x in rows),
                       sum(x['ground_truth'] - x['tp'] for x in rows),
                       sum(abs(x['error']) for x in rows), len(rows)])
    a = np.asarray(totals, dtype=float)
    rng = np.random.default_rng(seed)
    b = a[rng.integers(0, len(a), size=(repeats, len(a)))].sum(axis=1)
    f1 = 2*b[:, 0] / np.maximum(1, 2*b[:, 0]+b[:, 1]+b[:, 2])
    mae = b[:, 3] / b[:, 4]
    return {'sampling_unit': 'capture-number group', 'groups': len(a),
            'resamples': repeats, 'seed': seed,
            'f1_percentile_95': np.quantile(f1, [.025, .975]).tolist(),
            'mae_percentile_95': np.quantile(mae, [.025, .975]).tolist(),
            'scope': 'Conditional on labels and saved model; assumes numbered groups independent. Plant/orchard independence is unverified. Not training-seed variability.'}


def main(young_prediction_dir=None):
    results = {'protocol': {'matching_iou': .5, 'nms_iou': .5, 'imgsz': 384,
                           'validation_test': 'same confidence for each model/class; confidence selected on validation only',
                           'true_negatives': 'undefined in object detection; not reported'},
               'models': {}, 'cultivar_results': {}}
    for task in ['berry_aux', 'flower', 'young']:
        original = json.loads((R/'reports'/f'{task}_evaluation.json').read_text())
        if task != 'young':
            predictions = json.loads((R/'reports'/f'{task}_predictions.json').read_text())
        elif young_prediction_dir:
            predictions = json.loads((young_prediction_dir/'young_predictions.json').read_text())
        else:
            predictions = None
        model = {'classes': {}, 'test_AP': original['test_AP']}
        for name, c in original['classes'].items():
            threshold = c['test']['threshold']; cls = c['test']['class_id']
            if predictions is not None:
                val = score(predictions['val'], threshold, cls)
                test = score(predictions['test'], threshold, cls)
                for key in ['tp', 'fp', 'fn']:
                    assert test[key] == c['test'][key], (task, name, key)
                assert abs(test['f1']-c['test']['f1']) < 1e-12
            else:
                val, test = c['validation'], c['test']
            entry = {'validation': clean(val), 'test': clean(test)}
            if task != 'young':
                grouping = (lambda n: n.rsplit('_', 1)[0].rsplit('_', 1)[0]+'-'+str((int(n.split('_')[1])-1)//5)) if task=='berry_aux' else (lambda n: str(int(Path(n).stem.split('_')[1])//10))
                entry['conditional_group_bootstrap'] = bootstrap(test, grouping)
            else:
                entry['uncertainty'] = 'Only 2 regions from one test source. No defensible population confidence interval or significance claim.'
            model['classes'][name] = entry
        results['models'][task] = model
        if task == 'berry_aux':
            threshold = original['classes']['berry']['test']['threshold']
            for cultivar in ['Kyoho', 'ShineMuscat', 'SummerBlack']:
                rows = [x for x in predictions['test'] if x['file'].startswith(cultivar+'_')]
                results['cultivar_results'][cultivar] = clean(score(rows, threshold))
    if young_prediction_dir:
        base = json.loads((young_prediction_dir/'young_baseline_predictions.json').read_text())
        young = json.loads((young_prediction_dir/'young_predictions.json').read_text())
        assert [x['gt'] for x in base['test']] == [x['gt'] for x in young['test']]
        comparisons = []
        for threshold in [.3, .4, .5]:
            b, y = score(base['test'], threshold), score(young['test'], threshold)
            comparisons.append({'common_threshold': threshold, 'baseline': clean(b), 'adapted': clean(y),
                                'paired_region_differences': [{'region_index': i+1,
                                'adapted_minus_baseline_absolute_count_error': abs(v['error'])-abs(u['error'])}
                                for i, (u, v) in enumerate(zip(b['per_image'], y['per_image']))]})
        results['young_common_threshold_comparison'] = comparisons
    distributions = {}
    for manifest in ['data_manifest.json', 'flower_manifest.json']:
        rows = json.loads((R/'reports'/manifest).read_text())
        group_rows = defaultdict(list)
        for x in rows: group_rows[str(x['group'])].append(x)
        for g, group in group_rows.items(): assert len({x['split'] for x in group}) == 1
        distributions[manifest] = {'split_images': dict(Counter(x['split'] for x in rows)),
             'groups': [{'group': g, 'split': group[0]['split'], 'original_images': len(group)} for g, group in sorted(group_rows.items())],
             'cultivar_by_split': dict(Counter(x.get('cultivar', 'unrecorded')+':'+x['split'] for x in rows)),
             'plant_orchard_identity': 'not supplied by source; independence not proven'}
    (R/'reports/review_statistics.json').write_text(json.dumps(results, indent=2)+'\n')
    (R/'reports/split_group_distribution.json').write_text(json.dumps(distributions, indent=2)+'\n')
    print(json.dumps({'models': list(results['models']), 'cultivar_F1': {k: v['f1'] for k,v in results['cultivar_results'].items()}, 'young_common_thresholds': results.get('young_common_threshold_comparison')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--young-prediction-dir', type=Path)
    args = parser.parse_args()
    main(args.young_prediction_dir)
