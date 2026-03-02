"""Experiment protocol: 50 vs 50 comparative study.

Protocol (Option E):
  Phase 1 — CONTROL: 50 runs, SAGE OFF, fixed category/type/difficulty.
  Phase 2 — TREATMENT: 50 runs, SAGE ON, same params. SAGE accumulates
            knowledge sequentially so run 50 benefits from observations
            gathered in runs 1-49.

Every run goes through: GENERATE → STATIC_ANALYSIS → VALIDATE (smoke test).
We record whether it passed each stage, the quality score, and wall-clock
time.  That gives us concrete, measurable data:

  a) Is SAGE-on FASTER (pipeline time)?
  b) Is SAGE-on BETTER (quality score, pass rates)?
  c) Does the treatment arm IMPROVE over its own run sequence (learning curve)?

Statistical methods (no scipy dependency):
  - Mann-Whitney U  (two-sample rank test)
  - Cohen's d       (effect size)
  - Chi-squared     (2x2 pass/fail proportions)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RunMetrics:
    """Metrics captured from a single pipeline run."""
    run_number: int
    sage_enabled: bool
    # Pass/fail at each pipeline stage
    static_analysis_passed: bool = False
    smoke_test_passed: bool = False       # container built + healthy
    pipeline_completed: bool = False      # reached COMPLETE (not DISCARD)
    # Scores
    quality_score: float = 0.0
    # Timing
    pipeline_time_seconds: float = 0.0
    # Stage the pipeline reached before stopping
    terminal_state: str = "DISCARD"
    discard_reason: str = ""
    # Calibration
    target_difficulty: float = 0.0
    calibrated_difficulty: float | None = None
    calibration_gap: float | None = None
    # Repair attempts needed
    repair_attempts: int = 0
    # Timestamp
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ComparativeResult:
    """Full results from the 50-vs-50 experiment."""
    category: str = ""
    difficulty: float = 0.0
    control_metrics: list[RunMetrics] = field(default_factory=list)
    treatment_metrics: list[RunMetrics] = field(default_factory=list)
    # Learning curve: treatment runs in 10-run windows
    learning_windows: list[dict[str, Any]] = field(default_factory=list)
    # Stats: quality
    quality_p_value: float | None = None
    quality_effect_size: float | None = None
    # Stats: pipeline time
    time_p_value: float | None = None
    time_effect_size: float | None = None
    # Stats: pass rate (chi-squared)
    pass_rate_chi2: float | None = None
    pass_rate_p_value: float | None = None


# ---------------------------------------------------------------------------
# Pipeline function type
# ---------------------------------------------------------------------------

PipelineFn = Callable[[str, float, bool, int], Awaitable[RunMetrics]]
# args: (category, difficulty, sage_enabled, run_number) -> RunMetrics


# ---------------------------------------------------------------------------
# Statistics (no scipy dependency)
# ---------------------------------------------------------------------------

def _ranks(combined: list[float]) -> list[float]:
    """Assign ranks handling ties by averaging."""
    n = len(combined)
    indexed = sorted(range(n), key=lambda i: combined[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and combined[indexed[j + 1]] == combined[indexed[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


def mann_whitney_u(x: list[float], y: list[float]) -> tuple[float, float]:
    """Mann-Whitney U test. Returns (U, p-value).
    Normal approximation — valid for n >= 8.
    """
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0.0, 1.0

    combined = x + y
    ranks = _ranks(combined)
    r1 = sum(ranks[:nx])
    u1 = r1 - nx * (nx + 1) / 2.0
    u2 = nx * ny - u1
    u_stat = min(u1, u2)

    mu = nx * ny / 2.0
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12.0)
    if sigma == 0:
        return u_stat, 1.0
    z = (u_stat - mu) / sigma
    return u_stat, 2.0 * _norm_cdf(-abs(z))


def chi_squared_2x2(a: int, b: int, c: int, d: int) -> tuple[float, float]:
    """Chi-squared test for a 2x2 contingency table.

        |  Pass  |  Fail  |
    ----|--------|--------|
    Ctrl|   a    |   b    |
    Treat|  c    |   d    |

    Returns (chi2, p-value). Uses Yates' correction.
    """
    n = a + b + c + d
    if n == 0:
        return 0.0, 1.0
    expected_min = min(
        (a + b) * (a + c) / n,
        (a + b) * (b + d) / n,
        (c + d) * (a + c) / n,
        (c + d) * (b + d) / n,
    ) if n > 0 else 0
    if expected_min < 1:
        return 0.0, 1.0  # too sparse for chi-squared

    # Yates' correction
    num = n * (abs(a * d - b * c) - n / 2.0) ** 2
    denom = (a + b) * (c + d) * (a + c) * (b + d)
    if denom == 0:
        return 0.0, 1.0
    chi2 = num / denom
    # p-value from chi2 with 1 df using survival function approximation
    p = _chi2_sf(chi2, 1)
    return chi2, p


def _chi2_sf(x: float, df: int) -> float:
    """Survival function (1-CDF) for chi-squared with df=1.
    Uses the relationship: chi2(1) = z^2 where z ~ N(0,1).
    """
    if x <= 0:
        return 1.0
    z = math.sqrt(x)
    return 2.0 * _norm_cdf(-z)  # two-tailed


def _norm_cdf(z: float) -> float:
    """Standard normal CDF via error function."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def cohens_d(x: list[float], y: list[float]) -> float:
    """Cohen's d (pooled std dev)."""
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return 0.0
    mx = sum(x) / nx
    my = sum(y) / ny
    vx = sum((v - mx) ** 2 for v in x) / (nx - 1)
    vy = sum((v - my) ** 2 for v in y) / (ny - 1)
    pooled = ((nx - 1) * vx + (ny - 1) * vy) / (nx + ny - 2)
    if pooled <= 0:
        return 0.0
    return (mx - my) / math.sqrt(pooled)


# ---------------------------------------------------------------------------
# ExperimentProtocol
# ---------------------------------------------------------------------------

class ExperimentProtocol:
    """50-vs-50 comparative experiment."""

    def __init__(self, on_progress: Callable[[str], Any] | None = None):
        self._on_progress = on_progress

    def _log(self, msg: str) -> None:
        if self._on_progress:
            self._on_progress(msg)

    async def run_comparative(
        self,
        category: str,
        difficulty: float,
        runs_per_arm: int,
        pipeline_fn: PipelineFn,
        control_only: bool = False,
    ) -> ComparativeResult:
        """Run the full 50-vs-50 experiment.

        Phase 1: `runs_per_arm` runs with SAGE OFF (control).
        Phase 2: `runs_per_arm` runs with SAGE ON, sequential (treatment).
                 Skipped if control_only=True.
        """
        result = ComparativeResult(category=category, difficulty=difficulty)

        # --- Phase 1: CONTROL (SAGE OFF) ---
        self._log(f"=== PHASE 1: CONTROL ARM ({runs_per_arm} runs, SAGE OFF) ===")
        for i in range(runs_per_arm):
            self._log(f"  Control run {i + 1}/{runs_per_arm}")
            m = await pipeline_fn(category, difficulty, False, i + 1)
            result.control_metrics.append(m)
            self._log(
                f"    -> {m.terminal_state} | quality={m.quality_score:.0f} "
                f"| time={m.pipeline_time_seconds:.1f}s "
                f"| smoke={'PASS' if m.smoke_test_passed else 'FAIL'}"
            )

        if control_only:
            self._log(f"\n=== CONTROL-ONLY MODE: skipping treatment arm ===")
            self._log(f"  Generated {runs_per_arm} vanilla challenges for separate evaluation.")
            return result

        # --- Phase 2: TREATMENT (SAGE ON, sequential) ---
        self._log(f"\n=== PHASE 2: TREATMENT ARM ({runs_per_arm} runs, SAGE ON) ===")
        for i in range(runs_per_arm):
            self._log(f"  Treatment run {i + 1}/{runs_per_arm}")
            m = await pipeline_fn(category, difficulty, True, i + 1)
            result.treatment_metrics.append(m)
            self._log(
                f"    -> {m.terminal_state} | quality={m.quality_score:.0f} "
                f"| time={m.pipeline_time_seconds:.1f}s "
                f"| smoke={'PASS' if m.smoke_test_passed else 'FAIL'}"
            )

        # --- Learning curve: 10-run windows within treatment ---
        window_size = max(1, runs_per_arm // 5)  # 5 windows
        for w in range(0, runs_per_arm, window_size):
            window = result.treatment_metrics[w:w + window_size]
            if not window:
                continue
            scores = [m.quality_score for m in window]
            passes = sum(1 for m in window if m.smoke_test_passed)
            result.learning_windows.append({
                "window": f"runs {w + 1}-{w + len(window)}",
                "avg_quality": round(sum(scores) / len(scores), 1),
                "smoke_pass_rate": f"{passes}/{len(window)}",
                "avg_time": round(
                    sum(m.pipeline_time_seconds for m in window) / len(window), 1
                ),
            })

        # --- Statistical analysis ---
        ctrl_q = [m.quality_score for m in result.control_metrics]
        treat_q = [m.quality_score for m in result.treatment_metrics]
        ctrl_t = [m.pipeline_time_seconds for m in result.control_metrics]
        treat_t = [m.pipeline_time_seconds for m in result.treatment_metrics]

        if len(ctrl_q) >= 8 and len(treat_q) >= 8:
            _, result.quality_p_value = mann_whitney_u(treat_q, ctrl_q)
            result.quality_effect_size = cohens_d(treat_q, ctrl_q)
            _, result.time_p_value = mann_whitney_u(treat_t, ctrl_t)
            result.time_effect_size = cohens_d(treat_t, ctrl_t)

        # Pass rate chi-squared
        ctrl_pass = sum(1 for m in result.control_metrics if m.smoke_test_passed)
        ctrl_fail = len(result.control_metrics) - ctrl_pass
        treat_pass = sum(1 for m in result.treatment_metrics if m.smoke_test_passed)
        treat_fail = len(result.treatment_metrics) - treat_pass
        result.pass_rate_chi2, result.pass_rate_p_value = chi_squared_2x2(
            ctrl_pass, ctrl_fail, treat_pass, treat_fail
        )

        return result

    def generate_report(self, r: ComparativeResult) -> str:
        """Generate the full comparison report."""
        lines: list[str] = []
        lines.append("=" * 72)
        lines.append("  SAGE INSTITUTIONAL MEMORY — COMPARATIVE EXPERIMENT")
        lines.append("=" * 72)
        lines.append(f"  Category: {r.category}   Difficulty: {r.difficulty}")
        lines.append(f"  Control: {len(r.control_metrics)} runs (SAGE OFF)")
        if r.treatment_metrics:
            lines.append(f"  Treatment: {len(r.treatment_metrics)} runs (SAGE ON)")
        else:
            lines.append(f"  Treatment: CONTROL-ONLY (no treatment arm)")
        lines.append("")

        ctrl = r.control_metrics
        treat = r.treatment_metrics
        ctrl_q = [m.quality_score for m in ctrl]
        treat_q = [m.quality_score for m in treat]
        ctrl_t = [m.pipeline_time_seconds for m in ctrl]
        treat_t = [m.pipeline_time_seconds for m in treat]

        control_only = len(treat) == 0

        # === Section A: Quality ===
        lines.append("  A. QUALITY SUMMARY" if control_only else "  A. QUALITY COMPARISON")
        lines.append("  " + "-" * 60)

        if control_only:
            # Control-only: just summarize the vanilla arm
            lines.append(f"  {'Metric':<30s} {'Control':>12s}")
            lines.append("  " + "-" * 60)
            ctrl_smoke = sum(1 for m in ctrl if m.smoke_test_passed)
            ctrl_static = sum(1 for m in ctrl if m.static_analysis_passed)
            ctrl_complete = sum(1 for m in ctrl if m.pipeline_completed)
            lines.append(f"  {'Smoke test pass rate':<30s} {ctrl_smoke}/{len(ctrl):>9}")
            lines.append(f"  {'Static analysis pass rate':<30s} {ctrl_static}/{len(ctrl):>9}")
            lines.append(f"  {'Pipeline COMPLETE rate':<30s} {ctrl_complete}/{len(ctrl):>9}")
            lines.append(f"  {'Avg quality score':<30s} {_avg(ctrl_q):>12.1f}")
            lines.append(f"  {'Quality std dev':<30s} {_std(ctrl_q):>12.1f}")
            lines.append(f"  {'Avg repair attempts':<30s} {_avg([m.repair_attempts for m in ctrl]):>12.2f}")
            lines.append("")
            lines.append("  B. SPEED SUMMARY")
            lines.append("  " + "-" * 60)
            lines.append(f"  {'Avg pipeline time (s)':<30s} {_avg(ctrl_t):>12.1f}")
            lines.append(f"  {'Pipeline time std dev':<30s} {_std(ctrl_t):>12.1f}")
            ctrl_t_sorted = sorted(ctrl_t)
            lines.append(f"  {'Median pipeline time (s)':<30s} {_median(ctrl_t_sorted):>12.1f}")
            lines.append("")
            lines.append("  CONTROL-ONLY MODE: no treatment arm, no statistical comparison.")
            lines.append("  Use evaluate_all.sh --both to compare vanilla vs SAGE evaluators.")
            lines.append("=" * 72)
            return "\n".join(lines)

        # Full comparative report (both arms)
        lines.append(f"  {'Metric':<30s} {'Control':>12s} {'Treatment':>12s} {'Delta':>10s}")
        lines.append("  " + "-" * 60)

        ctrl_smoke = sum(1 for m in ctrl if m.smoke_test_passed)
        treat_smoke = sum(1 for m in treat if m.smoke_test_passed)
        lines.append(
            f"  {'Smoke test pass rate':<30s} "
            f"{ctrl_smoke}/{len(ctrl):>9} "
            f"{treat_smoke}/{len(treat):>9} "
            f"{(treat_smoke / max(len(treat), 1) - ctrl_smoke / max(len(ctrl), 1)) * 100:>+9.1f}%"
        )

        ctrl_static = sum(1 for m in ctrl if m.static_analysis_passed)
        treat_static = sum(1 for m in treat if m.static_analysis_passed)
        lines.append(
            f"  {'Static analysis pass rate':<30s} "
            f"{ctrl_static}/{len(ctrl):>9} "
            f"{treat_static}/{len(treat):>9} "
            f"{(treat_static / max(len(treat), 1) - ctrl_static / max(len(ctrl), 1)) * 100:>+9.1f}%"
        )

        ctrl_complete = sum(1 for m in ctrl if m.pipeline_completed)
        treat_complete = sum(1 for m in treat if m.pipeline_completed)
        lines.append(
            f"  {'Pipeline COMPLETE rate':<30s} "
            f"{ctrl_complete}/{len(ctrl):>9} "
            f"{treat_complete}/{len(treat):>9} "
            f"{(treat_complete / max(len(treat), 1) - ctrl_complete / max(len(ctrl), 1)) * 100:>+9.1f}%"
        )

        lines.append(
            f"  {'Avg quality score':<30s} "
            f"{_avg(ctrl_q):>12.1f} "
            f"{_avg(treat_q):>12.1f} "
            f"{_avg(treat_q) - _avg(ctrl_q):>+10.1f}"
        )
        lines.append(
            f"  {'Quality std dev':<30s} "
            f"{_std(ctrl_q):>12.1f} "
            f"{_std(treat_q):>12.1f}"
        )

        ctrl_repairs = _avg([m.repair_attempts for m in ctrl])
        treat_repairs = _avg([m.repair_attempts for m in treat])
        lines.append(
            f"  {'Avg repair attempts':<30s} "
            f"{ctrl_repairs:>12.2f} "
            f"{treat_repairs:>12.2f} "
            f"{treat_repairs - ctrl_repairs:>+10.2f}"
        )
        lines.append("")

        # === Section B: Does SAGE make it FASTER? ===
        lines.append("  B. SPEED COMPARISON")
        lines.append("  " + "-" * 60)
        lines.append(
            f"  {'Avg pipeline time (s)':<30s} "
            f"{_avg(ctrl_t):>12.1f} "
            f"{_avg(treat_t):>12.1f} "
            f"{_avg(treat_t) - _avg(ctrl_t):>+10.1f}"
        )
        lines.append(
            f"  {'Pipeline time std dev':<30s} "
            f"{_std(ctrl_t):>12.1f} "
            f"{_std(treat_t):>12.1f}"
        )

        # Median
        ctrl_t_sorted = sorted(ctrl_t)
        treat_t_sorted = sorted(treat_t)
        ctrl_med = _median(ctrl_t_sorted)
        treat_med = _median(treat_t_sorted)
        lines.append(
            f"  {'Median pipeline time (s)':<30s} "
            f"{ctrl_med:>12.1f} "
            f"{treat_med:>12.1f} "
            f"{treat_med - ctrl_med:>+10.1f}"
        )
        lines.append("")

        # === Section C: Learning curve ===
        lines.append("  C. LEARNING CURVE (treatment arm, windowed)")
        lines.append("  " + "-" * 60)
        lines.append(f"  {'Window':<20s} {'Avg Quality':>12s} {'Smoke Pass':>12s} {'Avg Time':>10s}")
        lines.append("  " + "-" * 60)
        for w in r.learning_windows:
            lines.append(
                f"  {w['window']:<20s} "
                f"{w['avg_quality']:>12.1f} "
                f"{w['smoke_pass_rate']:>12s} "
                f"{w['avg_time']:>10.1f}s"
            )

        # First-half vs second-half within treatment
        if len(treat_q) >= 10:
            mid = len(treat_q) // 2
            first = treat_q[:mid]
            second = treat_q[mid:]
            delta = _avg(second) - _avg(first)
            lines.append("")
            lines.append(f"  First half avg (runs 1-{mid}):     {_avg(first):.1f}")
            lines.append(f"  Second half avg (runs {mid + 1}-{len(treat_q)}):  {_avg(second):.1f}")
            lines.append(f"  Improvement within treatment:     {delta:+.1f}")
        lines.append("")

        # === Section D: Statistical tests ===
        lines.append("  D. STATISTICAL SIGNIFICANCE")
        lines.append("  " + "-" * 60)

        lines.append("  Quality (Mann-Whitney U):")
        if r.quality_p_value is not None:
            sig = _sig_label(r.quality_p_value)
            lines.append(f"    p-value:     {r.quality_p_value:.4f}  ({sig})")
            lines.append(f"    Effect size: {r.quality_effect_size:.3f}  (Cohen's d, {_d_label(r.quality_effect_size)})")
        else:
            lines.append("    Insufficient data")
        lines.append("")

        lines.append("  Pipeline time (Mann-Whitney U):")
        if r.time_p_value is not None:
            sig = _sig_label(r.time_p_value)
            lines.append(f"    p-value:     {r.time_p_value:.4f}  ({sig})")
            lines.append(f"    Effect size: {r.time_effect_size:.3f}  (Cohen's d, {_d_label(r.time_effect_size)})")
        else:
            lines.append("    Insufficient data")
        lines.append("")

        lines.append("  Pass rate (Chi-squared):")
        if r.pass_rate_p_value is not None:
            sig = _sig_label(r.pass_rate_p_value)
            lines.append(f"    chi2:        {r.pass_rate_chi2:.3f}")
            lines.append(f"    p-value:     {r.pass_rate_p_value:.4f}  ({sig})")
        else:
            lines.append("    Insufficient data")
        lines.append("")

        lines.append("  Legend: * p<0.05  ** p<0.01  *** p<0.001  n.s. = not significant")
        lines.append("  Cohen's d: |d|<0.2 negligible, 0.2-0.5 small, 0.5-0.8 medium, >0.8 large")
        lines.append("=" * 72)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0

def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _avg(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))

def _median(sorted_values: list[float]) -> float:
    n = len(sorted_values)
    if n == 0:
        return 0.0
    if n % 2 == 1:
        return sorted_values[n // 2]
    return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2.0

def _sig_label(p: float) -> str:
    if p < 0.001: return "***"
    if p < 0.01: return "**"
    if p < 0.05: return "*"
    return "n.s."

def _d_label(d: float | None) -> str:
    if d is None: return "N/A"
    ad = abs(d)
    if ad >= 0.8: return "large"
    if ad >= 0.5: return "medium"
    if ad >= 0.2: return "small"
    return "negligible"
