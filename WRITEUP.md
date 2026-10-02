# Equal Voice, Verified by Peers
**Subtitle:** One aggregation function that fixes non-IID skew and removes a poisoned bank in round 1, even when it never scales its update
**Tracks:** Advanced (primary), Intermediate (supporting)
**Project link:** https://github.com/Ackahkelvin45/hackathon

## Headline results

All numbers are F1 on NSL-KDD `KDDTest+`, with the organisers' `WeakMLP`, local training, split and 8 rounds unchanged.

| Track | Before: naive FedAvg | After: ours | Change |
|---|---|---|---|
| **Advanced**, official attack (bank 1 flips labels, scales 15x), seed 42 | **0.0511** | **0.7760** | **+0.7249** |
| Advanced, mean of 5 seeds | 0.2194 ± 0.1190 | 0.7672 ± 0.0100 | +0.5478 |
| **Intermediate**, non-IID, no attacker, seed 42 | **0.7117** | **0.7821** | **+0.0704** |
| Intermediate, mean of 5 seeds | 0.7169 ± 0.0057 | 0.7809 ± 0.0072 | +0.0641 |

The provided coordinate median scores 0.6855 under the same attack (0.6793 over 5 seeds). We report 5-seed means because naive FedAvg under attack swings between seeds, so one run overstates the gain.

Under the official attack the attacker was excluded in **40 of 40** rounds with **0 false flags** in 160 honest bank-rounds. The defended score equals what four honest banks reach if bank 1 never joins (0.7671 ± 0.0102), so the damage is fully removed. `model_scripted.pt` reproduces 0.7760 when loaded on its own.

## What we built

One function, `make_agg`, plugged into the notebook's `agg_fn` hook for both tracks. Each round:

1. **Normalise.** Divide each bank's update by its number of local SGD steps.
2. **Size check.** Flag a bank whose normalised update is more than 5x the median length.
3. **Peer check.** Every bank scores every candidate model on a 2,000-row sample of its own private data and returns one number, the AUC. A bank whose model ranks attacks worse than a coin flip for the median voter (AUC below 0.5) is quarantined and loses its vote.
4. **Average** the survivors with equal weights, rescaled by their mean step count.

Our only harness change is one line: `run_fl` reseeds at the start of each run, so before and after share initial weights and batch order.

## Why it works

**Equal voice fixes the skew.** Banks take 25 to 189 local steps per round. Naive FedAvg favours the largest bank twice: its update is longer because it trained longer, and it then gets the largest weight. Step normalisation (FedNova, Wang et al. 2020) removes the first effect and equal weights remove the second. Each half alone reaches about 0.755; together they reach 0.781, which beats naive FedAvg on IID data (0.758). It wins on 5 of 5 seeds and on 6 of 6 other Dirichlet partitions.

The gain is real ranking quality, not a shifted threshold: test AUC rises from 0.882 to 0.920. It comes from the rare attack families that the two smallest banks hold:

| Correctly classified | Naive | Ours |
|---|---|---|
| Probe attacks | 0.615 | 0.916 |
| R2L, U2R and unseen attacks | 0.033 | 0.231 |
| DoS attacks | 0.775 | 0.779 |
| Normal traffic | 0.964 | 0.921 |

The cost is visible in the last row: false alarms roughly double, and F1 on the in-distribution holdout dips from 0.955 to 0.950.

**Scaling is obvious once step counts are removed.** Honest banks stay at or below 2.7x the median; the 15x attacker starts at 19x and passes 150x.

**Label flipping needs a different signal, and direction is the wrong one.** Our first design flagged updates that pointed against the others. Under equal voice it fails: honest attack-heavy and normal-heavy banks legitimately pull in opposite directions. Across five clean runs, a "cosine below −0.5" rule would accuse honest banks 29 times, and the most hostile-looking honest bank reaches −0.87 once the attacker is gone. An honest minority and an attacker are geometrically the same.

They are not the same on data. A flipped model is wrong on *everyone's* traffic, while an honest minority bank's model is still right. In the official run, honest banks score 0.93 to 0.99 with their peers and the attacker scores 0.11 in round 1. The only threshold is chance level, so nothing is tuned. In every experiment the malicious banks also lie as validators in the worst way, scoring honest banks 0 and each other 1; the median absorbs this while honest banks are the majority.

**We do not clip.** Clipping survivors to the median length costs 0.078 F1 under the official attack, and clipping to 2x costs 0.010. With bank 1 gone, bank 0 is the only attack-heavy bank left, and clipping throttles exactly that bank.

## Stress tests

Final F1, mean of 5 seeds, malicious banks lying as validators.

| Scenario | Naive | Median | Ours | Attacker-rounds excluded | False flags |
|---|---|---|---|---|---|
| No attacker | 0.7169 | 0.7355 | **0.7809** | – | 0/200 |
| Bank 1, flip + 50x | 0.5210 | 0.6794 | **0.7672** | 40/40 | 0/160 |
| Bank 1, flip + 2x (under the size check) | 0.6735 | 0.6755 | **0.7672** | 40/40 | 0/160 |
| Bank 1, flip only | 0.6875 | 0.6747 | **0.7672** | 40/40 | 0/160 |
| Bank 0 (smallest), flip only | 0.6992 | 0.6763 | **0.7621** | 35/40 | 0/160 |
| Bank 2 (largest), flip only | 0.3393 | **0.7891** | 0.7854 | 40/40 | 0/160 |
| Banks 1+3, flip + 15x | 0.1381 | 0.7348 | **0.7762** | 80/80 | 0/120 |
| Banks 1+3, flip only, colluding | 0.7189 | 0.7471 | **0.7762** | 80/80 | 0/120 |
| Banks 0+1, flip only | 0.6724 | 0.5215 | **0.6795** | 75/80 | 0/120 |
| Official attack, 16 rounds | 0.2787 | 0.6848 | **0.7669** | 80/80 | 0/320 |
| Banks 1+3+4, flip only (malicious majority) | **0.6430** | 0.4531 | 0.3380 | 0/120 | 80/80 |

The two checks cover different attacks (F1, with attacker-rounds excluded):

| | Official, flip + 15x | Flip + 2x | Flip only |
|---|---|---|---|
| Size check only | 0.7672 (40/40) | 0.6455 (0/40) | 0.6985 (0/40) |
| Both checks | 0.7672 (40/40) | 0.7672 (40/40) | 0.7672 (40/40) |

## Where we fail

- **A malicious majority turns the peer check into a weapon.** Three lying banks out-vote two honest ones, frame them, and F1 falls to 0.338, below naive FedAvg. Without a root of trust, no vote survives a majority.
- **When banks 0 and 1 both attack**, we exclude them, but F1 stays at 0.68. They hold almost all the rare-attack data, and removing them removes that knowledge.
- **One late catch:** with bank 0 as attacker, one seed in five missed it until round 6.
- **The median ties us** when the largest bank is the attacker.

## What did not work

- **Our own first design** (direction test plus clipping, 0.6938 under attack). Both parts were wrong for the reasons above.
- **Server momentum:** 0.7234. **FedProx:** 0.7177, no gain, because drift was not the problem.
- **Class-balanced local loss on top of ours:** 0.7682, lower than ours alone.

## Honest limitations and credit

- **Credit.** Step-normalised equal weighting is FedNova. Teams Neuralynx and Zerooth published writeups using it before we finalised ours; we adopted it after reading them and reproduced their clean-data result. What we add is the peer check, the no-clipping finding, and the measurements above.
- **The peer check has a price.** Each bank needs a small labelled sample, sees its peers' one-round models (which the server already sees), and runs K extra evaluations per round.
- **Selection.** We compared aggregation variants on test F1 over 5 seeds, the only labelled evaluation the notebook provides. The 5x threshold was set from honest behaviour alone, and 0.5 is chance.
- **Recall stays near 0.67.** `KDDTest+` contains attack types absent from training, and an 8-neuron model is the ceiling.
- **Step counts come from reported row counts.** A bank that under-reports its size inflates its normalised update, which the size check bounds at 5x.

## Reproduce

Run `02_Intermediate_Advanced_Day2.ipynb` top to bottom, about four minutes on CPU. It prints every number above, draws the cover chart, and writes `model_scripted.pt` and `submission.json`.
