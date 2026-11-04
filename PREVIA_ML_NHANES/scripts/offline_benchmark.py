"""REAL offline training smoke test on sklearn diabetes (not NHANES).
442 observations; regression target disease progression 1 year.
Do not compare reported metrics to NHANES HbA1c classification.
"""
from pathlib import Path
import json
from datetime import datetime,timezone
import joblib
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split,GridSearchCV,KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge,ElasticNet
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error,mean_squared_error

SEED=2026
OUT=Path(__file__).resolve().parents[1]/'results'/'offline_smoketest'
OUT.mkdir(parents=True,exist_ok=True)
DS=load_diabetes()
X,y=DS.data,DS.target
X_dev,X_test,y_dev,y_test=train_test_split(X,y,test_size=.2,random_state=SEED)
X_train,X_val,y_train,y_val=train_test_split(X_dev,y_dev,test_size=.25,random_state=SEED)
cv=KFold(n_splits=4,shuffle=True,random_state=SEED)

def score(y,p):
 return {'r2':float(r2_score(y,p)),'mae':float(mean_absolute_error(y,p)),
         'rmse':float(np.sqrt(mean_squared_error(y,p)))}

models={
 'ridge':(make_pipeline(StandardScaler(),Ridge()),{'ridge__alpha':[.1,1,10,100,1000]}),
 'elasticnet':(make_pipeline(StandardScaler(),ElasticNet(max_iter=20000,random_state=SEED)),
  {'elasticnet__alpha':[.01,.1,1,10],'elasticnet__l1_ratio':[.1,.5,.9]}),
 'random_forest':(RandomForestRegressor(random_state=SEED,n_jobs=1),
  {'n_estimators':[100,200],'min_samples_leaf':[2,5,10],'max_depth':[4,8,None]}),
 'hist_gradient_boosting':(HistGradientBoostingRegressor(random_state=SEED),
  {'learning_rate':[.025,.05,.1], 'max_leaf_nodes':[7,15], 'min_samples_leaf':[10,20]})
}
results=[]
for name,(model,params) in models.items():
 search=GridSearchCV(model,params,cv=cv,scoring='neg_mean_absolute_error',n_jobs=1)
 search.fit(X_train,y_train)
 results.append({'name':name,'cv_mae':float(-search.best_score_),
    'validation':score(y_val,search.predict(X_val)), 'params':search.best_params_, 'model':search.best_estimator_})
w=min(results,key=lambda r:r['validation']['mae'])
final=score(y_test,w['model'].predict(X_test))
baseline=DummyRegressor(strategy='mean').fit(X_train,y_train)
baseline_final=score(y_test,baseline.predict(X_test))
report={'dataset':'sklearn load_diabetes built-in real patient dataset (442 rows)',
 'source':'https://scikit-learn.org/stable/datasets/toy_dataset.html#diabetes-dataset',
 'task':'regression of quantitative disease progression after one year; NOT HbA1c or event risk',
 'date_utc':datetime.now(timezone.utc).isoformat(),
 'train_n':len(X_train),'validation_n':len(X_val),'test_n':len(X_test),
 'selected':w['name'],'validation':[{'name':r['name'],'cv_mae':r['cv_mae'],'validation':r['validation'],'params':r['params']} for r in results],
 'test':final,'dummy_baseline_test':baseline_final,
 'limitations':['This is an independent pipeline sanity-check only, not the NHANES HbA1c experiment.',
 'The diabetes dataset has a quantitative outcome and ten different predictors.',
 'These scores cannot be used to claim PREVIA cardiovascular or HbA1c clinical performance.']}
(OUT/'scores.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
joblib.dump(w['model'],OUT/'offline_smoketest_model.joblib')
lines=['# PREVIA — benchmark réel hors connexion','',
  '**Attention :** dataset scikit-learn Diabetes, 442 dossiers, **régression de progression à un an**. Ce n’est **pas** NHANES, pas l’HbA1c ni un modèle clinique PREVIA.','',
  f'Partitions : {len(X_train)} entraînement, {len(X_val)} validation, {len(X_test)} test indépendant.','',
  '| Algorithme | MAE CV | MAE validation | R² validation |', '|---|---:|---:|---:|']
for r in results:
 lines.append(f'| {r["name"]} | {r["cv_mae"]:.2f} | {r["validation"]["mae"]:.2f} | {r["validation"]["r2"]:.3f} |')
lines += ['',f'**Modèle retenu :** {w["name"]}',
  f'**Test R² :** {final["r2"]:.3f}',f'**Test MAE :** {final["mae"]:.2f}',
  f'**Test RMSE :** {final["rmse"]:.2f}',
  f'**Baseline MAE :** {baseline_final["mae"]:.2f}',
  '', 'Ces scores établissent que le pipeline ML sait entraîner/évaluer sur données réelles. Ils ne valident aucun score de dépistage.']
(OUT/'RAPPORT_BENCHMARK.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'selected':w['name'],'test':final,'baseline_test':baseline_final,'validation':[(r['name'],round(r['validation']['mae'],2)) for r in results]},indent=2))
