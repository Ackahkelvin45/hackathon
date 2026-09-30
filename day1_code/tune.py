import sys; sys.argv = ["x"]
exec(open("train.py").read().split("# ---- 4.")[0].replace("for r in range(25):", "for r in range(0):"))  # reuse data + funcs, skip training
from sklearn.metrics import f1_score
def run(h, epochs, rounds, seed):
    torch.manual_seed(seed)
    g = MyModel(h=h)
    for _ in range(rounds):
        ls = [local_train(g, X, y, epochs=epochs) for X, y in client_t]
        g = fedavg(ls, [len(X) for X, _ in client_t])
    return g
models = [run(256, 5, 40, s) for s in (0, 1, 2)]
pv = np.mean([probs(m, X_val) for m in models], 0)
ph = np.mean([probs(m, X_hold) for m in models], 0)
ts = np.linspace(0.1, 0.9, 81)
best_t = max(ts, key=lambda t: f1_score(y_val.numpy(), (pv > t).astype(int)))
for i, m in enumerate(models): print(f"seed {i} holdout:", metrics(y_hold.numpy(), probs(m, X_hold), best_t))
print(f"ensemble holdout @{best_t:.2f}:", metrics(y_hold.numpy(), ph, best_t))
kt = pd.read_csv("test_public.csv")
Xk = torch.tensor(kt[FEATURE_COLS].values, dtype=torch.float32)
pred = (np.mean([probs(m, Xk) for m in models], 0) > best_t).astype(int)
pd.DataFrame({"Id": kt["Id"], "Expected": pred}).to_csv("submission_ensemble.csv", index=False)
for i, m in enumerate(models): torch.save(m.state_dict(), f"model_seed{i}.pt")
print("wrote submission_ensemble.csv")
