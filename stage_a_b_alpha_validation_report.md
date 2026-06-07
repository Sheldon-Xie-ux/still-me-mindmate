# Weak Accumulation Alpha Validation Report

## Scope

This report combines:

- Phase A: cost-pressure validation on the best segmented baseline strategies
- Phase B: behavioral second-layer confirmation using trade-level data

The goal is to answer:

1. Does the current segmented baseline alpha survive realistic trading costs?
2. Can behavioral confirmation amplify that alpha inside high-quality market structure?

## Baseline Segments Under Review

The baseline strategy is unchanged:

- `accumulation_weak`
- segment-specific focus:
  - `liquidity_top_20`
  - `activity_top_20`
  - `liquidity_top_20 ∩ activity_top_20`

Best baseline parameter region used:

- `volume_ratio = 1.2`
- `price_change_threshold = 0.03`
- `impact_z = -0.5`

## Phase A: Cost Pressure Test

Flat round-trip cost sensitivity tested at:

- `0 bps`
- `5 bps`
- `10 bps`
- `15 bps`
- `20 bps`
- `30 bps`

### Phase A Results

#### 1. High-Liquidity Segment

- `expectancy @ 0 bps = 0.001101`
- `expectancy @ 10 bps = 0.000101`
- `expectancy @ 20 bps = -0.000899`
- survives `10 bps`: `yes`
- survives `20 bps`: `no`

#### 2. High-Activity Segment

- `expectancy @ 0 bps = 0.001045`
- `expectancy @ 10 bps = 0.000045`
- `expectancy @ 20 bps = -0.000955`
- survives `10 bps`: `yes`
- survives `20 bps`: `no`

#### 3. High-Liquidity ∩ High-Activity

- `expectancy @ 0 bps = 0.001063`
- `expectancy @ 10 bps = 0.000063`
- `expectancy @ 20 bps = -0.000937`
- survives `10 bps`: `yes`
- survives `20 bps`: `no`

### Phase A Conclusion

The segmented baseline alpha does survive `10 bps`, but only marginally.

It does **not** survive `20 bps` in any of the three target segments.

Interpretation:

- baseline alpha still has some economic meaning
- but that economic meaning is thin
- without better execution or stronger confirmation, the edge is fragile

## Phase B: Behavioral Confirmation

Behavioral confirmation used trade-level data extracted from the same historical window.

Trade-level source fields available:

- `timestamp`
- `market_id`
- `price`
- `usd_amount`
- `side`
- `maker`
- `taker`

Behavioral features used:

- `large_trade_share`
  - concentration of the top trades inside recent trade flow
- `trade_burst_ratio`
  - short-horizon trade-count burst relative to recent baseline
- `buy_volume_share`
  - repeated directional buy pressure

The first-layer baseline signal was kept fixed.

Phase B only scanned behavioral thresholds on top of the segmented baseline.

Cost-adjusted comparison uses the `10 bps` checkpoint because Phase A showed that this is the key economic survival boundary.

### Phase B Results

#### 1. High-Liquidity Segment

Best behavioral row:

- `large_trade_share = 0.7`
- `trade_burst_ratio = 2.0`
- `buy_volume_share = 0.55`
- `trade_count = 3061`
- `expectancy = 0.002181`
- `sharpe_ratio = 4.625964`
- `cost_adjusted_expectancy @ 10 bps = 0.001181`
- better than baseline: `yes`

Baseline comparison:

- baseline `cost_adjusted_expectancy @ 10 bps = 0.000101`

#### 2. High-Activity Segment

Best behavioral row:

- `large_trade_share = 0.7`
- `trade_burst_ratio = 1.5`
- `buy_volume_share = 0.55`
- `trade_count = 2875`
- `expectancy = 0.001408`
- `sharpe_ratio = 3.072809`
- `cost_adjusted_expectancy @ 10 bps = 0.000408`
- better than baseline: `yes`

Baseline comparison:

- baseline `cost_adjusted_expectancy @ 10 bps = 0.000045`

#### 3. High-Liquidity ∩ High-Activity

Best behavioral row:

- `large_trade_share = 0.7`
- `trade_burst_ratio = 1.5`
- `buy_volume_share = 0.65`
- `trade_count = 1864`
- `expectancy = 0.001529`
- `sharpe_ratio = 2.556741`
- `cost_adjusted_expectancy @ 10 bps = 0.000529`
- better than baseline: `yes`

Baseline comparison:

- baseline `cost_adjusted_expectancy @ 10 bps = 0.000063`

### Phase B Conclusion

Behavioral confirmation does appear to amplify the weak baseline alpha.

This is not a marginal improvement:

- high-liquidity: `0.000101 -> 0.001181`
- high-activity: `0.000045 -> 0.000408`
- intersection: `0.000063 -> 0.000529`

The strongest pattern is:

- high large-trade concentration
- elevated short-horizon trade burstiness
- buy-side dominance

This suggests the baseline weak accumulation signal becomes much more economically meaningful when it is aligned with real behavior in the underlying trade flow.

## Final Answers

### 1. Does the current baseline alpha still have economic meaning under realistic cost?

Yes, but only weakly.

All three target segments survive `10 bps`, but none survive `20 bps`.

So the baseline alpha is real enough to keep studying, but fragile enough that it should not be considered production-ready without stronger confirmation.

### 2. Does behavioral confirmation truly amplify alpha?

Yes.

In all three target segments, the best behavioral-confirmed strategy outperforms the segmented baseline on:

- raw expectancy
- `10 bps` cost-adjusted expectancy
- sharpe ratio

The improvement is strongest in `liquidity_top_20`, but it is also clearly present in:

- `activity_top_20`
- `liquidity_top_20 ∩ activity_top_20`

## Recommended Next Step

The next most valuable step is no longer “keep tuning state filters.”

It is:

- validate the behavioral confirmation out-of-sample
- test stricter execution assumptions
- inspect whether the behavioral alpha is concentrated in specific event types or market categories

## Output Files

Phase A:

- `data/real/cost_pressure/cost_pressure_summary.csv`
- `data/real/cost_pressure/liquidity_top_20_cost_sensitivity.csv`
- `data/real/cost_pressure/activity_top_20_cost_sensitivity.csv`
- `data/real/cost_pressure/liquidity_top_20_activity_top_20_cost_sensitivity.csv`

Phase B:

- `data/real/hf_quant_sep_oct_2025_top_segments_trades.parquet`
- `data/real/behavioral_confirmation/behavioral_summary.csv`
- `data/real/behavioral_confirmation/liquidity_top_20_behavioral_top_results.csv`
- `data/real/behavioral_confirmation/activity_top_20_behavioral_top_results.csv`
- `data/real/behavioral_confirmation/liquidity_top_20_activity_top_20_behavioral_top_results.csv`
