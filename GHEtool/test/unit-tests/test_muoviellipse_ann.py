"""MuoviELLIPSE ANN: numpy inference stays close to the torch reference."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

from GHEtool.VariableClasses.PipeData.MuoviEllipse import MuoviEllipse

GOLDEN = Path(__file__).parent / "data" / "muoviellipse_ann_golden.npz"

# (size_label, a, b, wall, spacing)
SIZES = (
    ("32", 37e-3, 26e-3, 3e-3, 0.03),
    ("40", 46e-3, 33e-3, 3e-3, 0.03),
    ("45", 51e-3, 37e-3, 3e-3, 0.03),
    ("50", 58e-3, 41e-3, 3e-3, 0.03),
    ("55", 64e-3, 45e-3, 3e-3, 0.03),
    ("63", 73e-3, 52e-3, 3e-3, 0.03),
)


def test_muoviellipse_module_does_not_import_torch():
    spec = importlib.util.find_spec("GHEtool.VariableClasses.PipeData.MuoviEllipse")
    source = Path(spec.origin).read_text(encoding="utf-8")
    assert "import torch" not in source
    assert "import joblib" not in source
    assert "sklearn" not in source


@pytest.mark.parametrize("size,a,b,wall,spacing", SIZES)
def test_predict_rb_ra_series_matches_torch_golden(size, a, b, wall, spacing):
    gold = np.load(GOLDEN)
    X = gold["X"]
    y_ref = gold[f"y_{size}"]
    pipe = MuoviEllipse(1.5, a, b, wall, spacing)
    Rb, Ra = pipe.predict_Rb_Ra_series(X[:, 0], X[:, 1], X[:, 2], X[:, 3], X[:, 4])
    y = np.column_stack([np.asarray(Rb).ravel(), np.asarray(Ra).ravel()])
    # float32 torch vs float64 numpy: ~1e-7 absolute on Rb/Ra (issue #483)
    np.testing.assert_allclose(y, y_ref, rtol=1e-6, atol=1e-6)


@pytest.mark.parametrize("size,a,b,wall,spacing", SIZES[:1])
def test_predict_rb_ra_series_vectorized_matches_scalar(size, a, b, wall, spacing):
    gold = np.load(GOLDEN)
    X = gold["X"]
    pipe = MuoviEllipse(1.5, a, b, wall, spacing)
    Rb_v, Ra_v = pipe.predict_Rb_Ra_series(X[:, 0], X[:, 1], X[:, 2], X[:, 3], X[:, 4])
    Rb_s = []
    Ra_s = []
    for row in X:
        rb, ra = pipe.predict_Rb_Ra_series(row[0], row[1], row[2], row[3], row[4])
        Rb_s.append(float(np.asarray(rb).reshape(-1)[0]))
        Ra_s.append(float(np.asarray(ra).reshape(-1)[0]))
    np.testing.assert_allclose(np.asarray(Rb_v).ravel(), Rb_s, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(np.asarray(Ra_v).ravel(), Ra_s, rtol=1e-12, atol=1e-12)


def test_ann_weights_cached_on_pipe():
    pipe = MuoviEllipse(1.5, 37e-3, 26e-3, 3e-3, 0.03)
    assert getattr(pipe, "_ann", None) is None
    pipe.predict_Rb_Ra_series(0.075, 0.03, 0.05, 1.5, 2.5)
    first = pipe._ann
    pipe.predict_Rb_Ra_series(0.08, 0.03, 0.05, 1.5, 2.5)
    assert pipe._ann is first
