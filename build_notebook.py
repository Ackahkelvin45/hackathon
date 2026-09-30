"""Fills the 'YOUR TURN' hooks of the Day 2 starter notebook with our solution. Then run:
python -m nbconvert --to notebook --execute --inplace 02_Intermediate_Advanced_Day2.ipynb"""
import json
nb = json.load(open("kaggle/02_Intermediate_Advanced_Day2.ipynb"))
def code(src): return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}
def md(src): return {"cell_type": "markdown", "metadata": {}, "source": src}

INT = r'''
# 🔧 OUR TURN — intermediate track: server momentum (FedAvgM)
def _deltas(local_models, prev):
    ref = get_flat_params(prev)
    return ref, torch.stack([get_flat_params(m) - ref for m in local_models])

def _from_flat(template, flat):
    out = copy.deepcopy(template); set_flat_params(out, flat); return out

def make_fedavgm(beta=0.9, equal=False):
    """Treat the averaged client delta as a pseudo-gradient and apply momentum on the server.
    Skewed clients make the global model zig-zag round to round; momentum keeps the component
    that is consistent across rounds and damps the part that flips."""
    state = {"v": None}
    def agg(local_models, sizes, prev):
        ref, d = _deltas(local_models, prev)
        w = np.ones(len(sizes)) if equal else np.array(sizes, dtype=float)
        w = torch.tensor(w / w.sum(), dtype=torch.float32)
        g = (d * w.unsqueeze(1)).sum(0)
        state["v"] = g if state["v"] is None else beta * state["v"] + g
        return _from_flat(prev, ref + state["v"])
    return agg

def make_balance_weighted(client_dfs, k=3.0):
    """The notebook's first suggestion: down-weight clients whose label mix is far from global."""
    p = np.array([c["binary_label"].mean() for c in client_dfs]); n = np.array([len(c) for c in client_dfs], dtype=float)
    w = n * np.exp(-k * np.abs(p - (p * n).sum() / n.sum()))
    return lambda local_models, sizes, prev: fedavg(local_models, w)

my_agg_fn = make_fedavgm(beta=0.9)
custom_model, custom_history = run_fl(noniid_clients, rounds=8, aggregation="custom", agg_fn=my_agg_fn)

# other things we tried (reported honestly in the Writeup)
_, eq_history  = run_fl(noniid_clients, rounds=8, aggregation="custom", agg_fn=make_fedavgm(0.7, equal=True), verbose=False)
_, bal_history = run_fl(noniid_clients, rounds=8, aggregation="custom", agg_fn=make_balance_weighted(noniid_clients), verbose=False)
_, med_noniid_history = run_fl(noniid_clients, rounds=8, aggregation="median", verbose=False)

print("\nIID reference F1:                 ", baseline_history[-1]["f1"])
print("Naive non-IID F1 (BEFORE):        ", noniid_history[-1]["f1"])
print("FedAvgM beta=0.9 F1 (AFTER, ours):", custom_history[-1]["f1"], f"  (+{custom_history[-1]['f1'] - noniid_history[-1]['f1']:.4f})")
print("FedAvgM 0.7 + equal weights:      ", eq_history[-1]["f1"])
print("Label-balance weighting:          ", bal_history[-1]["f1"], "  (did not help)")
print("Coordinate median (provided):     ", med_noniid_history[-1]["f1"])
'''

ADV = r'''
# 🔧 OUR TURN — advanced track: flag + drop + clip, with a detection log
DETECTION_LOG = []   # one row per round: which clients were flagged, and every client's update norm

def make_robust(norm_mult=3.0, log=None):
    """1) FLAG a client if its update norm is > norm_mult x the median norm (catches scaling),
          or its cosine similarity to the coordinate-median update is negative (catches label flipping).
       2) DROP flagged clients this round.
       3) CLIP survivors to the median norm (bounds anything that slipped through).
       4) Size-weighted average of the rest."""
    state = {"r": 0}
    def agg(local_models, sizes, prev):
        state["r"] += 1
        ref, d = _deltas(local_models, prev)
        norms = d.norm(dim=1); med_norm = norms.median()
        med_dir = d.median(dim=0).values
        cos = torch.nn.functional.cosine_similarity(d, med_dir.unsqueeze(0), dim=1)
        bad = (norms > norm_mult * med_norm) | (cos < 0)
        if bad.all(): bad[:] = False
        if log is not None:
            log.append({"round": state["r"], "flagged": [i for i, b in enumerate(bad.tolist()) if b],
                        "norms": [round(x, 2) for x in norms.tolist()], "cosine": [round(x, 2) for x in cos.tolist()]})
        d = d * torch.clamp(med_norm / (norms + 1e-12), max=1.0).unsqueeze(1)
        w = torch.tensor(np.array(sizes, dtype=float), dtype=torch.float32) * (~bad).float()
        return _from_flat(prev, ref + (d * (w / w.sum()).unsqueeze(1)).sum(0))
    return agg

my_defense_fn = make_robust(log=DETECTION_LOG)
my_defense_model, my_defense_history = run_fl(
    noniid_clients, rounds=8,
    malicious_clients=[1], attack="scale", scale_factor=15.0,
    aggregation="custom", agg_fn=my_defense_fn,
)
print("\nNaive under attack (BEFORE):", attacked_history[-1]["f1"])
print("Median defense (provided):  ", defended_history[-1]["f1"])
print("Our defense (AFTER):        ", my_defense_history[-1]["f1"], f"  (recovered +{my_defense_history[-1]['f1'] - attacked_history[-1]['f1']:.4f})")
print("\nDetection log — the true attacker is client 1:")
for row in DETECTION_LOG: print("  ", row)
'''

STRESS = r'''
# Stress tests: stronger scaling, two attackers, and an attacker that does NOT scale (label flip only)
scenarios = {
    "1 attacker, scale 15": dict(malicious_clients=[1], attack="scale", scale_factor=15.0),
    "1 attacker, scale 50": dict(malicious_clients=[1], attack="scale", scale_factor=50.0),
    "2 attackers [1,3], scale 15": dict(malicious_clients=[1, 3], attack="scale", scale_factor=15.0),
    "1 attacker, label flip only": dict(malicious_clients=[1], attack="label_flip"),
}
print(f"{'scenario':<30}{'naive FedAvg':>14}{'median':>10}{'ours':>10}   flagged per round (ours)")
for name, kw in scenarios.items():
    log = []
    f_naive = run_fl(noniid_clients, rounds=8, verbose=False, **kw)[1][-1]["f1"]
    f_med   = run_fl(noniid_clients, rounds=8, verbose=False, aggregation="median", **kw)[1][-1]["f1"]
    f_ours  = run_fl(noniid_clients, rounds=8, verbose=False, aggregation="custom", agg_fn=make_robust(log=log), **kw)[1][-1]["f1"]
    print(f"{name:<30}{f_naive:>14}{f_med:>10}{f_ours:>10}   {[r['flagged'] for r in log]}")
'''

CHART = r'''
# Cover image: F1 by round, before vs after, both tracks
import matplotlib.pyplot as plt
INK, MUTED, SURF = "#0b0b0b", "#898781", "#fcfcfb"
C = {"Naive FedAvg": "#2a78d6", "Coordinate median": "#eb6834", "Ours": "#1baf7a"}
f1s = lambda h: [x["f1"] for x in h]
panels = [
    ("Advanced: one malicious bank (label flip + 15x scaling)",
     {"Naive FedAvg": f1s(attacked_history), "Coordinate median": f1s(defended_history), "Ours": f1s(my_defense_history)}),
    ("Intermediate: skewed (non-IID) banks, no attacker",
     {"Naive FedAvg": f1s(noniid_history), "Coordinate median": f1s(med_noniid_history), "Ours": f1s(custom_history)}),
]
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True, facecolor=SURF)
for ax, (title, series) in zip(axes, panels):
    ax.set_facecolor(SURF)
    ends = sorted(((v[-1], k) for k, v in series.items()))
    for k, v in series.items():
        ax.plot(range(1, 9), v, color=C[k], lw=2, marker="o", ms=5, label=k, zorder=3)
    last_y = -1
    for y, k in ends:  # direct labels at line ends, nudged apart so they never collide
        ly = max(y, last_y + 0.045); last_y = ly
        ax.annotate(f"{k}  {y:.2f}", (8, y), xytext=(8.25, ly), color=INK, fontsize=10, va="center",
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6) if abs(ly - y) > 0.01 else None)
    ax.set_title(title, color=INK, fontsize=12, loc="left", pad=12)
    ax.set_xlabel("Federated round", color=MUTED); ax.set_xlim(0.7, 11.2); ax.set_xticks(range(1, 9)); ax.set_ylim(-0.02, 0.9)
    ax.grid(axis="y", color="#e6e5e0", lw=0.8); ax.tick_params(colors=MUTED, length=0)
    for s in ax.spines.values(): s.set_visible(False)
axes[0].set_ylabel("F1 on NSL-KDD test set", color=MUTED)
axes[0].legend(frameon=False, loc="lower center", ncol=3, fontsize=10, labelcolor=INK)
fig.suptitle("Flag, drop, clip: robust aggregation for federated intrusion detection", color=INK, fontsize=15, x=0.06, ha="left", weight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig("cover.png", dpi=150, facecolor=SURF); plt.show()
'''

out = []
for c in nb["cells"]:
    s = "".join(c["source"])
    c = dict(c, source=s)
    if c["cell_type"] == "code": c["outputs"] = []; c["execution_count"] = None
    if "!pip -q install" in s:
        c["source"] = s.replace("!pip -q install torch scikit-learn pandas numpy --upgrade 2>/dev/null", "# (pip upgrade removed: pinned preinstalled versions keep the numbers reproducible)")
    if "TRAIN_URL =" in s:
        c["source"] = s.replace('train_raw = pd.read_csv(TRAIN_URL, names=COLS)\ntest_raw  = pd.read_csv(TEST_URL, names=COLS)',
            '# use the repo\'s local copy if present (identical files), else download\nif os.path.exists("data/KDDTrain+.txt"): TRAIN_URL, TEST_URL = "data/KDDTrain+.txt", "data/KDDTest+.txt"\ntrain_raw = pd.read_csv(TRAIN_URL, names=COLS)\ntest_raw  = pd.read_csv(TEST_URL, names=COLS)')
        assert c["source"] != s
    if "def run_fl(" in s:
        c["source"] = s.replace("    malicious_clients = malicious_clients or []\n    global_model = model_fn()",
            "    torch.manual_seed(SEED)  # OUR ONE HARNESS CHANGE: every run starts from the same init and batch order,\n                             # so before/after differences come from aggregation alone\n    malicious_clients = malicious_clients or []\n    global_model = model_fn()")
        assert c["source"] != s
    if "YOUR TURN — intermediate" in s: c["source"] = INT.strip()
    if "YOUR TURN — advanced" in s:
        out.append(code(ADV.strip())); out.append(md("### Stress tests")); out.append(code(STRESS.strip()))
        out.append(md("### Cover chart")); c = code(CHART.strip())
    if 'TEAM_NAME = "CHANGE_ME"' in s:
        c["source"] = s.replace('"CHANGE_ME"', '"ZeroTrustAI"').replace('TRACK = "intermediate"', 'TRACK = "advanced"').replace("FINAL_MODEL = custom_model", "FINAL_MODEL = my_defense_model")
    out.append(c)
nb["cells"] = out
json.dump(nb, open("02_Intermediate_Advanced_Day2.ipynb", "w"), indent=1)
print("cells:", len(out))
