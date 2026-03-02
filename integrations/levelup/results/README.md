# Experiment Results

## Directory Structure

Each experiment run produces a timestamped directory:

```
results/
├── README.md                      ← This file
├── YYYYMMDD_HHMMSS_sqli_1.5/     ← One experiment run
│   ├── raw.json                   ← Full machine-readable data (100 RunMetrics)
│   ├── report.txt                 ← ASCII report (copy of stdout)
│   ├── metadata.json              ← Run config, versions, environment
│   └── notes.md                   ← Human observations (fill in after review)
└── ...
```

## Naming Convention

`{date}_{time}_{category}_{difficulty}` — e.g., `20260301_143000_sqli_1.5`

## What Goes in metadata.json

```json
{
  "experiment_date": "2026-03-01T14:30:00Z",
  "runs_per_arm": 50,
  "category": "sqli",
  "difficulty": 1.5,
  "sage_endpoint": "http://localhost:8080",
  "sage_nodes": 4,
  "llm_provider": "google",
  "llm_model": "gemini-3-flash-preview",
  "python_version": "3.11.x",
  "sage_commit": "<git sha>",
  "levelup_source_commit": "<git sha of level up backend copied>",
  "docker_version": "x.x.x",
  "machine": "macOS Darwin 25.3.0, Apple M-series",
  "dry_run": false
}
```

## Checklist After Each Experiment

- [ ] Verify `raw.json` has exactly N control + N treatment entries
- [ ] Verify no CRASH entries (pipeline infrastructure failure, not SAGE)
- [ ] Record any anomalies in `notes.md` (e.g., Docker daemon restart mid-run)
- [ ] Commit results to git with descriptive message
- [ ] If p < 0.05 on any metric, double-check by re-running (replication)

## What Reviewers Will Ask

1. **"How do you know it's not just LLM randomness?"**
   → That's what the control arm is for. Same LLM, same params, same everything
   except SAGE. Mann-Whitney U compares distributions, not single points.

2. **"N=50 seems small."**
   → 50 per arm detects a medium effect (d=0.5) at 80% power. If the effect
   is smaller than d=0.5, it's arguably not practically significant for a PoC.

3. **"Why not randomize / interleave?"**
   → The treatment arm MUST be sequential because SAGE's value proposition is
   cumulative learning. Interleaving would prevent knowledge accumulation.
   The control arm runs first to avoid any ordering bias from SAGE state.

4. **"Could Docker caching explain the speed difference?"**
   → Each run builds a fresh container from LLM-generated code. No image
   reuse between runs. Docker layer cache is cleared between experiments.

5. **"Quality score seems subjective."**
   → It's computed from 9 objective sub-scores (see quality.py): solvability,
   par validation, repair count, static analysis, description length,
   narrative richness, step complexity, file count, tags. All deterministic.
