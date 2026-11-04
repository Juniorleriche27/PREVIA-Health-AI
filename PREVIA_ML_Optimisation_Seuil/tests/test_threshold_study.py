import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'scripts'))
import numpy as np
from optimize_decisions import policy_candidates,group_metrics,candidate_thresholds

def test_policy_targets():
    y=np.r_[[0]*8,[1]*8]
    p=np.array([.11,.12,.18,.27,.32,.43,.54,.71,.31,.41,.52,.6,.63,.72,.78,.92])
    policies=policy_candidates(y,p)
    assert policies['specificity_at_least_80pct']['specificity'] >= .8
    assert policies['sensitivity_at_least_70pct']['sensitivity'] >= .7
    assert policies['sensitivity_at_least_80pct']['sensitivity'] >= .8
    assert 0 <= policies['best_balanced_accuracy']['balanced_accuracy'] <= 1

def test_all_equal_predictions():
    y=[0,0,1,1]
    p=[.5]*4
    res=policy_candidates(y,p)
    assert res['sensitivity_at_least_80pct']['sensitivity'] == 1.0
    assert res['specificity_at_least_80pct']['specificity'] == 1.0

def test_group_denominators():
    res=group_metrics(np.array([0,1,0,1]),np.array([.2,.8,.4,.9]),['A','A','B','B'],.5)
    assert res['A']['n']+res['B']['n']==4
    assert res['A']['selected_n']==1
    assert res['B']['selected_n']==1

def test_invalid_array():
    try:candidate_thresholds([.2,float('nan')])
    except ValueError:pass
    else:assert False

def test_evaluate_matches_saved_reference_metrics():
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.metrics import roc_auc_score
    from optimize_decisions import evaluate
    rng=np.random.default_rng(16)
    n=130
    X=pd.DataFrame({'age':rng.integers(40,75,n),'sex':rng.choice(['male','female'],n),
                    'bmi':rng.uniform(19,38,n),'sbp':rng.uniform(98,179,n),
                    'smoking':rng.choice(['never','former','current'],n)})
    y=np.asarray((X['bmi'] > 29) | ((X['age'] > 60)&(rng.random(n)>.3)),dtype=int)
    proc=ColumnTransformer([('num','passthrough',['age','bmi','sbp']),
         ('cat',OneHotEncoder(handle_unknown='ignore'),['sex','smoking'])])
    model=Pipeline([('prep',proc),('clf',LogisticRegression(max_iter=3000))]).fit(X,y)
    p=model.predict_proba(X)[:,1]
    report={'validation_selected':{'roc_auc':roc_auc_score(y,p)},
            'split_counts':{'validation':len(y)}}
    r=evaluate(model,X,y,report)
    assert len(r['policy_comparison'])==4
    assert r['policy_comparison']['sensitivity_at_least_80pct']['validation_metrics']['sensitivity_recall'] >= .8
