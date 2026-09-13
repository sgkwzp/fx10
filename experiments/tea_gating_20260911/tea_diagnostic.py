"""Small, reproducible Tea diagnostic for factorized procedural deviation.

This is a feasibility diagnostic, not a trained SOTA model. It uses only normal
training videos to build simple prototypes and evaluates held-out validation/test
videos at frame level.
"""
from pathlib import Path
import json
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
FEAT = ROOT / "data/Tea/vc_v_features_10fps"
LABEL = ROOT / "data/Tea/refined_label_v3"
PROTO = ROOT / "data/Tea/vc_normal_action_features"
OUT = ROOT / "results/tea_diagnostic"


def load_labels(video):
    ys, types = [], []
    for line in (LABEL / f"{video}.txt").read_text(encoding="utf-8").splitlines():
        parts = line.split("|")
        typ = parts[1] if len(parts) > 1 else "Normal"
        ys.append(0 if typ == "Normal" else 1)
        types.append(typ)
    return np.asarray(ys, dtype=np.int8), types


def normalize(x):
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-8)


def main():
    train = (ROOT / "data/Tea/training.txt").read_text().split()
    val = (ROOT / "data/Tea/validation.txt").read_text().split()
    test = (ROOT / "data/Tea/test.txt").read_text().split()
    protos = normalize(np.stack([np.load(p) for p in sorted(PROTO.glob("Action_*.npy"))]))
    normal_train = []
    for v in train:
        p = FEAT / f"{v}.npy"
        if not p.exists():
            continue
        x = np.load(p).astype(np.float32)
        y, _ = load_labels(v)
        normal_train.append(x[y == 0])
    normal_train = normalize(np.concatenate(normal_train))
    # Robust reference for temporal transition residuals.
    deltas = []
    for v in train:
        p = FEAT / f"{v}.npy"
        if not p.exists():
            continue
        x = np.load(p).astype(np.float32)
        y, _ = load_labels(v)
        x = normalize(x)
        keep = (y[1:] == 0) & (y[:-1] == 0)
        deltas.append(x[1:][keep] - x[:-1][keep])
    delta_ref = np.median(np.concatenate(deltas), axis=0)

    rows = []
    for split, videos in [("validation", val), ("test", test)]:
        for v in videos:
            p = FEAT / f"{v}.npy"
            if not p.exists():
                continue
            x = normalize(np.load(p).astype(np.float32))
            y, types = load_labels(v)
            n = min(len(x), len(y))
            x, y, types = x[:n], y[:n], types[:n]
            # Visual residual: distance to the closest normal action prototype.
            visual = 1.0 - (x @ protos.T).max(axis=1)
            # Order residual: deviation from the normal temporal transition.
            dx = np.vstack([np.zeros((1, x.shape[1]), dtype=x.dtype), np.diff(x, axis=0)])
            order = np.linalg.norm(dx - delta_ref, axis=1)
            # Effect residual: distance to normal feature manifold (kNN proxy).
            # Subsample reference to keep the diagnostic lightweight.
            ref = normal_train[::max(1, len(normal_train)//2000)]
            effect = 1.0 - (x @ ref.T).max(axis=1)
            scores = {"visual": visual, "order": order, "effect": effect}
            for name, s in scores.items():
                rows.append({"split": split, "video": v, "score": name, "y": y, "s": s, "types": types})
            fused = (visual - visual.mean()) / (visual.std() + 1e-6)
            fused += (order - order.mean()) / (order.std() + 1e-6)
            fused += (effect - effect.mean()) / (effect.std() + 1e-6)
            rows.append({"split": split, "video": v, "score": "factorized_fused", "y": y, "s": fused, "types": types})

    summary = {}
    for split in ["validation", "test"]:
        summary[split] = {}
        for name in ["visual", "order", "effect", "factorized_fused"]:
            rr = [r for r in rows if r["split"] == split and r["score"] == name]
            y = np.concatenate([r["y"] for r in rr])
            s = np.concatenate([r["s"] for r in rr])
            summary[split][name] = {
                "frames": int(len(y)),
                "positive_rate": float(y.mean()),
                "roc_auc": float(roc_auc_score(y, s)) if len(np.unique(y)) > 1 else None,
                "average_precision": float(average_precision_score(y, s)) if y.sum() else None,
            }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # Per-error-type breakdown on test for the fused score.
    by_type = {}
    for r in [x for x in rows if x["split"] == "test" and x["score"] == "factorized_fused"]:
        for typ in sorted(set(r["types"])):
            mask = np.asarray([t == typ for t in r["types"]])
            by_type.setdefault(typ, []).extend(r["s"][mask].tolist())
    (OUT / "error_type_score_mean.json").write_text(json.dumps({k: float(np.mean(v)) for k, v in by_type.items()}, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
