exec(open("train.py").read().split("# ---- 2.")[0].replace("val = pool.iloc[:5000]; pool = pool.iloc[5000:]", "val = pool.iloc[:2000]; pool = pool.iloc[2000:]"))
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import f1_score
Xv, yv = val[FEATURE_COLS].values, val["binary_label"].values
Xh, yh = holdout[FEATURE_COLS].values, holdout["binary_label"].values
kt = pd.read_csv("test_public.csv"); Xk = kt[FEATURE_COLS].values

# are holdout rows with identical features but conflicting labels in the pool? (irreducible noise)
pool_map = {}
for t, y in zip(map(tuple, pool[FEATURE_COLS].round(5).values), pool["binary_label"].values):
    pool_map.setdefault(t, set()).add(y)
conf = sum(1 for t, y in zip(map(tuple, holdout[FEATURE_COLS].round(5).values), yh) if t in pool_map and y not in pool_map[t])
print("holdout rows whose exact feature twin in pool has the opposite label:", conf)

best = None
for name, kw in [("A", dict(max_iter=600, learning_rate=0.1, max_leaf_nodes=63)),
                 ("B", dict(max_iter=1500, learning_rate=0.05, max_leaf_nodes=63)),
                 ("C", dict(max_iter=1000, learning_rate=0.1, max_leaf_nodes=127, l2_regularization=0.1))]:
    ms = [HistGradientBoostingClassifier(early_stopping=False, random_state=s * 10 + i, **kw)
              .fit(c[FEATURE_COLS].values, c["binary_label"].values) for i, c in enumerate(clients) for s in range(3)]
    pv = np.mean([x.predict_proba(Xv)[:, 1] for x in ms], 0)
    ph = np.mean([x.predict_proba(Xh)[:, 1] for x in ms], 0)
    t = max(np.linspace(0.1, 0.9, 81), key=lambda t: f1_score(yv, (pv > t).astype(int)))
    err = int(((ph > t) != yh).sum()); f1 = f1_score(yh, (ph > t).astype(int))
    print(f"{name}: holdout f1={f1:.4f} errors={err} t={t:.2f}", flush=True)
    pk = np.mean([x.predict_proba(Xk)[:, 1] for x in ms], 0)
    pd.DataFrame({"Id": kt["Id"], "Expected": (pk > t).astype(int)}).to_csv(f"sub_{name}.csv", index=False)
    if best is None or err < best[1]: best = (name, err)
print("best:", best)
