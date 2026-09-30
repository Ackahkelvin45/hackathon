# About the Dataset

This hackathon uses **NSL-KDD**, a widely-used, well-documented network intrusion detection dataset. It is an improved version of the original KDD Cup 1999 dataset with duplicate records removed, which makes it fairer and harder to game than the original. Each row is a single network connection record; the task is to tell normal traffic from an attack.

NSL-KDD was picked deliberately: it's small enough to train on CPU in seconds, and tabular enough that feature engineering matters more than architecture.

## Files Provided

| File | What it is |
|------|------------|
| `01_Beginner_Track_Day1.ipynb` | The starter notebook. Downloads, cleans, and partitions the data for you. Start here. |
| `test_public.csv` | Unlabeled features for the held-out evaluation set. This is what your final model should predict on. |
| `sample_submission.csv` | The exact format your predictions should follow. |

You won't need to download or clean NSL-KDD yourself. The starter notebook does this automatically from a public source and builds your 5 client partitions inside your own notebook session, with a fixed random seed so everyone starts from the identical baseline.

- Files: 3
- Size: 12.63 MB
- Type: csv, ipynb
- Columns: 44
- License: MIT

## Data Dictionary

Every row is one network connection, described by 41 features plus a label. Categorical features are label-encoded and all features are standardized (zero mean, unit variance) before you see them. You're working with model-ready numeric data from the start.

### Basic connection features
Properties of the raw TCP/IP connection itself:
`duration`, `protocol_type`, `service`, `flag`, `src_bytes`, `dst_bytes`, `land`, `wrong_fragment`, `urgent`

### Content features
Derived from inspecting the connection's payload for suspicious behavior:
`hot`, `num_failed_logins`, `logged_in`, `num_compromised`, `root_shell`, `su_attempted`, `num_root`, `num_file_creations`, `num_shells`, `num_access_files`, `num_outbound_cmds`, `is_host_login`, `is_guest_login`

### Traffic features
Computed over a 2-second window of recent connections to the same host/service (useful for spotting scans and floods):
`count`, `srv_count`, `serror_rate`, `srv_serror_rate`, `rerror_rate`, `srv_rerror_rate`, `same_srv_rate`, `diff_srv_rate`, `srv_diff_host_rate`

### Host-based traffic features
The same idea, computed over the last 100 connections to the same destination host (catches slower, low-and-slow attacks that a 2-second window would miss):
`dst_host_count`, `dst_host_srv_count`, `dst_host_same_srv_rate`, `dst_host_diff_srv_rate`, `dst_host_same_src_port_rate`, `dst_host_srv_diff_host_rate`, `dst_host_serror_rate`, `dst_host_srv_serror_rate`, `dst_host_rerror_rate`, `dst_host_srv_rerror_rate`

### Label
`Expected`: **0 = normal traffic, 1 = attack**. Originally over 20 distinct attack types (normal, DoS, probe, and rare R2L/U2R attacks), collapsed to binary here so the leaderboard rewards catching any intrusion, not memorizing attack names. Roughly balanced overall (~53% normal / ~47% attack). Your 5 client partitions are each an even, representative slice of this same balance.

## A note on the held-out evaluation set

Your final score is computed against a separate slice of data that was set aside before your client partitions were created. No client, and no team, ever trains on it. This is what makes the leaderboard score meaningful rather than just a measure of how well you memorized your own training data.

## How the starter notebook works

Summary of `01_Beginner_Track_Day1.ipynb`, section by section:

1. **Setup**: installs torch / scikit-learn / pandas / numpy, sets `SEED = 42`.
2. **Load and clean**: downloads `KDDTrain+` and `KDDTest+` from a public GitHub mirror, drops `difficulty`, adds `binary_label = (label != "normal")`. Label-encodes `protocol_type`, `service`, `flag` (fit on train + test). Standardizes all 41 features with `StandardScaler` (fit on train).
3. **Holdout and partition**: reserves `HOLDOUT_SIZE = 15000` rows from the train set as the secret Kaggle test slice (seed-locked, prints an MD5 fingerprint that must match the organizers'). The remaining rows are split evenly and IID across `N_CLIENTS = 5`.
4. **Weak baseline model**: `WeakMLP`, a single 8-unit hidden layer MLP.
5. **FL harness**: `local_train` (SGD, lr 0.05, batch 256, BCEWithLogitsLoss), `fedavg` (size-weighted average of flattened params), `evaluate` (precision / recall / F1 at threshold 0.5 on `KDDTest+`), `run_fl` (rounds of local training then FedAvg).
6. **Baseline run**: 6 rounds, expected F1 ≈ 0.75–0.78. This is the number to beat.
7. **🔧 YOUR TURN**: define a new `model_fn` and/or modified `local_train`, then re-run `run_fl`. Suggested directions, in order of effort:
   - Class imbalance: `pos_weight` in `BCEWithLogitsLoss`, per-client oversampling, or tuning the decision threshold instead of 0.5.
   - Feature engineering: drop near-constant features, add ratios / interactions.
   - Better model: more hidden units, extra layers, dropout, or a different architecture wrapped to match the interface.
8. **Submission**: loads `test_public.csv`, predicts with `FINAL_MODEL` at threshold 0.5, writes `submission.csv` with columns `Id`, `Expected`. Upload that file to the Beginner Track Leaderboard.
