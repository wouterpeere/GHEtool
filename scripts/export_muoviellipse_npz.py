#!/usr/bin/env python3
"""One-shot: dump MuoviELLIPSE torch+sklearn weights to .npz (needs torch/joblib).

Training can stay in torch out of tree. Runtime GHEtool only needs the .npz.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
ANN = ROOT / "GHEtool" / "VariableClasses" / "PipeData" / "ANN"
GOLDEN = ROOT / "GHEtool" / "test" / "unit-tests" / "data"
SIZES = ("32", "40", "45", "50", "55", "63")

# Interior + edge-ish points in SI units (r_b, spacing, R_fp, k_b, k_s)
GOLDEN_X = np.array(
    [
        [0.075, 0.030, 0.05, 1.5, 2.5],
        [0.050, 0.020, 0.02, 0.8, 1.2],
        [0.100, 0.040, 0.15, 2.0, 3.5],
        [0.060, 0.025, 0.08, 1.2, 2.0],
        [0.090, 0.035, 0.12, 1.8, 3.0],
        [0.070, 0.028, 0.04, 1.0, 1.8],
        [0.085, 0.032, 0.10, 1.6, 2.8],
        [0.055, 0.022, 0.03, 0.7, 1.5],
        [0.110, 0.045, 0.20, 2.4, 4.0],
        [0.065, 0.027, 0.06, 1.4, 2.2],
        [0.080, 0.033, 0.09, 1.7, 2.6],
        [0.095, 0.038, 0.11, 1.9, 3.2],
    ],
    dtype=np.float64,
)


def export_size(size: str) -> tuple[np.ndarray, np.ndarray]:
    folder = ANN / f"MuoviELLIPSE{size}"
    sd = torch.load(folder / "borehole_ann.pt", map_location="cpu", weights_only=True)
    xs = joblib.load(folder / "X_scaler.joblib")
    ys = joblib.load(folder / "y_scaler.joblib")
    pack = {
        "w0": sd["net.0.weight"].cpu().numpy(),
        "b0": sd["net.0.bias"].cpu().numpy(),
        "w1": sd["net.2.weight"].cpu().numpy(),
        "b1": sd["net.2.bias"].cpu().numpy(),
        "w2": sd["net.4.weight"].cpu().numpy(),
        "b2": sd["net.4.bias"].cpu().numpy(),
        "w3": sd["net.6.weight"].cpu().numpy(),
        "b3": sd["net.6.bias"].cpu().numpy(),
        "x_mean": np.asarray(xs.mean_, dtype=np.float64),
        "x_scale": np.asarray(xs.scale_, dtype=np.float64),
        "y_mean": np.asarray(ys.mean_, dtype=np.float64),
        "y_scale": np.asarray(ys.scale_, dtype=np.float64),
    }
    out = folder / "borehole_ann.npz"
    np.savez_compressed(out, **pack)
    print(f"wrote {out} ({out.stat().st_size} bytes)")

    # Torch reference (same graph as EllipseANN + StandardScaler)
    X = GOLDEN_X.astype(np.float32)
    X_s = ((GOLDEN_X - xs.mean_) / xs.scale_).astype(np.float32)
    model = torch.nn.Sequential(
        torch.nn.Linear(5, 64),
        torch.nn.Tanh(),
        torch.nn.Linear(64, 64),
        torch.nn.Tanh(),
        torch.nn.Linear(64, 32),
        torch.nn.Tanh(),
        torch.nn.Linear(32, 2),
    )
    model.load_state_dict(
        {
            "0.weight": sd["net.0.weight"],
            "0.bias": sd["net.0.bias"],
            "2.weight": sd["net.2.weight"],
            "2.bias": sd["net.2.bias"],
            "4.weight": sd["net.4.weight"],
            "4.bias": sd["net.4.bias"],
            "6.weight": sd["net.6.weight"],
            "6.bias": sd["net.6.bias"],
        }
    )
    model.eval()
    with torch.no_grad():
        y_s = model(torch.tensor(X_s)).numpy()
    y = y_s * ys.scale_ + ys.mean_
    return GOLDEN_X, y


def main() -> None:
    GOLDEN.mkdir(parents=True, exist_ok=True)
    payload = {"X": GOLDEN_X}
    for size in SIZES:
        _, y = export_size(size)
        payload[f"y_{size}"] = y
        print(f"  golden y_{size} shape {y.shape} Rb[{y[:, 0].min():.4f},{y[:, 0].max():.4f}]")
    gpath = GOLDEN / "muoviellipse_ann_golden.npz"
    np.savez_compressed(gpath, **payload)
    print(f"wrote {gpath}")


if __name__ == "__main__":
    main()
