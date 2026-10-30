"""Train a placeholder recruitment-risk model on simulated data."""
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

project_root = Path(__file__).resolve().parent.parent
out_path = project_root / "assets" / "model.pkl"

rng = np.random.default_rng(42)
n = 4000

positive = rng.uniform(30, 1250, n)
negative = rng.uniform(40, 1850, n)

# net score in [-1, 1]
score = (positive - negative) / (positive + negative)
probability = 1 / (1 + np.exp(-(4.0 * score - 0.5)))
recruited = rng.binomial(1, probability)

X = pd.DataFrame({"positive_events": positive, "negative_events": negative})
model = make_pipeline(StandardScaler(), LogisticRegression())
model.fit(X, recruited)

out_path.parent.mkdir(exist_ok=True)
with open(out_path, "wb") as f:
    pickle.dump(model, f)

print(f"Saved model to {out_path}")
