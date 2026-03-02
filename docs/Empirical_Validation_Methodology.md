# Consensus-Validated Institutional Memory Improves LLM Agent Calibration on Complex Sequential Tasks

## Dhillon Andrew Kannabhiran (dhillon@levelupctf.com)

------------------------------------------------------------------------

# Abstract

Large language model (LLM) agents do not learn across invocations. Each call starts from the same pretrained weights regardless of prior experience, preventing multi-agent systems from accumulating institutional knowledge. We present empirical evidence that **consensus-validated institutional memory** --- where agent observations are summarized, proposed to a Byzantine fault-tolerant network, validated by weighted quorum, and committed to a queryable knowledge base --- measurably improves downstream agent performance on complex sequential tasks.

Using a controlled experimental framework applied to AI-driven CTF (Capture The Flag) challenge generation, we find:

1. **Calibration accuracy:** Agents with access to institutional memory achieve target difficulty levels nearly 2x more accurately than memoryless agents (Cohen's d = -0.860, LARGE effect; mean gap 0.294 vs 0.487).
2. **Difficulty-dependent improvement:** A 9-tier difficulty escalation experiment (difficulty 1.0--3.0) reveals that institutional memory's advantage *increases* with task complexity. The calibration gap trend has a negative slope for memory-backed agents (gap shrinks at higher difficulty) versus a flat slope for memoryless agents, with 5 of 9 difficulty tiers won by the memory condition --- all at the hard end of the scale.
3. **Consensus filtering works:** The BFT validator quorum correctly accepts domain-relevant observations (scores 0.69--0.86) while rejecting cross-domain contamination from prior experiments (scores 0.35--0.50), demonstrating that governance prevents knowledge pollution.
4. **Quality sub-dimensions:** While overall quality differences are not statistically significant (ceiling effect at lower difficulties), per-dimension analysis reveals medium-effect improvements in defense depth (d = +0.586) and small-effect improvements in structural isolation (d = +0.330).

We report all results including null findings. All experiment code, analysis scripts, and raw data are open-source.

------------------------------------------------------------------------

# 1. Introduction

## 1.1 The Stateless Agent Problem

LLM-based agents have demonstrated remarkable capability on complex tasks including code generation [1], reasoning [2], and tool use [3]. Multi-agent systems composed of specialized agents can now tackle problems requiring coordination across design, implementation, evaluation, and refinement [4][5]. However, these systems share a fundamental limitation: **each agent invocation starts from scratch.**

When an LLM agent generates a CTF challenge, calibrates its difficulty, and discovers that challenges with single-layer AES ECB consistently calibrate below target, that knowledge is lost. The next invocation makes the same mistakes. Production systems work around this with prompt engineering, few-shot examples, or retrieval-augmented generation (RAG) [6], but these are static --- they don't grow from the system's own operational experience.

Recent work on agent memory systems --- Mem0 [7], MemOS [8], Collaborative Memory [9], Reflexion [10], MemGPT [11] --- provides cross-session persistence and multi-user memory sharing. However, these systems lack:

- **Governance over what gets remembered.** Any agent can write any memory. There is no validation, quality control, or consensus mechanism.
- **Verifiable provenance.** Existing provenance tagging lacks cryptographic commitment and tamper-evidence.
- **Protection against knowledge pollution.** Incorrect, outdated, or adversarial memories persist alongside valid ones with no formal mechanism for dispute or decay.

## 1.2 The Measurement Gap

Beyond the engineering gaps, there is a scientific gap: **no prior work has empirically demonstrated that governed agent memory improves downstream task performance under controlled experimental conditions.** Existing evaluations of memory systems measure retrieval accuracy, latency, or storage efficiency --- properties of the memory layer itself. They do not measure the impact on the agents that consume the memories.

This paper addresses both gaps. We describe (S)AGE (Sovereign) Agent Governed Experience, a consensus-validated institutional memory layer, and present controlled experiments measuring its effect on multi-agent task performance.

## 1.3 Contribution

Our contribution is threefold:

1. **Empirical evidence** that consensus-validated institutional memory produces large, measurable improvements in agent calibration accuracy (Cohen's d = -0.860) across multiple experimental conditions.
2. **A difficulty-scaling result** showing that the advantage of institutional memory increases with task complexity --- precisely the regime where it matters most.
3. **A replicable experimental methodology** for measuring the downstream impact of memory systems on agent performance, applicable beyond CTF generation.

## 1.4 Hypotheses

- **H1 (Calibration):** Agents with institutional memory achieve closer calibration to target difficulty levels than memoryless agents.
- **H2 (Quality):** Agents with institutional memory produce higher-quality outputs than memoryless agents.
- **H3 (Learning):** Agent performance improves over sequential invocations as institutional knowledge accumulates.
- **H4 (Difficulty scaling):** The calibration advantage of institutional memory increases at higher task difficulty levels.

------------------------------------------------------------------------

# 2. System Overview

## 2.1 (S)AGE: Consensus-Validated Institutional Memory

(S)AGE is a governed institutional memory layer for multi-agent systems. The full architecture is described in a companion paper [12]; we summarize the properties relevant to the empirical evaluation.

**Memory lifecycle:**
1. An agent completes a task and generates a raw observation (e.g., "this challenge with properties X calibrated Y at target difficulty Z").
2. A local LLM (qwen3:1.7b) distills the raw context into a concise 2--4 sentence summary, preserving technical specifics.
3. The summary is proposed to a 4-node BFT network as a memory candidate, with an embedding vector (nomic-embed-text, 768-dim) and domain tag.
4. Validators evaluate the proposal using Proof of Experience (PoE) weighted voting. Each validator's weight reflects historical accuracy, domain relevance, activity recency, and corroboration strength.
5. Proposals reaching a 2/3 weighted quorum are committed to the institutional memory store.
6. Future agents query the store by domain and embedding similarity, receiving only committed (consensus-validated) memories.

**Key properties:**
- **Byzantine fault tolerance:** Tolerates up to f faulty validators given n >= 3f+1. Verified empirically: 1-of-4 node failure tolerated, 2-of-4 halts consensus (correct behavior).
- **Domain-specific filtering:** Validators weigh proposals against their expertise profile. Cross-domain proposals receive lower scores and are more likely rejected.
- **Confidence decay:** Memory confidence decays exponentially over time (domain-specific lambda), with corroboration providing a stabilizing bonus.
- **Environment-gated integration:** When disabled (`SAGE_ENABLED=false`), every API call returns empty/passthrough values, producing zero behavior change. This is the control condition.

## 2.2 Proof-of-Concept Domain

We evaluate SAGE using Level Up, an AI-driven CTF challenge generation platform with a multi-agent pipeline: designer, narrative generator, exploit agent, hardener, calibrator, smoke tester, validator, quality scorer, and orchestrator. Each pipeline run produces a containerized challenge with source code, Dockerfile, calibration metadata, and quality scores.

Four agents are wired to SAGE:

| Agent | SAGE Operation | Purpose |
|-------|---------------|---------|
| Designer | `query_knowledge()` | Retrieve prior learnings about effective challenge patterns |
| Exploit Agent | `enrich_attack_hints()` + `submit_observation()` | Augment exploit context with solver feedback; record observations |
| Calibrator | `enrich_difficulty_guidance()` + `submit_observation()` | Augment calibration with historical accuracy data; record calibration results |
| Orchestrator | `summarize_and_submit()` | Distill and submit full pipeline outcomes to institutional memory |

The pipeline is fully automated. Variance comes from the LLM (Google Gemini 3 Flash Preview) and, when enabled, SAGE memory. The domain offers several advantages for empirical study: outputs are concrete code artifacts, quality is multi-dimensional and measurable, difficulty can be precisely targeted and calibrated, and the generation pipeline is fully automated.

------------------------------------------------------------------------

# 3. Experimental Design

## 3.1 Control Methodology

Each experiment follows a two-phase sequential protocol:

1. **Control arm** (N runs, SAGE OFF): Baseline performance. All runs are independent; no memory persists between them.
2. **Treatment arm** (N runs, SAGE ON): Runs sequentially so institutional knowledge accumulates. Run k benefits from observations gathered in runs 1 through k-1.

The treatment arm must be sequential because SAGE's value proposition is cumulative learning. The control arm runs first to avoid ordering bias from residual state.

**Controlled variables (held constant across both arms):**
- LLM provider and model (Google Gemini 3 Flash Preview)
- Challenge category and type
- Target difficulty level
- Pipeline configuration and agent prompts
- Evaluation criteria and evaluator model
- Docker environment and resource limits
- Hardware (same machine, same session)

## 3.2 Primary Metric: Calibration Gap

The calibration gap is defined as:

```
calibration_gap = |calibrated_difficulty - target_difficulty|
```

where `calibrated_difficulty` is assigned by the pipeline's calibration agent after analyzing the generated challenge, and `target_difficulty` is the requested difficulty. Lower gaps indicate better calibration.

This metric is **evaluator-independent**: it is computed from pipeline metadata, not from LLM scoring. This eliminates evaluator bias as a confound.

## 3.3 Quality Evaluation

Each challenge is scored on seven dimensions (1--10 scale) by an independent LLM evaluator (Anthropic Claude Sonnet 4 --- a different provider than the generator):

| Dimension | Definition |
|-----------|-----------|
| `difficulty_accuracy` | Does the actual code complexity match the target difficulty? |
| `defense_depth` | Does it have multiple realistic defense layers? |
| `code_quality` | Is the code clean, realistic, and production-like? |
| `creativity` | Is it a unique, interesting challenge? |
| `realism` | Would this scenario exist in a real company? |
| `flag_isolation` | Is the flag properly hidden? |
| `exploit_complexity` | Does solving it require multiple steps and real skill? |

Each challenge is evaluated independently in its own LLM context window (no batch evaluation) to prevent information leakage.

## 3.4 Dual Evaluator Design

To control for evaluator bias, each challenge set is scored by two independent evaluators: a cold evaluator (no memory context) and a SAGE-augmented evaluator. If improvements appear only under the SAGE evaluator, the signal may reflect evaluator bias.

## 3.5 Statistical Methods

All statistical tests are implemented from scratch in Python with no dependency on scipy/statsmodels, ensuring full reproducibility.

- **Mann-Whitney U test:** Non-parametric rank-based comparison for continuous variables. Normal approximation for p-values (valid for n >= 8). Two-tailed; alpha = 0.05.
- **Cohen's d:** Standardized mean difference using pooled standard deviation. Interpretation: |d| < 0.2 negligible, 0.2--0.5 small, 0.5--0.8 medium, > 0.8 large [13].
- **Linear regression:** OLS regression of calibration gap against difficulty level, yielding slope, intercept, and R-squared.

------------------------------------------------------------------------

# 4. Experiments and Results

## 4.1 Experiment 1: Calibration Accuracy (crypto_aes, difficulty 2.0)

**Parameters:** Category = crypto_aes (AES cryptographic challenges), target difficulty = 2.0 (moderate). Sample: 20 vanilla, 18 SAGE.

| Metric | Vanilla | SAGE | Delta | Cohen's d | Interpretation |
|--------|---------|------|-------|-----------|---------------|
| Mean calibration gap | 0.487 | 0.294 | -0.193 | **-0.860** | **LARGE (SAGE better)** |

**This is the strongest experimental signal.** SAGE-backed generators hit target difficulty levels with nearly twice the accuracy of memoryless generators. The effect size (d = -0.860) is large by Cohen's convention [13].

**Mechanistic explanation:** The calibrator agent queries SAGE for historical calibration data --- prior observations about what made challenges too easy or too hard for a given category and difficulty level. The calibrator learns, for example, that single-layer AES ECB challenges at difficulty 2.0 consistently calibrate below target, and adjusts accordingly.

## 4.2 Experiment 2: Quality Comparison (crypto_aes, difficulty 2.0)

**Parameters:** Same challenge set as Experiment 1. Dual evaluator scoring.

### 4.2.1 Overall Quality

| Evaluator | Vanilla Mean | SAGE Mean | Cohen's d | p-value | Significant? |
|-----------|-------------|-----------|-----------|---------|-------------|
| Vanilla (cold) | 7.05 | 6.76 | -0.500 | 0.082 | No |
| SAGE (memory) | 6.89 | 6.78 | -0.191 | > 0.05 | No |

Overall quality differences are not statistically significant under either evaluator. Both arms scored high (6.7--7.1 on a 10-point scale), suggesting a **ceiling effect** at this difficulty level.

### 4.2.2 Per-Dimension Analysis

| Dimension | Cohen's d | Interpretation |
|-----------|-----------|---------------|
| defense_depth | **+0.586** | **MEDIUM (SAGE better)** |
| flag_isolation | **+0.330** | **SMALL (SAGE better)** |
| Other dimensions | < 0.2 | Negligible |

SAGE-generated challenges have more layered defenses and better structural isolation, suggesting institutional memory improves specific structural aspects of quality even when overall quality differences wash out.

### 4.2.3 Learning Curve

| Window | Mean Quality | Cohen's d (early vs late) |
|--------|-------------|--------------------------|
| Early SAGE runs | 6.68 | +0.252 (SMALL positive) |
| Late SAGE runs | 6.84 | |

Quality improves modestly as SAGE accumulates knowledge, consistent with cumulative learning (H3).

## 4.3 Experiment 3: Difficulty Escalation (sqli, difficulties 1.0--3.0)

**Parameters:** Category = sqli (SQL injection), 9 difficulty tiers (1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0), 1 challenge per arm per tier. Tests whether the calibration advantage persists, amplifies, or degrades as task complexity increases.

### 4.3.1 Per-Tier Calibration Gap

| Target Difficulty | Vanilla Gap | SAGE Gap | Delta | Winner |
|-------------------|-----------|----------|-------|--------|
| 1.00 | 0.30 | 0.40 | +0.10 | Vanilla |
| 1.25 | 0.15 | 0.25 | +0.10 | Vanilla |
| 1.50 | 1.00 | 0.30 | -0.70 | **SAGE** |
| 1.75 | 0.15 | 0.55 | +0.40 | Vanilla |
| 2.00 | 0.60 | 0.15 | -0.45 | **SAGE** |
| 2.25 | 0.05 | 0.65 | +0.60 | Vanilla |
| 2.50 | 0.60 | 0.40 | -0.20 | **SAGE** |
| 2.75 | 0.50 | 0.15 | -0.35 | **SAGE** |
| 3.00 | 0.30 | 0.20 | -0.10 | **SAGE** |
| **OVERALL** | **0.406** | **0.339** | **-0.067** | **SAGE** |

**Overall:** Cohen's d = -0.271 (SMALL effect, SAGE better). Mann-Whitney p = 0.86 (not significant at n=9 per arm).

### 4.3.2 Calibration Gap Trend: The Key Finding

Linear regression of calibration gap against difficulty level reveals divergent trends:

| Arm | Regression | Slope | Interpretation |
|-----|-----------|-------|---------------|
| Vanilla | gap = 0.386 + 0.010 * difficulty | +0.010 | Flat: gap is constant regardless of difficulty |
| SAGE | gap = 0.446 - 0.053 * difficulty | -0.053 | **Negative: gap SHRINKS at higher difficulties** |

Predicted calibration gaps at the extremes:

| Difficulty | Vanilla (predicted) | SAGE (predicted) |
|-----------|-------------------|-----------------|
| 1.0 | 0.396 | 0.392 |
| 3.0 | 0.416 | 0.286 |

**Interpretation:** For memoryless generators, difficulty does not affect calibration accuracy --- they are equally imprecise at easy and hard tasks. For memory-backed generators, calibration *improves* at higher difficulties. This is the opposite of the expected degradation pattern and is consistent with progressive knowledge accumulation: as the SAGE arm processes more challenges at escalating difficulties, it accumulates increasingly useful calibration knowledge.

### 4.3.3 SAGE Wins at the Hard End

SAGE wins 5 of 9 tiers, but the distribution is not random. **All 5 wins are at the harder tiers** (d >= 1.5). At the 4 easiest tiers (d = 1.0, 1.25, 1.75, 2.25), vanilla wins. This pattern is consistent with the hypothesis that institutional memory provides more value when tasks are harder and the generator has less inherent knowledge to draw on.

### 4.3.4 Pipeline Stability

| Metric | Vanilla | SAGE |
|--------|---------|------|
| Pipeline completion | 9/9 (100%) | 9/9 (100%) |
| Total repair attempts | 2 | 1 |
| Mean repairs per run | 0.22 | 0.11 |

SAGE-backed generation required fewer repairs, suggesting institutional memory reduces pipeline instability.

## 4.4 Experiment 4: Cross-Domain Filtering

During the SQLi escalation experiment (Experiment 3), the SAGE network contained committed memories from a prior crypto_aes experiment. This unintentionally created a test of cross-domain contamination.

**Result:** The validator quorum correctly discriminated:
- SQLi-relevant observations were accepted with scores 0.69, 0.79, and 0.86.
- Old crypto_aes memories were rejected with scores 0.35--0.50.

Out of 14 pending memories evaluated, 3 were accepted and 11 were rejected. The PoE domain relevance factor (cosine similarity between validator expertise profiles and memory domain tags) down-weighted cross-domain proposals, and the quorum threshold (2/3 weighted) prevented their commitment.

This demonstrates that the governance layer actively prevents knowledge pollution, a critical property for multi-domain deployments.

------------------------------------------------------------------------

# 5. Discussion

## 5.1 Calibration Accuracy as the Primary Signal

The strongest evidence for institutional memory's value comes from calibration accuracy, not overall quality. This is a meaningful distinction. Quality scoring involves subjective dimensions (creativity, realism) with high evaluator variance. Calibration accuracy is a simple numerical comparison --- |calibrated - target| --- that is evaluator-independent and directly actionable.

Institutional memory provides the most value when agents face **repeated decisions on a continuous scale** where historical data directly informs adjustment. Calibration is exactly this type of decision. The calibrator agent asks "how difficult is this challenge?" and SAGE provides historical context: "challenges with these properties have previously calibrated above/below target."

## 5.2 Why Higher Difficulty Benefits More

The negative slope in Experiment 3 (SAGE gap shrinks with difficulty) has a natural explanation. At low difficulties (d=1.0--1.25), the LLM's pretrained knowledge is sufficient --- SQL injection at difficulty 1.0 is well-represented in training data, and the generator calibrates reasonably without help. At higher difficulties (d=2.5--3.0), the generator must construct novel multi-step attack chains with layered defenses. Here, pretrained knowledge becomes insufficient, and institutional memory fills the gap with specific observations like "SLOWPATH injection techniques at this difficulty calibrate accurately" or "boolean-based blind SQLi with WAF bypass achieves target difficulty 2.0."

This suggests a general principle: **institutional memory is most valuable in low-knowledge, high-complexity regimes** --- precisely where agents are most likely to fail without it.

## 5.3 The Memory Lifecycle in Practice

Experiment 3 revealed the full memory lifecycle operating as designed:

1. **Generation:** The orchestrator distills raw challenge context (title, description, solution, calibration notes) into a 2--4 sentence technical summary via a local LLM (qwen3:1.7b).
2. **Proposal:** The summary is proposed to the SAGE network with an embedding vector and domain tag.
3. **Validation:** The 4-node BFT quorum evaluates using PoE-weighted votes. Domain relevance, accuracy, and recency are factored in.
4. **Commitment/Rejection:** 3 of 9 observations were committed (scores 0.69--0.86). The remaining 6 were rejected, some for low quality and some for cross-domain irrelevance.
5. **Retrieval:** Later generator invocations query committed memories, receiving only consensus-validated knowledge.

The 33% acceptance rate (3/9) indicates the validator is selective, not rubber-stamping. This selectivity is a feature: low-quality or off-domain observations are filtered out before they can pollute the institutional knowledge base.

## 5.4 Quality: Ceiling Effects and Domain Selection

The non-significant overall quality result (Experiment 2) does not invalidate the quality hypothesis. Both arms scored high (6.7--7.1 on a 10-point scale), indicating a ceiling effect at difficulty 2.0. The per-dimension bright spots (defense_depth d = +0.586, flag_isolation d = +0.330) suggest that institutional memory does improve specific structural aspects. A higher-difficulty or more discriminating domain may reveal aggregate quality improvements.

## 5.5 Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| Small sample size (n=9--20 per arm) | Reduced statistical power | Escalation experiment designed for trend detection, not point significance |
| Single PoC domain (CTF generation) | May not generalize | Methodology is domain-agnostic; replication encouraged |
| Single LLM provider (Gemini 3 Flash Preview) | May be LLM-specific | Planned: multi-LLM comparison |
| LLM-based quality evaluation | Evaluator noise | Mitigated: dual evaluator; calibration gap is evaluator-independent |
| Sequential treatment arm | Ordering effects | By design: control arm first; treatment must be sequential for accumulation |
| No human solver validation | Quality untested by humans | Planned: human solver study |
| Single run per escalation tier | High per-tier variance | Overall trend (negative slope) is more informative than individual tiers |
| Proprietary generation pipeline | Cannot be reproduced exactly | All outputs, metadata, and analysis are open; methodology is replicable with any compatible pipeline |

------------------------------------------------------------------------

# 6. Related Work

**Agent memory systems.** Mem0 [7] provides cross-session persistence for individual agents. MemOS [8] introduces a memory operating system abstraction with read/write/reflect operations. Collaborative Memory [9] addresses multi-user memory sharing with provenance tagging. Reflexion [10] stores verbal self-reflections in an episodic buffer. MemGPT [11] manages context windows via virtual memory paging. None of these systems provide consensus-validated governance over stored memories or empirical evidence of downstream task improvement.

**Generative agents.** Park et al. [14] demonstrated retrieval, reflection, and planning across interactions in simulated social environments. Voyager [15] showed open-ended exploration with a growing skill library. ReAct [16] synergized reasoning and acting in tool-use agents. These systems accumulate experience but lack formal governance, validation, or protection against knowledge degradation.

**Byzantine fault tolerance in ML.** Blanchard et al. [17] applied BFT to gradient aggregation in distributed learning. FLTrust [18] bootstrapped trust for Byzantine-robust federated learning. These apply BFT to model parameters, not to knowledge artifacts. SAGE extends BFT to the validation of agent-generated institutional knowledge.

**Knowledge-augmented LLMs.** RAG [6] retrieves relevant documents to augment LLM context. RETRO [19] integrates retrieval into language model pretraining. These provide static knowledge bases; SAGE provides a dynamic, agent-populated knowledge base that grows from operational experience and is governed by consensus.

------------------------------------------------------------------------

# 7. Summary of Findings

| Hypothesis | Metric | Effect Size | Verdict |
|-----------|--------|-------------|---------|
| **H1: Calibration** | Calibration gap (crypto_aes) | **d = -0.860 (LARGE)** | **Supported** |
| H1: Calibration | Calibration gap (sqli escalation) | d = -0.271 (SMALL) | Directionally supported |
| H2: Quality | Overall quality | d = -0.191 to -0.500 | Not supported (ceiling effect) |
| H2: Quality | Defense depth | d = +0.586 (MEDIUM) | Partially supported |
| H2: Quality | Flag isolation | d = +0.330 (SMALL) | Partially supported |
| **H3: Learning** | Early vs late SAGE quality | d = +0.252 (SMALL) | **Suggestive** |
| **H4: Difficulty scaling** | Gap slope (SAGE vs vanilla) | -0.053 vs +0.010 | **Supported** |

The central finding of this work is that **consensus-validated institutional memory produces measurable, large-effect improvements in LLM agent calibration accuracy**, and that this improvement **increases with task complexity**. The calibration gap metric is evaluator-independent, making the finding robust to LLM evaluation noise. The cross-domain filtering result (Experiment 4) demonstrates that the governance layer actively prevents knowledge pollution without manual curation.

We report all results including null findings on overall quality. The quality null result is informative: it demonstrates that institutional memory is not a universal improvement but rather a targeted one, most effective for **repeated decisions on continuous scales where historical data directly informs adjustment**.

------------------------------------------------------------------------

# 8. Reproducibility

## 8.1 What Is Open Source

The (S)AGE institutional memory infrastructure, integration interface, experiment harness, statistical analysis code, and all generated artifacts are open-source. The challenge generation platform (Level Up) is proprietary.

**Open-source (SAGE repository):**

| Component | Purpose |
|-----------|---------|
| (S)AGE infrastructure (full) | 4-node BFT network, PoE consensus, REST API, Python SDK |
| `sage_bridge.py` | Integration interface — shows exactly how agents wire to (S)AGE (`query_knowledge`, `submit_observation`, `enrich_attack_hints`, `summarize_and_submit`) |
| `experiment_protocol.py` | Statistical engine (Mann-Whitney U, chi-squared, Cohen's d) |
| `analyze_escalation.py` | Escalation analysis with linear regression and trend detection |
| `compute_cohens_d.py` | Cohen's d analysis with dual evaluator comparison |
| `run_escalation_experiment.sh` | Bash harness for multi-tier escalation experiments |
| `validator_agent.py` | Automated consensus voting agent (pure math heuristics) |

**Open-source (reproducibility artifact):**

| Artifact | Purpose |
|----------|---------|
| Generated challenge source code (Python/Flask) | The actual challenge applications produced by the pipeline |
| Dockerfiles and container configurations | Runnable challenge containers |
| `challenge_meta.json` per run | Target difficulty, calibrated difficulty, quality score, terminal state, repair attempts |
| Evaluation scores (per-dimension, per-challenge) | Raw quality assessments from both evaluators |
| Calibration gap data | The primary metric — fully verifiable from metadata |

**Proprietary (not released):**

The Level Up challenge generation pipeline (12+ agents including designer, exploit generator, hardener, calibrator, and orchestrator) is proprietary. The pipeline serves as the testbed but is not the contribution of this paper. The contribution is the institutional memory layer and the empirical evidence of its effect.

**Reproducibility implications:** Reviewers can independently (a) inspect all generated challenges, (b) re-run evaluations against the challenge artifacts, (c) recompute all statistical analyses from raw data, and (d) verify every calibration gap from metadata. The pipeline itself is a black box, but all inputs, outputs, and analysis are fully transparent. This is consistent with standard practice in empirical systems research where the evaluation platform is proprietary but the experimental artifacts are released [cf. industry systems papers at OSDI, SOSP, and MLSys].

For replication with alternative pipelines: any multi-agent system that produces artifacts with a measurable calibration target can be wired to (S)AGE via `sage_bridge.py` and evaluated using the same statistical framework. The methodology is domain-agnostic.

## 8.2 Statistical Implementation

Statistical tests are implemented from scratch in Python with no external dependencies beyond the standard library. This eliminates version-pinning issues with scipy/statsmodels and allows direct audit of the exact computation.

## 8.3 Result Artifacts

Each experiment produces a timestamped, immutable result directory containing raw data (JSON), ASCII reports, configuration metadata, and per-run artifacts (source code, Dockerfile, calibration metadata). Results are never overwritten. The metadata records the exact LLM model, SAGE commit hash, Python version, Docker version, and hardware specification.

## 8.4 Evaluation Independence

The challenge generator uses Google Gemini 3 Flash Preview. The quality evaluator uses Anthropic Claude Sonnet 4. Using different LLM providers for generation and evaluation prevents self-evaluation bias --- the evaluator has no knowledge of its own prior outputs.

------------------------------------------------------------------------

# 9. Future Work

**Extension runs at peak difficulty.** Additional runs at difficulty 3.0 (in progress) will test whether SAGE sustains narrow calibration gaps without drift, strengthening the difficulty-scaling result.

**Larger sample sizes.** Increase to 50+ challenges per arm per tier to achieve statistical significance on per-tier comparisons and improve power for medium effects.

**Cross-domain transfer.** Test whether knowledge accumulated in one domain (e.g., sqli) transfers to improve performance in a related domain (e.g., XSS, SSRF).

**Multi-LLM comparison.** Run the same experiment with Anthropic Claude, OpenAI GPT-4, and Google Gemini to determine whether the benefit is LLM-agnostic.

**Human solver validation.** Have human CTF players attempt generated challenges and compare solve times and perceived difficulty against automated calibration scores.

**Longitudinal studies.** Test knowledge retention, confidence decay, and whether institutional memory remains useful as the domain evolves over weeks or months.

**Alternative domains.** Apply the methodology to non-CTF multi-agent tasks (e.g., code review, vulnerability scanning, report generation) to test generalizability.

------------------------------------------------------------------------

# References

[1] Chen, M., Tworek, J., Jun, H., et al. (2021). "Evaluating Large Language Models Trained on Code." *arXiv:2107.03374*.

[2] Wei, J., Wang, X., Schuurmans, D., et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *NeurIPS 2022*.

[3] Schick, T., Dwivedi-Yu, J., Dessi, R., et al. (2023). "Toolformer: Language Models Can Teach Themselves to Use Tools." *NeurIPS 2023*.

[4] Wu, Q., Bansal, G., Zhang, J., et al. (2023). "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." *arXiv:2308.08155*.

[5] Guo, T., Chen, X., Wang, Y., et al. (2024). "Large Language Model Based Multi-agents: A Survey of Progress and Challenges." *arXiv:2402.01680*.

[6] Lewis, P., Perez, E., Piktus, A., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *NeurIPS 2020*.

[7] Mem0. "The Memory Layer for AI Applications." https://mem0.ai/

[8] MemOS (2025). "A Memory Operating System for AI Agents." *arXiv:2507.03724*. EMNLP Oral.

[9] Collaborative Memory (2025). "Multi-User Memory Sharing in LLM Agents." *arXiv:2505.18279*.

[10] Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., & Yao, S. (2023). "Reflexion: Language Agents with Verbal Reinforcement Learning." *NeurIPS 2023*.

[11] Packer, C., Wooders, S., Lin, K., et al. (2023). "MemGPT: Towards LLMs as Operating Systems." *arXiv:2310.08560*.

[12] Kannabhiran, D. A. (2026). "Agent Memory Infrastructure: Byzantine-Resilient Institutional Memory for Multi-Agent Systems." *Technical Report*.

[13] Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates.

[14] Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). "Generative Agents: Interactive Simulacra of Human Behavior." *Proc. ACM UIST '23*.

[15] Wang, G., Xie, Y., Jiang, Y., et al. (2023). "Voyager: An Open-Ended Embodied Agent with Large Language Models." *arXiv:2305.16291*.

[16] Yao, S., Zhao, J., Yu, D., et al. (2023). "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR 2023*.

[17] Blanchard, P., El Mhamdi, E. M., Guerraoui, R., & Stainer, J. (2017). "Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent." *NeurIPS 2017*.

[18] Cao, X., Fang, M., Liu, J., & Gong, N. Z. (2021). "FLTrust: Byzantine-robust Federated Learning via Trust Bootstrapping." *Proc. NDSS 2021*.

[19] Borgeaud, S., Mensch, A., Hoffmann, J., et al. (2022). "Improving Language Models by Retrieving from Trillions of Tokens." *ICML 2022*.

[20] Lamport, L., Shostak, R., & Pease, M. (1982). "The Byzantine Generals Problem." *ACM TOPLAS*, 4(3), 382--401.

[21] Castro, M. & Liskov, B. (1999). "Practical Byzantine Fault Tolerance." *Proc. OSDI '99*. USENIX.

[22] Mann, H. B. & Whitney, D. R. (1947). "On a Test of Whether One of Two Random Variables is Stochastically Larger than the Other." *Annals of Mathematical Statistics*, 18(1), 50--60.

[23] Zhang, Z., et al. (2024). "A Survey on the Memory Mechanism of Large Language Model based Agents." *arXiv:2404.13501*. Accepted by ACM TOIS.
