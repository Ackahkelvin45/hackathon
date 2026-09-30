# Flag, Drop, Clip: a robust aggregator for poisoned federated intrusion detection
**Subtitle:** Norm-and-direction anomaly detection that names the malicious bank and recovers F1 from 0.05 to 0.70
**Tracks:** Advanced (primary), Intermediate (supporting)
**Project link:** https://github.com/Ackahkelvin45/hackathon

## Headline result (Advanced, primary)
Same non-IID split, same WeakMLP, same 8 rounds, same seed, client 1 malicious (label flip + 15x scaled update). Test set: NSL-KDD KDDTest+.

| Aggregation under attack | F1 |
|---|---|
| Naive FedAvg (before) | **0.0511** |
| Coordinate median (provided baseline) | 0.6855 |
| Ours: flag + drop + clip (after) | **0.6968** |

**F1 recovered: +0.6457.**

Stress tests (final-round F1):

| Scenario | Naive FedAvg | Median | Ours |
|---|---|---|---|
| 1 attacker, scale 50 | 0.6215 (swings 0.00 to 0.69 between rounds) | 0.6861 | 0.6968 |
| 2 attackers, scale 15 | 0.0017 | 0.7083 | 0.7132 |
| 1 attacker, label flip only (no scaling) | 0.6850 | 0.6773 | 0.6926 |

## What we did
Each round, for every client we compute its update delta = local weights - previous global weights, then:
1. **Flag** a client if its delta's L2 norm is more than 3x the median norm, or if its cosine similarity to the coordinate-median delta is negative (it pushes against the consensus direction).
2. **Drop** flagged clients from the round.
3. **Clip** the survivors to the median norm.
4. Size-weighted average of what is left.

## Why it works
The attack has two signatures. Scaling by 15 makes the update's norm huge: honest norms were 0.2 to 1.7, the attacker's were 10 to 27. Label flipping makes its direction oppose the honest majority. Norm catches the first, cosine catches the second, so an attacker who stops scaling to hide is still caught by direction. The median is used as the reference because one outlier out of five cannot move it. Clipping bounds the damage of anything that slips through.

## Detection
Client 1 was flagged in **8 of 8 rounds**. Honest caveat: client 0 was also flagged in rounds 1 and 2 (false positives). Under non-IID data an honest but unusual bank can look adversarial early, before the global model settles. It was readmitted from round 3. With two attackers, both were flagged in all 8 rounds, but honest client 4 was also dropped in 6 rounds. With a non-scaling attacker, round 1 missed it (and wrongly flagged client 0); rounds 2 to 8 caught it by direction alone.

## Intermediate (supporting)
Non-IID split, no attacker. Naive FedAvg: **0.7117** (IID reference 0.7641).

| Aggregation | F1 |
|---|---|
| Naive FedAvg | 0.7117 |
| FedAvgM, server momentum 0.9 (ours) | 0.7387 (+0.0270) |
| FedAvgM 0.7, equal client weights (ours) | 0.7368 |
| Coordinate median (provided) | 0.7489 (+0.0372) |

Server momentum smooths the round-to-round zig-zag caused by skewed clients. Equal weights stop the largest skewed bank dominating.

## What did not work
- Weighting clients by closeness of label balance to the global balance: 0.7035, worse than naive. Label balance is too coarse; skew here is by attack family.
- Our robust aggregator on clean non-IID data: 0.7103, no gain. Dropping unusual honest clients costs information.
- The provided median beat our momentum method on Intermediate. We report that as is.

## Limitations
Variants were compared on the test set with one seed, so small gaps (0.01) are within noise; the Advanced gain (+0.65) is not. Recall is low (0.54) for every method: the 8-neuron model is the ceiling, not aggregation. The defense assumes attackers are a minority.

## Reproduce
Run `02_Intermediate_Advanced_Day2.ipynb` top to bottom. Our one harness change: `run_fl` reseeds at the start of every run so all methods share the same initial weights and batch order. `model_scripted.pt` and `submission.json` are in the repo.
