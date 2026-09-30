# Secure AI Competition — Day 1: Federated Intrusion Detection

## Overview

Five banks, one shared enemy: build a federated model that catches fraud and network intrusions without ever pooling customer data, then find out what happens when one of your "banks" turns malicious.

## Description

You're a consortium of five banks. You all want to catch the same fraud and network-intrusion patterns, but you're legally forbidden from pooling your customer traffic data into one place. Federated learning (FL) is the answer: each bank trains a model locally on its own data, and only the trained model updates, never the raw data, get shared and averaged into one global model.

Today's job: you're given a working (but weak) federated intrusion-detection system trained on NSL-KDD. Make it better. Full technical detail and a working baseline are provided; you're improving a real system, not building one from a blank page.

This page is just for Day 1. The full hackathon includes two more tracks that unlock tomorrow. Come back any time today to check your leaderboard score.

## Getting Started

1. Copy the Day 1 starter notebook (`01_Beginner_Track_Day1.ipynb`) into your own Kaggle Notebook or Colab.
2. Run every cell top to bottom once. You should see a working baseline in under a minute.
3. Work in the section marked **🔧 YOUR TURN**. That's where your improvements go.
4. Run the submission cell to generate `submission.csv`, then upload it to the competition page.

## Files

| File | Purpose |
|------|---------|
| `01_Beginner_Track_Day1.ipynb` | Starter notebook with the federated baseline |
| `test_public.csv` | Public test set |
| `sample_submission.csv` | Submission format reference |

## Scoring

Fully automated. No writeup or video needed for this leaderboard. Predictions are scored against a held-out test set (precision / recall / F1, **not** accuracy) that no team has seen or trained on. Submit as many times as the daily limit allows; your best score counts unless you select a different final submission.

Your Day 1 result also feeds into your overall hackathon score. See the Evaluation tab on the main Hackathon page for how everything combines.

## Our solution (local run)

```
python3 -m venv .venv && .venv/bin/pip install torch scikit-learn pandas numpy
.venv/bin/python train.py   # single model, 25 rounds -> submission_single.csv
.venv/bin/python tune.py    # 3-seed ensemble, 40 rounds -> submission.csv (upload this)
```

Same data pipeline and FedAvg loop as the notebook. Changes: MLP 41→256→128→1 with dropout,
Adam lr 1e-3, 5 local epochs per round, 40 rounds, threshold tuned on a 5k validation slice.

| Model | Local holdout F1 (mirrors Kaggle test) |
|-------|-----------------------------------------|
| Notebook baseline | ~0.76 |
| train.py single | 0.9948 |
| tune.py ensemble | 0.9958 |
