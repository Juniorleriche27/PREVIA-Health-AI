"""PREVIA — reproducible NHANES 2017-2018 HbA1c screening research.

No cardiovascular event prediction and no clinical decision support.
Full metrics require actual CDC SAS XPT source files.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
    confusion_matrix, f1_score, precision_score, recall_score,
    roc_auc_score, roc_curve, balanced_accuracy_score, log_loss)
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.inspection import permutation_importance

BASE = Path(__file__).resolve().parents[1]
FILES = ('DEMO_J','BMX_J','BPX_J','SMQ_J','DIQ_J','GHB_J')
FEATURES = ['age','sex','bmi','sbp','smoking']
NUM = ['age','bmi','sbp']
CAT = ['sex','smoking']
SEED=2026


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def read_xpt(root: Path, name: str, selected: list[str]) -> pd.DataFrame:
    path=root/(name+'.xpt')
    if not path.exists():
        raise FileNotFoundError(f'Missing official CDC file: {path}. Run download_nhanes.ps1.')
    df=pd.read_sas(path,format='xport',encoding='utf-8')
    names=['SEQN']+[c for c in selected if c in df.columns]
    missing=[c for c in selected if c not in df.columns]
    if missing:raise ValueError(f'{name}: missing documented columns {missing}')
    df=df[names].copy()
    if df.SEQN.isna().any() or df.SEQN.duplicated().any():
        raise ValueError(f'{name} missing or duplicate SEQN; refusing many-to-many merge')
    return df


def build_cohort(raw:Path):
    demo=read_xpt(raw,'DEMO_J',['RIDAGEYR','RIAGENDR','WTMEC2YR'])
    demo=demo[demo.RIDAGEYR.between(40,74)].copy()
    n_age=int(len(demo))
    data=demo
    spec={'BMX_J':['BMXBMI'], 'BPX_J':['BPXSY1','BPXSY2','BPXSY3'],
          'SMQ_J':['SMQ020','SMQ040'], 'DIQ_J':['DIQ010'], 'GHB_J':['LBXGH']}
    for fname,fields in spec.items():
        right=read_xpt(raw,fname,fields)
        before=len(data)
        data=data.merge(right,on='SEQN',how='left',validate='one_to_one')
        if len(data)!=before:raise ValueError('Join expanded rows')
    # Exclude self-reported diagnosed diabetes. DIQ010=3 (borderline) retained;
    # exclude unknown refusals. Diagnosis is NOT a predictor.
    data=data[data.DIQ010.isin([2,3])].copy()
    n_undiagnosed=int(len(data))
    data['sbp']=data[['BPXSY1','BPXSY2','BPXSY3']].where(
        lambda x:(x>=70)&(x<=260)).mean(axis=1)
    data['age']=data['RIDAGEYR']
    data['bmi']=data['BMXBMI'].where(data.BMXBMI.between(12,75))
    data['sex']=data.RIAGENDR.map({1:'male',2:'female'})
    # 2=never smoked 100; 1=smoked 100 and SMQ040 1/2=current or 3=former
    data['smoking']=pd.Series(index=data.index,dtype='object')
    data.loc[data.SMQ020.eq(2),'smoking']='never'
    data.loc[data.SMQ020.eq(1)&data.SMQ040.isin([1,2]),'smoking']='current'
    data.loc[data.SMQ020.eq(1)&data.SMQ040.eq(3),'smoking']='former'
    data['hba1c']=data['LBXGH'].where(data.LBXGH.between(3,18))
    before_target=len(data)
    data=data[data.hba1c.notna()].copy()
    if len(data)<250:raise ValueError('Too few measured HbA1c observations')
    data['target']=(data.hba1c>=5.7).astype(int)
    if data.target.nunique()!=2:raise ValueError('One-class target')
    # Exclude rows with every feature unknown, other missing values imputed within folds.
    data=data[data[FEATURES].notna().sum(axis=1)>=2].copy()
    missing={name:int(data[name].isna().sum()) for name in FEATURES}
    counts={'initial_aged_40_74':n_age,'without_known_diabetes':n_undiagnosed,
      'before_hba1c_missing_filter':int(before_target),
      'eligible_measured_hba1c':int(len(data)),
      'target_positive_n':int(data.target.sum()),
      'target_negative_n':int((1-data.target).sum()),
      'target_fraction':round(float(data.target.mean()),5),
      'missing_features':missing,
      'sex_counts':{str(k):int(v) for k,v in data.sex.value_counts(dropna=False).items()}}
    # Only X/y retained. No SEQN in training artifacts or CSV.
    return data[FEATURES].copy(),data.target.copy(),counts


def pipelines():
    pre_scaled=ColumnTransformer([
      ('numeric',Pipeline([('imputer',SimpleImputer(strategy='median')),
                           ('scale',StandardScaler())]),NUM),
      ('categorical',Pipeline([('imputer',SimpleImputer(strategy='most_frequent')),
                               ('onehot',OneHotEncoder(handle_unknown='ignore'))]),CAT),
    ])
    pre_unscaled=ColumnTransformer([
      ('numeric',SimpleImputer(strategy='median'),NUM),
      ('categorical',Pipeline([('imputer',SimpleImputer(strategy='most_frequent')),
                               ('onehot',OneHotEncoder(handle_unknown='ignore'))]),CAT),
    ])
    return {
      'logistic':(Pipeline([('prep',pre_scaled),('model',LogisticRegression(max_iter=1500,random_state=SEED))]),
          {'model__C':[0.01,0.1,1,10], 'model__class_weight':[None,'balanced']}),
      'random_forest':(Pipeline([('prep',pre_unscaled),('model',RandomForestClassifier(random_state=SEED,n_jobs=1))]),
          {'model__n_estimators':[150,250], 'model__min_samples_leaf':[2,5,10,20],
           'model__max_depth':[4,8,None], 'model__max_features':['sqrt',0.8]}),
      'hist_gradient_boosting':(Pipeline([('prep',pre_unscaled),('model',HistGradientBoostingClassifier(random_state=SEED))]),
          {'model__learning_rate':[0.025,0.05,0.1], 'model__max_leaf_nodes':[7,15,31],
           'model__l2_regularization':[0,1,5], 'model__min_samples_leaf':[20,40]})
    }


def binary_metrics(y, p, threshold):
    y=np.asarray(y,dtype=int)
    p=np.asarray(p,dtype=float)
    pred=(p>=threshold).astype(int)
    tn,fp,fn,tp=[int(x) for x in confusion_matrix(y,pred,labels=[0,1]).ravel()]
    return {
      'n':int(len(y)),'positives':int(y.sum()),'positives_rate':float(y.mean()),
      'roc_auc':float(roc_auc_score(y,p)),
      'pr_auc_average_precision':float(average_precision_score(y,p)),
      'brier':float(brier_score_loss(y,p)),
      'log_loss':float(log_loss(y,p,labels=[0,1])),
      'threshold':float(threshold), 'sensitivity_recall':float(recall_score(y,pred,zero_division=0)),
      'specificity':float(tn/(tn+fp)) if tn+fp else None,
      'precision_ppv':float(precision_score(y,pred,zero_division=0)),
      'f1':float(f1_score(y,pred,zero_division=0)),
      'balanced_accuracy':float(balanced_accuracy_score(y,pred)),
      'confusion':{'tn':tn,'fp':fp,'fn':fn,'tp':tp}
    }


def threshold_from_validation(y,p,min_specificity=0.8):
    """Maximise sensitivity with specificity >=0.8, measured on validation ONLY."""
    candidates=np.r_[np.linspace(0.05,0.95,181), 1.000001]
    ranks=[]
    y=np.asarray(y)
    for t in candidates:
        pred=(p>=t)
        spec=float(((~pred)&(y==0)).sum()/max(1,(y==0).sum()))
        sens=float((pred&(y==1)).sum()/max(1,(y==1).sum()))
        if spec>=min_specificity:ranks.append((sens,spec,float(t)))
    if not ranks:return 0.5
    return sorted(ranks,key=lambda a:(-a[0],a[2]))[0][2]


def train(X,y,counts,raw:Path,out:Path,folds=4,n_iter=12):
    out.mkdir(parents=True,exist_ok=True)
    # Fixed stratified split train 60%, validation 20%, final untouched test 20%.
    X_dev,X_test,y_dev,y_test=train_test_split(X,y,test_size=0.2,random_state=SEED,stratify=y)
    X_train,X_val,y_train,y_val=train_test_split(X_dev,y_dev,test_size=0.25,
                                                  random_state=SEED,stratify=y_dev)
    cv=StratifiedKFold(n_splits=folds,shuffle=True,random_state=SEED)
    contenders=[]
    baseline=DummyClassifier(strategy='prior').fit(X_train,y_train)
    p_baseline=baseline.predict_proba(X_val)[:,1]
    contenders.append({'model':'dummy_prior','cv_roc_auc':0.5,
        'validation':binary_metrics(y_val,p_baseline,0.5), 'params':{}})
    fitted={}
    for name,(model,params) in pipelines().items():
        n_candidates= min(n_iter, int(np.prod([len(v) for v in params.values()])))
        search=RandomizedSearchCV(model,params,n_iter=n_candidates,scoring='roc_auc',cv=cv,
                                  random_state=SEED,n_jobs=1,refit=True,error_score='raise')
        search.fit(X_train,y_train)
        p=search.predict_proba(X_val)[:,1]
        res={'model':name,'cv_roc_auc':float(search.best_score_),
              'validation':binary_metrics(y_val,p,0.5), 'params':search.best_params_}
        fitted[name]=(search.best_estimator_,p)
        contenders.append(res)
    # Choose using validation ROC-AUC, never final held-out test.
    winner=max((c for c in contenders if c['model']!='dummy_prior'),
               key=lambda c:(c['validation']['roc_auc'],-c['validation']['brier']))
    name=winner['model']; trained,p_val=fitted[name]
    t=threshold_from_validation(y_val,p_val,min_specificity=0.8)
    # Model used on test is precisely the fitted training-only model;
    # no refit on train+val before held-out metrics.
    p_test=trained.predict_proba(X_test)[:,1]
    p_val=np.asarray(p_val)
    baseline_test=baseline.predict_proba(X_test)[:,1]
    test=binary_metrics(y_test,p_test,t)
    base_metrics=binary_metrics(y_test,baseline_test,0.5)
    # Bootstrap test metrics CIs describe sampling of test predictions only,
    # NOT external validity, sampling design, or clinical confidence intervals.
    rng=np.random.default_rng(SEED)
    boots=[]
    y_arr=y_test.to_numpy()
    for _ in range(500):
        idx=rng.integers(0,len(y_arr),len(y_arr))
        if len(set(y_arr[idx]))<2:continue
        boots.append(roc_auc_score(y_arr[idx],p_test[idx]))
    ci=np.quantile(boots,[.025,.975]).tolist()
    # Feature importance measured on validation (not causal explanation).
    perm=permutation_importance(trained,X_val,y_val,scoring='roc_auc',
                                n_repeats=8,random_state=SEED,n_jobs=1)
    importance=sorted([{'feature':f,'auc_drop_mean':float(a),'auc_drop_std':float(b)}
                       for f,a,b in zip(FEATURES,perm.importances_mean,perm.importances_std)],
                      key=lambda x:-x['auc_drop_mean'])
    digest={f:sha256(raw/(f+'.xpt')) for f in FILES}
    report={'study':'NHANES 2017-2018 observed HbA1c >=5.7% (screening research)',
      'created_utc':datetime.now(timezone.utc).isoformat(),'source':'CDC NHANES 2017–2018',
      'source_file_sha256':digest, 'counts':counts,
      'design':{'split':'60% train / 20% validation / 20% untouched test',
                'seed':SEED,'stratified':True,'cv_folds':folds,
                'tuning':'RandomizedSearchCV on training only',
                'selection':'highest validation ROC AUC; tie by Brier',
                'threshold':'highest validation recall with specificity >=0.80',
                'input_features':FEATURES,
                'exclusion':'known diabetes DIQ010=1; unknown diagnosis excluded',
                'survey_weights':'not applied; unweighted predictive sample; no population estimates'},
      'split_counts':{'train':len(X_train),'validation':len(X_val),'test':len(X_test)},
      'contenders':contenders,'selected_model':name,
      'validation_selected':binary_metrics(y_val,p_val,t),
      'heldout_test':test,'heldout_dummy_prior':base_metrics,
      'validation_permutation_importance_auc_drop':importance,
      'heldout_test_auc_bootstrap_95pct_descriptive':ci,
      'limitations':[
         'Cross-sectional association with measured HbA1c, not future disease or 10-year CVD events.',
         'Self-reported known diabetes excluded, not necessarily undiagnosed cases.',
         'No survey-weighted or nationally representative population statistics.',
         'NHANES participants in United States; no validation in Togo.',
         'Missing measurements and social context can bias results.',
         'HbA1c can be misleading in some hemoglobin disorders and conditions.',
         'Not clinical diagnostic or referral software.',
         'Only validated model metrics from holdout, no clinical utility demonstrated.'
      ]}
    (out/'metrics.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    joblib.dump(trained,out/'hba1c_screening_model.joblib')
    # No subject-level test predictions or respondent identifiers exported.
    summary=[f'# PREVIA — rapport ML NHANES 2017–2018',
       '',f'**Date UTC :** {report["created_utc"]}',
       f'**Cible :** HbA1c observée ≥5,7 % (pas une prédiction cardiovasculaire).',
       f'**Population :** {len(X)} adultes 40–74 ans, hors diabète déjà déclaré.',
       f'**Prévalence non pondérée de la cible :** {counts["target_fraction"]:.2%}',
       f'**Partition :** {len(X_train)} entraînement / {len(X_val)} validation / {len(X_test)} test.',
       '', '## Comparaison et optimisation (validation uniquement)',
       '| Modèle | ROC-AUC CV | ROC-AUC validation | PR-AUC validation | Brier validation |',
       '|---|---:|---:|---:|---:|']
    for x in contenders:
        summary.append(f'| {x["model"]} | {x["cv_roc_auc"]:.3f} | {x["validation"]["roc_auc"]:.3f} | {x["validation"]["pr_auc_average_precision"]:.3f} | {x["validation"]["brier"]:.3f} |')
    summary += ['',f'**Modèle retenu :** {name} (choisi sans consulter le test).','',
      '## Scores finaux — jeu de test indépendant',
      f'- ROC-AUC : **{test["roc_auc"]:.3f}**',
      f'- PR-AUC : **{test["pr_auc_average_precision"]:.3f}**',
      f'- Brier : **{test["brier"]:.3f}**',
      f'- Seuil retenu sur validation : **{t:.3f}**',
      f'- Sensibilité : **{test["sensitivity_recall"]:.3f}**',
      f'- Spécificité : **{test["specificity"]:.3f}**',
      f'- Précision : **{test["precision_ppv"]:.3f}**',
      f'- Matrice TN/FP/FN/TP : **{test["confusion"]}**',
      f'- IC bootstrap descriptif AUC (test) : **[{ci[0]:.3f}, {ci[1]:.3f}]**',
      '', '## Importance des variables (permutation, validation)',
      '| Variable | Baisse moyenne ROC-AUC après permutation |', '|---|---:|',
      *[f'| {r["feature"]} | {r["auc_drop_mean"]:.4f} |' for r in importance],
      '', "Ces importances décrivent l’association des variables au résultat du modèle; elles ne prouvent pas de causalité.",'', '## Validité et limites',
      *[f'- {v}' for v in report['limitations']], '',
      'Résultats : `metrics.json`. Modèle : `hba1c_screening_model.joblib`.']
    (out/'RAPPORT_ML.md').write_text('\n'.join(summary)+'\n',encoding='utf-8')
    print('\n'.join([f'OBSERVATIONS: {len(X)}; positives: {y.sum()}',
          f'SELECTED: {name}',f'TEST ROC AUC: {test["roc_auc"]:.4f}',
          f'TEST PR AUC: {test["pr_auc_average_precision"]:.4f}',
          f'TEST BRIER: {test["brier"]:.4f}',f'TEST recall: {test["sensitivity_recall"]:.4f}',
          f'TEST specificity: {test["specificity"]:.4f}',f'REPORT: {out/"RAPPORT_ML.md"}']))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--raw',type=Path,default=BASE/'data'/'raw')
    p.add_argument('--out',type=Path,default=BASE/'results'/'nhanes')
    p.add_argument('--n-iter',type=int,default=12)
    args=p.parse_args()
    X,y,c=build_cohort(args.raw)
    train(X,y,c,args.raw,args.out,n_iter=args.n_iter)

if __name__=='__main__':main()
