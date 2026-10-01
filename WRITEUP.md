# Flag, Drop, Clip — and Stop Weighting by Size
**Subtitle:** One aggregation function that fixes non-IID skew and names the poisoned bank, with every claim checked over 5 seeds
**Tracks:** Advanced (primary), Intermediate (supporting)
**Project link:** https://github.com/Ackahkelvin45/hackathon

## Headline result — Advanced (primary)

Official scenario: non-IID split, bank 1 flips its labels and scales its update 15x. Same `WeakMLP`, same 8 rounds, same test set (NSL-KDD `KDDTest+`).

| Aggregation under attack | F1, seed 42 (exported model) | F1, mean ± std over 5 seeds |
|---|---|---|
| Naive FedAvg (**before**) | **0.0511** | 0.2194 ± 0.1190 |
| Coordinate median (provided baseline) | 0.6855 | 0.6793 ± 0.0092 |
| Ours (**after**) | **0.6938** | **0.7018 ± 0.0100** |

**F1 recovered: +0.6427** on the notebook's seed, **+0.4824** averaged over 5 seeds. We report both because naive FedAvg under attack swings wildly between seeds and rounds, so a single run overstates the gain. The attacker was flagged in **40 of 40** attacker-rounds, with 1 false flag in 160 honest client-rounds.

`model_scripted.pt` in the repo reproduces 0.6938 when loaded on its own.

## Supporting result — Intermediate

Non-IID split, no attacker, the *same* aggregation function.

| Aggregation | F1, seed 42 | F1, 5 seeds |
|---|---|---|
| Naive FedAvg (**before**) | 0.7117 | 0.7169 ± 0.0057 |
| Coordinate median (provided) | 0.7489 | 0.7355 ± 0.0148 |
| Ours (**after**) | 0.7467 | **0.7473 ± 0.0088** |
| Naive FedAvg on IID data (ceiling) | – | 0.7580 ± 0.0065 |

**Gain: +0.0350** (seed 42), **+0.0305** (5 seeds). That closes 74% of the gap between non-IID and IID.

## What we built

One function, `make_agg`, plugged into the notebook's `agg_fn` hook. Each round it looks at every bank's update (local weights minus previous global weights) and:

1. **Norm rule.** Flags a bank whose update is more than 3x the median length.
2. **Direction rule.** Flags a bank whose update points against the others (cosine below −0.5 to the sum of their unit updates), but only if those others agree with each other (coherence at least 0.5).
3. **Drop** flagged banks for that round, never more than a minority.
4. **Clip** the survivors to the median length.
5. Take an **equal-weight** mean, not a size-weighted one.

The model, local training, rounds and data split are untouched. Our only harness change is one line: `run_fl` reseeds at the start of each run, so before and after share initial weights and batch order.

## Why it works

**Equal weights fix the skew.** Every bank trains one local epoch, so a bank with 8x the rows takes 8x the SGD steps, and its update is already longer. Size-weighting then counts that bank a second time. Bank 2 holds 43% of the rows, so naive FedAvg is close to "whatever bank 2 says". With one local epoch, normalising each update by its step count (FedNova, Wang et al. 2020) reduces to an equal-weight mean, up to a global step size. Two checks support this reading. Equal weights *alone* score 0.7536 ± 0.0094. And on the IID split, where sizes are equal, our aggregator and naive FedAvg are indistinguishable (0.7579 vs 0.7580): the fix only acts when there is skew.

**The attack leaves two fingerprints.** Scaling makes the update 9 to 47 times the median length, while honest banks stay within about 2x. Label flipping reverses the gradient, so bank 1's cosine to the others sat between −0.47 and −0.69 from round 2. The norm rule catches the first, the direction rule the second, and clipping bounds anything that slips past both.

**The detector must know when to abstain.** This was our main lesson. Once the model converges, honest banks with opposite label mixes pull in opposite directions *by design*: an attack-heavy bank and a normal-heavy bank look like adversaries to each other. Without the coherence gate, the detector raises 20 false flags in 400 client-rounds of a clean 16-round run. With the gate it raises none, because it only trusts the direction test while the rest of the consortium agrees with itself.

## Stress tests: where we win and where we lose

Final F1, mean of 5 seeds.

| Scenario | Naive | Median | Ours | Attacker-rounds caught | False flags |
|---|---|---|---|---|---|
| No attacker | 0.7169 | 0.7355 | **0.7473** | – | 0/200 |
| Bank 1, flip + 50x | 0.5210 | 0.6794 | **0.7018** | 40/40 | 1/160 |
| Bank 1, flip + 2.9x (just under the norm rule) | 0.6595 | 0.6765 | **0.6987** | 35/40 | 0/160 |
| Bank 1, flip only | 0.6875 | 0.6747 | **0.6978** | 32/40 | 3/160 |
| Banks 1+3, flip + 15x | 0.1381 | 0.7348 | **0.7415** | 80/80 | 0/120 |
| Bank 2 (largest), flip only | 0.3393 | **0.7891** | 0.7617 | 25/40 | 0/160 |
| Banks 1+3, flip only, colluding | 0.7189 | **0.7471** | 0.7075 | 1/80 | 0/120 |
| Official attack, 16 rounds | 0.2787 | 0.6848 | **0.6970** | 80/80 | 7/320 |

An attacker who stops scaling to hide is still caught by direction. Round 1 is the usual miss, since from random weights nobody has a clear direction yet.

**We lose twice, and both are instructive.** Two colluding banks that flip without scaling (40% of the consortium) are not detected: they agree with each other, coherence drops, and the detector abstains. It makes no false accusations, but F1 falls slightly below naive. When the largest bank flips, the median beats us by 0.027. In the 16-round run, the 7 false flags all hit bank 0: once attack-heavy bank 1 is removed, bank 0 is the only attack-heavy bank left, and an honest lone minority is geometrically indistinguishable from an attacker. No direction-based test can resolve that.

## What did not work

- **Server momentum (FedAvgM 0.9):** 0.7234 ± 0.0090. Looked good on one seed, mostly noise over five.
- **FedProx (mu 0.1):** 0.7177 ± 0.0074. No gain. Drift from the global model was not the problem; double-counting was.
- **Weighting by label balance:** 0.7137 ± 0.0098, below naive. The skew is by attack family, and label balance is too coarse to see it.
- **Strikes and permanent quarantine:** an earlier version helped against colluders but locked honest banks out in 16-round runs, so we removed it.
- **Clipping costs a little:** our full aggregator scores 0.006 below equal weights alone on clean data. We keep it as the price of robustness.

## Limitations

- Defended F1 sits near 0.70, below the clean 0.75. That is exactly what four honest banks score when bank 1 never joins at all (0.7009 ± 0.0105, against our 0.7018 under attack). Bank 1 holds real attack data that is lost once its labels are flipped. The defense removes all of the damage; it cannot recover the information.
- Recall is about 0.54 for every method. `KDDTest+` contains attack types absent from training, and an 8-neuron model is the ceiling. Aggregation cannot fix that.
- Thresholds (3x, −0.5, 0.5) were set from diagnostics on this split. Gaps under about 0.02 are within seed noise.
- We assume an honest majority. An attacker who knows the rules can stay inside them, but then clipping and equal weights cap its influence at one bank's share.

## Reproduce

Run `02_Intermediate_Advanced_Day2.ipynb` top to bottom, about two minutes on CPU. It prints every number above, draws the cover chart, and writes `model_scripted.pt` and `submission.json`.
