"""Federated ensemble of gradient-boosted trees: each client trains on its own slice,
only the fitted models are shared; global prediction = mean of client probabilities."""
exec(open("train.py").read().split("# ---- 2.")[0])  # reuse identical data pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import f1_score, precision_score, recall_score

def hgb(seed=0):
    return HistGradientBoostingClassifier(max_iter=600, learning_rate=0.1, max_leaf_nodes=63,
                                          early_stopping=False, random_state=seed)
def m(y, p, t=0.5):
    q = (p > t).astype(int)
    return dict(precision=round(precision_score(y, q), 4), recall=round(recall_score(y, q), 4), f1=round(f1_score(y, q), 4))

Xv, yv = val[FEATURE_COLS].values, val["binary_label"].values
Xh, yh = holdout[FEATURE_COLS].values, holdout["binary_label"].values

client_models = [hgb(i).fit(c[FEATURE_COLS].values, c["binary_label"].values) for i, c in enumerate(clients)]
for i, cm in enumerate(client_models): print(f"client {i} alone, holdout:", m(yh, cm.predict_proba(Xh)[:, 1]))
pv = np.mean([cm.predict_proba(Xv)[:, 1] for cm in client_models], 0)
ph = np.mean([cm.predict_proba(Xh)[:, 1] for cm in client_models], 0)
best_t = max(np.linspace(0.1, 0.9, 81), key=lambda t: f1_score(yv, (pv > t).astype(int)))
print(f"federated ensemble, holdout @0.5 :", m(yh, ph))
print(f"federated ensemble, holdout @{best_t:.2f}:", m(yh, ph, best_t))
print("errors:", int(((ph > best_t).astype(int) != yh).sum()), "/", len(yh))

kt = pd.read_csv("test_public.csv")
pk = np.mean([cm.predict_proba(kt[FEATURE_COLS].values)[:, 1] for cm in client_models], 0)
pd.DataFrame({"Id": kt["Id"], "Expected": (pk > best_t).astype(int)}).to_csv("submission_trees.csv", index=False)
print("wrote submission_trees.csv")
