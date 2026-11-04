"""PREVIA v1.1: evaluate alternative operating points on original validation only.

No retraining and, critically, NO reuse of the 2017-2018 held-out test.
Run after successful train_nhanes.py on the original CDC files.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import joblib
import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split

MODULE = Path(__file__).resolve().parents[2] / "PREVIA_ML_NHANES"
sys.path.insert(0, str(MODULE / "scripts"))
from train_nhanes import SEED, FEATURES, binary_metrics, build_cohort  # noqa E402


def candidate_thresholds(p):
    """Every distinct prediction induces a possible binary classification."""
    p = np.asarray(p, dtype=float)
    if p.ndim != 1 or len(p) == 0 or not np.isfinite(p).all():
        raise ValueError("Invalid prediction array")
    if np.any((p < 0) | (p > 1)):
        raise ValueError("Probabilities must be in [0, 1]")
    return np.r_[0.0, np.unique(p), np.nextafter(1.0, 2.0)]


def policy_candidates(y, p):
    """Return policies optimized exclusively from validation predictions."""
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    if len(y) != len(p) or len(set(y)) != 2:
        raise ValueError("Both target classes required, equal y/p lengths")
    points = []
    for th in candidate_thresholds(p):
        predicted = p >= th
        sens = float(predicted[y == 1].mean())
        spec = float((~predicted[y == 0]).mean())
        points.append(dict(threshold=float(th), sensitivity=sens,
                           specificity=spec, selected=int(predicted.sum()),
                           balanced_accuracy=(sens + spec) / 2))
    def high_spec(floor):
        allowed = [q for q in points if q['specificity'] >= floor - 1e-12]
        return max(allowed, key=lambda q:(q['sensitivity'],q['specificity'],-q['threshold']))
    def high_recall(floor):
        allowed = [q for q in points if q['sensitivity'] >= floor - 1e-12]
        return max(allowed, key=lambda q:(q['specificity'],q['sensitivity'],q['threshold']))
    return {
        'specificity_at_least_80pct':high_spec(.80),
        'sensitivity_at_least_70pct':high_recall(.70),
        'sensitivity_at_least_80pct':high_recall(.80),
        'best_balanced_accuracy':max(points,key=lambda q:(q['balanced_accuracy'],-q['threshold']))
    }


def group_metrics(y, p, group, threshold):
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    g = np.asarray(group, dtype=str)
    if not(len(y) == len(p) == len(g)):
        raise ValueError("Group lengths differ")
    output={}
    for name in sorted(set(g)):
        idx=(g == name)
        n = int(idx.sum())
        vals = {'n':n, 'positive_n':int(y[idx].sum()),
                'selected_n':int((p[idx] >= threshold).sum()),
                'selected_rate':float((p[idx] >= threshold).mean())}
        if 0 < vals['positive_n'] < n:
            m = binary_metrics(y[idx], p[idx], threshold)
            vals.update({k:m[k] for k in ('sensitivity_recall','specificity','precision_ppv')})
        else:
            vals.update({'sensitivity_recall':None,'specificity':None,'precision_ppv':None})
        output[name]=vals
    return output


def evaluate(model, X_val, y_val, original_report):
    """No testing or refitting: only predictions on the historic validation partition."""
    if list(X_val.columns) != FEATURES:
        raise ValueError("Unexpected feature order")
    p = model.predict_proba(X_val)[:,1]
    old = original_report['validation_selected']
    auc = roc_auc_score(y_val,p)
    # Match the original report to guard against altered inputs / model or split.
    if abs(auc - old['roc_auc']) > 1e-8 or len(y_val) != original_report['split_counts']['validation']:
        raise ValueError("Saved model/source do not match the initial validation experiment")
    results = {}
    for policy, op in policy_candidates(y_val,p).items():
        th = op['threshold']
        results[policy] = {
            'decision_rule':op,
            'validation_metrics':binary_metrics(y_val,p,th),
            'by_reference_sex':group_metrics(y_val,p,X_val['sex'],th)
        }
    return {
        'n_validation':int(len(y_val)), 'target_positive_validation':int(sum(y_val)),
        'roc_auc_validation':float(auc),
        'pr_auc_validation':float(average_precision_score(y_val,p)),
        'brier_validation':float(brier_score_loss(y_val,p)),
        'policy_comparison':results
    }


def run(raw:Path, trained_results:Path, output:Path):
    summary_path=trained_results/'metrics.json'
    model_path=trained_results/'hba1c_screening_model.joblib'
    if not summary_path.exists() or not model_path.exists():
        raise FileNotFoundError('Missing baseline training metrics/model; run original training first.')
    old=json.loads(summary_path.read_text(encoding='utf-8'))
    X,y,counts=build_cohort(raw)
    if int(old['counts']['eligible_measured_hba1c']) != len(X):
        raise ValueError('Cohort count mismatch')
    X_dev,_X_test,y_dev,_y_test=train_test_split(
        X,y,test_size=.20,random_state=SEED,stratify=y)
    _X_train,X_val,_y_train,y_val=train_test_split(
        X_dev,y_dev,test_size=.25,random_state=SEED,stratify=y_dev)
    del _X_test,_y_test,_X_train,_y_train
    model=joblib.load(model_path)  # trusted locally created artifact only
    evaluation=evaluate(model,X_val,y_val,old)
    report={
        'title':'PREVIA — Comparison of operating thresholds on validation',
        'generated_utc':datetime.now(timezone.utc).isoformat(),
        'original_model':old['selected_model'],
        'objective':'Preliminary discrimination of contemporaneously observed HbA1c >=5.7%, not future CVD',
        'validation_only':True,
        'source_count_total':len(X),
        'method':'Same original stratified validation partition. Saved model unchanged. All thresholds selected only on validation. The previously reported test set is NOT analyzed.',
        'results':evaluation,
        'caveats':[
            'A lower threshold can improve sensitivity but increases false positives; this is not improved ROC-AUC.',
            'Sensitivity targets are reached on validation by construction; no evidence they generalize to new cohorts.',
            'Sex subgroups are NHANES reference labels and not clinical fairness validation.',
            'Prior test set was already viewed and is not a new independent test.',
            'No diagnosis, screening recommendation, clinical action or deployment is supported.',
        ]
    }
    output.mkdir(parents=True,exist_ok=True)
    (output/'comparison.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    lines=['# PREVIA — Optimisation du seuil sur validation','',
           '**Important :** ceci optimise les décisions possibles avec le modèle existant, **sans réentraîner** le ML, **sans reconsulter le jeu de test** et **sans prouver d’efficacité clinique**.',
           '',f"- Modèle initial : `{report['original_model']}`",
           f"- Observations validation : {evaluation['n_validation']}",
           f"- ROC-AUC validation : {evaluation['roc_auc_validation']:.4f}",
           f"- PR-AUC validation : {evaluation['pr_auc_validation']:.4f}",
           f"- Brier validation : {evaluation['brier_validation']:.4f}",
           '', '| Politique | Seuil | Sensibilité | Spécificité | Précision | Faux négatifs | Faux positifs |',
           '|---|---:|---:|---:|---:|---:|---:|']
    labels={'specificity_at_least_80pct':'Spécificité ≥80 % (v1)',
            'sensitivity_at_least_70pct':'Sensibilité ≥70 %',
            'sensitivity_at_least_80pct':'Sensibilité ≥80 %',
            'best_balanced_accuracy':'Précision équilibrée maximale'}
    for key,row in evaluation['policy_comparison'].items():
        m=row['validation_metrics']
        lines.append(f"| {labels[key]} | {m['threshold']:.4f} | {m['sensitivity_recall']:.1%} | {m['specificity']:.1%} | {m['precision_ppv']:.1%} | {m['confusion']['fn']} | {m['confusion']['fp']} |")
    lines+=['','## Lecture correcte',
        '- Les contraintes de sensibilité ou de spécificité sont appliquées uniquement sur validation.',
        '- Un meilleur rappel n’augmente pas nécessairement ROC-AUC ou PR-AUC.',
        '- Un seuil ne peut être proposé pour un usage réel sans critères de coûts, une validation externe et une gouvernance clinique.',
        '- La validation a servi à choisir les seuils : les scores affichés ne sont pas des performances finales indépendantes.',
        '', '## Audit des groupes (source : fichier JSON)',
        'Les taux sont descriptifs ; les groupes peuvent présenter des tailles et prévalences différentes. Aucun jugement sur l’équité clinique.',
        '', '## Travail scientifique restant',
        'Conserver la v1 comme seule évaluation test historique, valider le protocole sur un cycle NHANES différent et, à terme, dans la population cible avant tout usage en santé.']
    (output/'RAPPORT_SEUILS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines[:17]))
    print(f'\nREPORT: {output / "RAPPORT_SEUILS.md"}')
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--raw',type=Path,default=MODULE/'data'/'raw')
    parser.add_argument('--trained-results',type=Path,default=MODULE/'results'/'nhanes')
    parser.add_argument('--out',type=Path,default=MODULE/'results'/'threshold_study')
    args=parser.parse_args()
    run(args.raw,args.trained_results,args.out)

if __name__=='__main__':main()
