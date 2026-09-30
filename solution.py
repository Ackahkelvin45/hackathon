"""Day 2/3 solution: both tracks. Run: ../secure-ai-competition/.venv/bin/python solution.py"""
import pandas as pd, numpy as np, torch, torch.nn as nn, copy, json, sys
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score

SEED = 42
np.random.seed(SEED); torch.manual_seed(SEED)
COLS = ["duration","protocol_type","service","flag","src_bytes","dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins","logged_in","num_compromised","root_shell","su_attempted","num_root","num_file_creations","num_shells","num_access_files","num_outbound_cmds","is_host_login","is_guest_login","count","srv_count","serror_rate","srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate","diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count","dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate","dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate","dst_host_rerror_rate","dst_host_srv_rerror_rate","label","difficulty"]
train_raw = pd.read_csv("data/KDDTrain+.txt", names=COLS)
test_raw = pd.read_csv("data/KDDTest+.txt", names=COLS)
def clean(df):
    df = df.drop(columns=["difficulty"]).copy()
    df["binary_label"] = (df["label"] != "normal").astype(int)
    return df
train_df, test_df = clean(train_raw), clean(test_raw)
for c in ["protocol_type", "service", "flag"]:
    le = LabelEncoder(); le.fit(pd.concat([train_df[c], test_df[c]]))
    train_df[c] = le.transform(train_df[c]); test_df[c] = le.transform(test_df[c])
FEATURE_COLS = [c for c in train_df.columns if c not in ["label", "binary_label"]]
scaler = StandardScaler()
train_df[FEATURE_COLS] = scaler.fit_transform(train_df[FEATURE_COLS])
test_df[FEATURE_COLS] = scaler.transform(test_df[FEATURE_COLS])

N_CLIENTS, HOLDOUT_SIZE = 5, 15000
_rng = np.random.RandomState(SEED); _perm = _rng.permutation(len(train_df))
train_pool = train_df.iloc[_perm[HOLDOUT_SIZE:]].reset_index(drop=True)
def make_iid_partition(df, n_clients=N_CLIENTS, seed=SEED):
    rng = np.random.RandomState(seed); idx = rng.permutation(len(df))
    return [df.iloc[c].reset_index(drop=True) for c in np.array_split(idx, n_clients)]
FAMILY_MAP = {"normal":"normal","neptune":"dos","back":"dos","land":"dos","pod":"dos","smurf":"dos","teardrop":"dos","apache2":"dos","udpstorm":"dos","processtable":"dos","worm":"dos","mailbomb":"dos","satan":"probe","ipsweep":"probe","nmap":"probe","portsweep":"probe","mscan":"probe","saint":"probe"}
def make_noniid_partition(df, n_clients=N_CLIENTS, alpha=0.3, seed=SEED):
    rng = np.random.RandomState(seed); df = df.copy()
    df["family"] = df["label"].map(lambda x: FAMILY_MAP.get(x, "r2l_u2r_other"))
    client_indices = [[] for _ in range(n_clients)]
    for fam in df["family"].unique():
        fam_idx = df.index[df["family"] == fam].to_numpy().copy(); rng.shuffle(fam_idx)
        proportions = rng.dirichlet(alpha=[alpha] * n_clients)
        split_points = (np.cumsum(proportions) * len(fam_idx)).astype(int)[:-1]
        for i, s in enumerate(np.split(fam_idx, split_points)): client_indices[i].extend(s.tolist())
    out = []
    for ci in client_indices:
        rng.shuffle(ci); out.append(df.loc[ci].drop(columns=["family"]).reset_index(drop=True))
    return out
iid_clients = make_iid_partition(train_pool); noniid_clients = make_noniid_partition(train_pool)
N_FEATURES = len(FEATURE_COLS)

class WeakMLP(nn.Module):
    def __init__(self, n_features=N_FEATURES, hidden=8):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(n_features, hidden), nn.ReLU(), nn.Linear(hidden, 1))
    def forward(self, x): return self.net(x).squeeze(-1)

X_test = torch.tensor(test_df[FEATURE_COLS].values, dtype=torch.float32)
y_test = torch.tensor(test_df["binary_label"].values, dtype=torch.float32)
def df_to_tensors(df):
    return torch.tensor(df[FEATURE_COLS].values, dtype=torch.float32), torch.tensor(df["binary_label"].values, dtype=torch.float32)
def local_train(model, X, y, epochs=1, lr=0.05, batch_size=256):
    model = copy.deepcopy(model); opt = torch.optim.SGD(model.parameters(), lr=lr); loss_fn = nn.BCEWithLogitsLoss(); n = len(X)
    for _ in range(epochs):
        perm = torch.randperm(n)
        for i in range(0, n, batch_size):
            idx = perm[i:i + batch_size]; opt.zero_grad(); loss_fn(model(X[idx]), y[idx]).backward(); opt.step()
    return model
def get_flat_params(model): return torch.cat([p.data.view(-1) for p in model.parameters()])
def set_flat_params(model, flat):
    i = 0
    for p in model.parameters():
        n = p.numel(); p.data.copy_(flat[i:i + n].view(p.shape)); i += n
def _from_flat(template, flat):
    out = copy.deepcopy(template); set_flat_params(out, flat); return out
def fedavg(models, weights):
    w = torch.tensor(np.array(weights, dtype=float) / np.sum(weights), dtype=torch.float32)
    return _from_flat(models[0], (torch.stack([get_flat_params(m) for m in models]) * w.unsqueeze(1)).sum(0))
def coordinate_median(models):
    return _from_flat(models[0], torch.stack([get_flat_params(m) for m in models]).median(dim=0).values)
def evaluate(model):
    model.eval()
    with torch.no_grad(): preds = (torch.sigmoid(model(X_test)) > 0.5).float()
    return {"precision": round(precision_score(y_test, preds, zero_division=0), 4), "recall": round(recall_score(y_test, preds, zero_division=0), 4), "f1": round(f1_score(y_test, preds, zero_division=0), 4)}
def run_fl(client_dfs, model_fn=lambda: WeakMLP(), rounds=8, epochs=1, aggregation="fedavg", agg_fn=None, malicious_clients=None, attack="scale", scale_factor=15.0, verbose=False):
    torch.manual_seed(SEED)  # same init + same batch order for every method -> fair before/after
    malicious_clients = malicious_clients or []; global_model = model_fn()
    client_tensors = [df_to_tensors(df) for df in client_dfs]; history = []
    for r in range(rounds):
        local_models, sizes = [], []; global_flat = get_flat_params(global_model)
        for cid, (X, y) in enumerate(client_tensors):
            is_mal = cid in malicious_clients
            if is_mal: y = 1 - y
            lm = local_train(global_model, X, y, epochs=epochs)
            if is_mal and attack == "scale":
                set_flat_params(lm, global_flat + scale_factor * (get_flat_params(lm) - global_flat))
            local_models.append(lm); sizes.append(len(X))
        prev = global_model
        if aggregation == "fedavg": global_model = fedavg(local_models, sizes)
        elif aggregation == "median": global_model = coordinate_median(local_models)
        else: global_model = agg_fn(local_models, sizes, prev)
        history.append(evaluate(global_model))
        if verbose: print(f"round {r+1:>2}: {history[-1]}")
    return global_model, history

# ---------------- OUR AGGREGATORS ----------------
def _deltas(local_models, prev):
    ref = get_flat_params(prev)
    return ref, torch.stack([get_flat_params(m) - ref for m in local_models])

def make_fedavgm(beta=0.7, server_lr=1.0, equal=False):
    """Intermediate: server momentum (FedAvgM). Smooths the round-to-round zig-zag that skewed clients cause."""
    state = {"v": None}
    def agg(local_models, sizes, prev):
        ref, d = _deltas(local_models, prev)
        w = np.ones(len(sizes)) if equal else np.array(sizes, dtype=float)
        w = torch.tensor(w / w.sum(), dtype=torch.float32)
        g = (d * w.unsqueeze(1)).sum(0)
        state["v"] = g if state["v"] is None else beta * state["v"] + g
        return _from_flat(prev, ref + server_lr * state["v"])
    return agg

def make_balance_weighted(client_dfs, k=3.0):
    """Intermediate: down-weight clients whose label mix is far from the consortium-wide mix."""
    p = np.array([c["binary_label"].mean() for c in client_dfs]); n = np.array([len(c) for c in client_dfs], dtype=float)
    pg = (p * n).sum() / n.sum()
    w = n * np.exp(-k * np.abs(p - pg))
    def agg(local_models, sizes, prev): return fedavg(local_models, w)
    return agg

FLAGS = []  # (round, flagged client ids) -- detection log
def make_robust(norm_mult=3.0, log=True):
    """Advanced: detect + resist. 1) flag updates whose L2 norm is > norm_mult x the median norm
    or that point against the coordinate-median direction (cosine < 0); 2) drop them;
    3) clip survivors to the median norm; 4) size-weighted average."""
    state = {"r": 0}
    def agg(local_models, sizes, prev):
        state["r"] += 1
        ref, d = _deltas(local_models, prev)
        norms = d.norm(dim=1); med_norm = norms.median()
        med_dir = d.median(dim=0).values
        cos = torch.nn.functional.cosine_similarity(d, med_dir.unsqueeze(0), dim=1)
        bad = (norms > norm_mult * med_norm) | (cos < 0)
        if bad.all(): bad[:] = False
        if log: FLAGS.append((state["r"], [i for i, b in enumerate(bad.tolist()) if b], [round(x, 2) for x in norms.tolist()]))
        keep = ~bad
        d = d * torch.clamp(med_norm / (norms + 1e-12), max=1.0).unsqueeze(1)
        w = torch.tensor(np.array(sizes, dtype=float), dtype=torch.float32) * keep.float(); w = w / w.sum()
        return _from_flat(prev, ref + (d * w.unsqueeze(1)).sum(0))
    return agg

if __name__ == "__main__":
    R = {}
    def go(name, *a, **k):
        m, h = run_fl(*a, **k); R[name] = {"final": h[-1], "f1_by_round": [x["f1"] for x in h]}; print(f"{name:<45} F1={h[-1]['f1']}  {[x['f1'] for x in h]}", flush=True); return m
    go("iid_fedavg_reference", iid_clients)
    go("INT naive fedavg (noniid)", noniid_clients)
    cands = {
        "INT median": dict(aggregation="median"),
        "INT fedavgm b0.5": dict(aggregation="custom", agg_fn=make_fedavgm(0.5)),
        "INT fedavgm b0.7": dict(aggregation="custom", agg_fn=make_fedavgm(0.7)),
        "INT fedavgm b0.9": dict(aggregation="custom", agg_fn=make_fedavgm(0.9)),
        "INT fedavgm b0.7 equal": dict(aggregation="custom", agg_fn=make_fedavgm(0.7, equal=True)),
        "INT balance-weighted k3": dict(aggregation="custom", agg_fn=make_balance_weighted(noniid_clients, 3.0)),
        "INT robust(clip)": dict(aggregation="custom", agg_fn=make_robust(log=False)),
    }
    models = {n: go(n, noniid_clients, **k) for n, k in cands.items()}
    ATT = dict(malicious_clients=[1], attack="scale", scale_factor=15.0)
    go("ADV naive fedavg under attack", noniid_clients, **ATT)
    go("ADV median baseline defense", noniid_clients, aggregation="median", **ATT)
    adv_model = go("ADV our robust defense", noniid_clients, aggregation="custom", agg_fn=make_robust(), **ATT)
    print("detection log (round, flagged, norms):"); [print("  ", f) for f in FLAGS]
    flags15 = list(FLAGS); FLAGS.clear()
    HARD = dict(malicious_clients=[1], attack="scale", scale_factor=50.0)
    go("ADV50 naive fedavg", noniid_clients, **HARD)
    go("ADV50 median", noniid_clients, aggregation="median", **HARD)
    go("ADV50 our robust defense", noniid_clients, aggregation="custom", agg_fn=make_robust(log=False), **HARD)
    best_int = max(cands, key=lambda n: R[n]["final"]["f1"])
    R["_best_intermediate"] = best_int; R["_detection_log_scale15"] = flags15
    json.dump(R, open("results.json", "w"), indent=1)
    torch.save({"int": models[best_int].state_dict(), "adv": adv_model.state_dict()}, "models_state.pt")
    # export primary = advanced
    adv_model.eval(); torch.jit.script(adv_model).save("model_scripted.pt")
    json.dump({"team_name": "CHANGE_ME", "track": "advanced", "self_reported_metrics": evaluate(adv_model), "model_file": "model_scripted.pt", "n_input_features": N_FEATURES}, open("submission.json", "w"), indent=2)
    print("best intermediate:", best_int, R[best_int]["final"]); print(open("submission.json").read())
