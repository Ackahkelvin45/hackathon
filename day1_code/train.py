"""Day 1: federated intrusion detection on NSL-KDD. Mirrors the starter notebook's
data pipeline exactly, swaps in a stronger local model, writes submission.csv."""
import copy, hashlib, os
import numpy as np, pandas as pd, torch, torch.nn as nn
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score

SEED = 42
np.random.seed(SEED); torch.manual_seed(SEED)

# ---- 1. data (identical to notebook) ----
BASE = "https://raw.githubusercontent.com/jmnwong/NSL-KDD-Dataset/master/"
COLS = ["duration","protocol_type","service","flag","src_bytes","dst_bytes","land","wrong_fragment","urgent","hot",
 "num_failed_logins","logged_in","num_compromised","root_shell","su_attempted","num_root","num_file_creations",
 "num_shells","num_access_files","num_outbound_cmds","is_host_login","is_guest_login","count","srv_count",
 "serror_rate","srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate","diff_srv_rate","srv_diff_host_rate",
 "dst_host_count","dst_host_srv_count","dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
 "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate","dst_host_rerror_rate",
 "dst_host_srv_rerror_rate","label","difficulty"]

os.makedirs("data", exist_ok=True)
def load(name):
    p = f"data/{name}.txt"
    if not os.path.exists(p):
        pd.read_csv(BASE + name.replace("+", "%2B") + ".txt", names=COLS).to_csv(p, index=False, header=False)
    return pd.read_csv(p, names=COLS)
train_raw, test_raw = load("KDDTrain+"), load("KDDTest+")

def clean(df):
    df = df.drop(columns=["difficulty"]).copy()
    df["binary_label"] = (df["label"] != "normal").astype(int)
    return df
train_df, test_df = clean(train_raw), clean(test_raw)
for c in ["protocol_type", "service", "flag"]:
    le = LabelEncoder().fit(pd.concat([train_df[c], test_df[c]]))
    train_df[c], test_df[c] = le.transform(train_df[c]), le.transform(test_df[c])
FEATURE_COLS = [c for c in train_df.columns if c not in ["label", "binary_label"]]
scaler = StandardScaler()
train_df[FEATURE_COLS] = scaler.fit_transform(train_df[FEATURE_COLS])
test_df[FEATURE_COLS] = scaler.transform(test_df[FEATURE_COLS])

N_CLIENTS, HOLDOUT_SIZE = 5, 15000
_perm = np.random.RandomState(SEED).permutation(len(train_df))
holdout = train_df.iloc[_perm[:HOLDOUT_SIZE]].reset_index(drop=True)   # local mirror of the Kaggle test set
pool = train_df.iloc[_perm[HOLDOUT_SIZE:]].reset_index(drop=True)
print("holdout fingerprint:", hashlib.md5(str(sorted(_perm[:HOLDOUT_SIZE].tolist())).encode()).hexdigest()[:12])

# carve a small validation slice from the pool for threshold tuning; clients get the rest
val = pool.iloc[:5000]; pool = pool.iloc[5000:].reset_index(drop=True)
idx = np.random.RandomState(SEED).permutation(len(pool))
clients = [pool.iloc[c].reset_index(drop=True) for c in np.array_split(idx, N_CLIENTS)]

def tensors(df):
    return (torch.tensor(df[FEATURE_COLS].values, dtype=torch.float32),
            torch.tensor(df["binary_label"].values, dtype=torch.float32))

# ---- 2. stronger local model ----
class MyModel(nn.Module):
    def __init__(self, n=len(FEATURE_COLS), h=128):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(n, h), nn.ReLU(), nn.Dropout(0.1),
                                 nn.Linear(h, h // 2), nn.ReLU(), nn.Dropout(0.1),
                                 nn.Linear(h // 2, 1))
    def forward(self, x): return self.net(x).squeeze(-1)

def local_train(model, X, y, epochs=3, lr=1e-3, batch_size=128):
    model = copy.deepcopy(model); model.train()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.BCEWithLogitsLoss()
    for _ in range(epochs):
        perm = torch.randperm(len(X))
        for i in range(0, len(X), batch_size):
            b = perm[i:i + batch_size]
            opt.zero_grad(); loss_fn(model(X[b]), y[b]).backward(); opt.step()
    return model

# ---- 3. FL harness (FedAvg, unchanged in spirit from notebook) ----
def flat(m): return torch.cat([p.data.view(-1) for p in m.parameters()])
def fedavg(models, sizes):
    w = torch.tensor(np.array(sizes, float) / sum(sizes), dtype=torch.float32)
    avg = (torch.stack([flat(m) for m in models]) * w[:, None]).sum(0)
    out = copy.deepcopy(models[0]); i = 0
    for p in out.parameters():
        n = p.numel(); p.data.copy_(avg[i:i + n].view(p.shape)); i += n
    return out

def probs(model, X):
    model.eval()
    with torch.no_grad(): return torch.sigmoid(model(X)).numpy()

def metrics(y, p, t=0.5):
    pred = (p > t).astype(int)
    return dict(precision=round(precision_score(y, pred), 4), recall=round(recall_score(y, pred), 4), f1=round(f1_score(y, pred), 4))

X_val, y_val = tensors(val); X_hold, y_hold = tensors(holdout)
client_t = [tensors(c) for c in clients]
g = MyModel()
for r in range(25):
    locals_ = [local_train(g, X, y) for X, y in client_t]
    g = fedavg(locals_, [len(X) for X, _ in client_t])
    print(f"round {r+1:>2}: val {metrics(y_val.numpy(), probs(g, X_val))}")

# ---- 4. threshold tuning on val, report on local holdout ----
pv = probs(g, X_val)
ts = np.linspace(0.1, 0.9, 81)
best_t = max(ts, key=lambda t: f1_score(y_val.numpy(), (pv > t).astype(int)))
print(f"best threshold {best_t:.2f}")
print("local holdout @0.5 :", metrics(y_hold.numpy(), probs(g, X_hold)))
print("local holdout @best:", metrics(y_hold.numpy(), probs(g, X_hold), best_t))
print("KDDTest+ @best     :", metrics(*[test_df["binary_label"].values, probs(g, tensors(test_df)[0])], best_t))

# ---- 5. submission ----
kt = pd.read_csv("test_public.csv")
pred = (probs(g, torch.tensor(kt[FEATURE_COLS].values, dtype=torch.float32)) > best_t).astype(int)
pd.DataFrame({"Id": kt["Id"], "Expected": pred}).to_csv("submission.csv", index=False)
torch.save(g.state_dict(), "model.pt")
print(f"wrote submission.csv ({len(pred)} rows, {pred.mean():.3f} attack rate)")
