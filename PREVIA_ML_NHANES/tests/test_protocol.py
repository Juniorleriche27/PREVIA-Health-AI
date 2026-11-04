from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import numpy as np
from train_nhanes import binary_metrics,threshold_from_validation,FEATURES,FILES

def test_features_exclude_target_and_id():
    assert 'LBXGH' not in FEATURES and 'SEQN' not in FEATURES
    assert 'GHB_J' in FILES and 'DIQ_J' in FILES

def test_metrics_perfect():
    x=binary_metrics([0,0,1,1],[.1,.2,.8,.9],.5)
    assert x['roc_auc']==1
    assert x['confusion']=={'tn':2,'fp':0,'fn':0,'tp':2}

def test_threshold_specificity():
    y=np.array([0,0,0,0,0,1,1,1])
    p=np.array([.1,.2,.3,.4,.5,.4,.6,.8])
    t=threshold_from_validation(y,p)
    assert binary_metrics(y,p,t)['specificity']>=.8

def test_build_cohort_join_and_no_label_leak(monkeypatch,tmp_path):
    import pandas as pd
    import train_nhanes as mod
    rows=300
    ids=list(range(rows))
    d={
      'DEMO_J':pd.DataFrame({'SEQN':ids,'RIDAGEYR':[45+i%25 for i in ids],
            'RIAGENDR':[1+i%2 for i in ids],'WTMEC2YR':[100+i for i in ids]}),
      'BMX_J':pd.DataFrame({'SEQN':ids,'BMXBMI':[24+i%15 for i in ids]}),
      'BPX_J':pd.DataFrame({'SEQN':ids,'BPXSY1':[120+i%25 for i in ids],
        'BPXSY2':[120+i%25 for i in ids],'BPXSY3':[120+i%25 for i in ids]}),
      'SMQ_J':pd.DataFrame({'SEQN':ids,'SMQ020':[2]*rows,'SMQ040':[np.nan]*rows}),
      'DIQ_J':pd.DataFrame({'SEQN':ids,'DIQ010':[2]*rows}),
      'GHB_J':pd.DataFrame({'SEQN':ids,'LBXGH':[5.4+i%5*.2 for i in ids]})}
    monkeypatch.setattr(mod,'read_xpt',lambda _root,name,_fields:d[name])
    X,y,counts=mod.build_cohort(tmp_path)
    assert len(X)==300 and len(y)==300
    assert list(X)==mod.FEATURES and 'SEQN' not in X.columns and 'LBXGH' not in X.columns
    assert set(np.unique(y))=={0,1}
    assert counts['eligible_measured_hba1c']==300
