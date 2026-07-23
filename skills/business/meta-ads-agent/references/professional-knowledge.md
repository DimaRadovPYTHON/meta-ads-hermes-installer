# Meta Ads Professional Knowledge Base

> Compiled for the Hermes Meta Ads Agent
> Sources: Ryze AI, Benly.ai, 1ClickReport, Meta for Developers

---

## 1. META'S AUCTION SYSTEM

**Total Value = Bid × Estimated Action Rate + Ad Quality**

Three factors determine who wins every auction:
- **Bid Amount** — What you're willing to pay for the desired action
- **Estimated Action Rate** — Meta predicts how likely each user is to convert based on 500+ behavioral signals (purchase history, device, time on platform, interaction patterns, lookalike models)
- **Quality Score** — Based on ad relevance, expected positive/negative feedback, and post-click experience. Poor landing pages reduce quality score by 15-40%

The highest monetary bid does NOT always win. Lower bids with excellent creative can outperform aggressive bids with poor ads. Successful advertisers focus 60% on creative/targeting and 40% on bidding.

---

## 2. THE 7 BIDDING STRATEGIES (2026)

### Lowest Cost (Highest Volume)
- **Best For:** New campaigns, audience testing, creative validation, <50 conversions/week
- **Avoid:** Predictable costs needed, scaling mature campaigns, strict CPA targets
- **Results:** Fastest data collection, 20-40% cost variation, maximum volume

### Cost Cap
- **Best For:** Scaling campaigns, lead generation, e-commerce with known LTV
- **Best Used:** Set 10-20% above your baseline CPA from Lowest Cost testing
- **Results:** 10-15% cost variation, stable delivery, easier budget planning

### Bid Cap
- **Best For:** Strict budget limits, competitive industries, strong historical data
- **Warning:** Severely limits delivery, can keep campaigns in learning phase indefinitely
- **Results:** Lowest cost variance but potential delivery limitations

### Minimum ROAS
- **Best For:** E-commerce with varied prices, catalog sales, 100+ conversions/week
- **Setup:** Calculate break-even ROAS = 1 / Profit Margin. Start 10-20% above current ROAS
- **Results:** Higher revenue per conversion, fewer total conversions, better profit margins

### Advantage+ Automated
- **Best For:** Large budgets ($5K+/mo), mature accounts, hands-off management
- **Results:** 15-30% efficiency improvement, reduced management time

### Target Cost
- **Best For:** Financial services, high-value B2B leads, precise budget planning
- **Results:** Highly predictable costs, potentially slower delivery

### Maximum Delivery
- **Best For:** Product launches, crisis communication, brand awareness pushes
- **Avoid:** Performance marketing, lead generation, ongoing campaigns

---

## 3. THE 90-DAY PROGRESSION PATH

### Phase 1: Days 1-21 — Lowest Cost (Data Collection)
- Budget $20-100/day per ad set
- Goal: 25-50 conversions per ad set
- Test 3-5 audience segments
- **Week 1-2:** Achieve 25+ conversions per ad set, test audiences, validate creative
- **Week 3:** Pause audiences with CPA > 2x target, increase budget on winners by 20-50%

### Phase 2: Days 22-60 — Cost Cap (Scaling)
- Set Cost Cap at 110% of baseline CPA
- **Weeks 4-6:** Scale budgets 25% weekly, expand to similar audiences
- **Weeks 7-8:** Lower Cost Cap 5-10% if stable, launch lookalike audiences, refresh creative

### Phase 3: Days 61-90 — Advanced (Optimization)
- **E-commerce:** Test Minimum ROAS bidding, optimize for revenue
- **Lead Gen:** Implement Bid Cap for cost control
- **Large Budgets:** Leverage Advantage+ automation

---

## 4. BUDGET SCALING RULES

- **Never increase budget >50% in a single day** — resets Meta's learning phase
- **Scale winning campaigns:** 20-25% every 3-4 days when CPA stays stable
- Example: $100/day → $125 → $150 → $188 over 2 weeks (not directly to $300)
- Cost Cap provides a natural safeguard during scaling — budget that can't spend efficiently simply won't spend (correct behavior)

---

## 5. LEARNING PHASE MANAGEMENT

- Meta requires **50 optimization events** (conversions) within **7 days** to exit learning
- Campaigns stuck in learning see **20-40% higher CPAs**
- **Do NOT** change bid strategy, adjust caps >20%, modify targeting, or alter creative during learning
- If learning exceeds 14 days: consolidate ad sets or simplify targeting
- Lowest Cost exits learning fastest (maximum algorithm flexibility)
- Restrictive strategies (Bid Cap, aggressive Cost Cap) can keep campaigns in learning indefinitely

---

## 6. CREATIVE FATIGUE DETECTION

- **Threshold:** Frequency > 3.5 AND CTR drop > 25% from previous 7-day period
- **Action:** Pause ad set, flag for creative rotation
- High-performing creatives typically last **14-21 days** before fatigue
- Launch **3-4 new creative variations** every 2 weeks
- Ad creative fatigue increases CPA by 30-70% as frequency rises above 3.0
- The ad library/ad level is the right level for fatigue detection (not campaign)

---

## 7. META VALUE RULES

### What They Are
Bid multipliers for specific audience segments without restricting audience size. Available for Sales and App Promotion campaigns only.

### Criteria (choose up to 2 per rule)
- Age range (13-17, 18-24, 25-34, 35-44, 45-54, 55-64, 65+)
- Gender
- Location (country, state, city, postal code)
- Mobile OS (iOS, Android)
- Placement (Feed, Stories, Reels, Audience Network, Messenger)

### Range
- Bid decrease: down to 90% (bid 10% of base)
- Bid increase: up to 1,000% (10x base bid)
- Max 10 rules per campaign

### Best Practices
1. **Start with decreases, not increases** — decrease bids for low-value segments first, free budget for algorithm to reallocate naturally
2. **Order rules from most specific to least specific** — only the FIRST matching rule applies
3. **Requires 50+ conversions/week** minimum
4. **Need 20%+ ROAS variance** between segments for rules to matter
5. **Test one variable at a time** — geo week 1, age week 2, device week 3
6. **Allow 7-14 day learning period** — do not change in first week
7. **Use 20-30% adjustments first**, not 100%+

### DTC 4-Tier Template
| Tier | Definition | Bid Multiplier |
|------|-----------|---------------|
| Top 10% LTV | Past purchasers, 12mo LTV top decile | 2.5x |
| Repeat buyers | 2+ orders all-time | 1.8x |
| High-AOV first-time | First order > 1.5x mean AOV | 1.4x |
| Discount-heavy buyers | Orders only on >25% off | 0.6x |

### Common Mistakes
- Setting value rules without value-based optimisation — Meta ignores them without VBO
- Bidding up everything — half should be neutral or down-bid
- Stale audience definitions — refresh custom audiences quarterly
- Over-segmentation — 8+ rules turns into chaos, max 4 recommended
- No CAPI for value events — Pixel-only gives Meta garbage AOV data
- Ignoring the lift report — check at Day 14, if lift < 10%, revert

---

## 8. KEY METRICS & FORMULAS

| Metric | Formula | Notes |
|--------|---------|-------|
| ROAS | Revenue / Ad Spend | Track blended, not Meta-reported |
| Break-even ROAS | 1 / Profit Margin | 25% margin = 4x break-even |
| CPA | Total Spend / Total Conversions | Also called cost per result |
| CTR | (Clicks / Impressions) × 100 | Measures creative engagement |
| Frequency | Impressions / Reach | Above 3.5 = fatigue risk |
| CPM | (Total Spend / Impressions) × 1000 | Cost per 1000 impressions |

- **Blended ROAS** accounts for all attribution windows
- **Meta-reported ROAS undercounts by 20-40%** — always track blended
- **7-day click, 1-day view attribution** captures 85-90% of conversions (default)
- **Q4 CPMs:** 60% higher than average
- **Jan-Feb CPMs:** 25% lower than average

---

## 9. ALERT CONDITIONS

| Condition | Severity | Action |
|-----------|----------|--------|
| CPA > 2x target | Critical | Alert + auto-pause (if enabled) |
| ROAS < 50% of target | Critical | Alert + review campaign |
| Frequency > 3.5 on winning ad | Warning | Alert + suggest creative rotation |
| Spend > 80% daily budget before 6pm | Info | Alert to monitor |
| Campaign in learning limited 7+ days | Warning | Alert to simplify targeting |
| CTR drop > 25% from previous 7 days | Warning | Alert + creative fatigue check |

---

## 10. COMMON MISTAKES

1. **Changing bids too frequently** — Wait 7 days minimum between changes. Frequent changes increase CPA by 40-60%
2. **Setting unrealistic Cost Caps** — 50% below baseline prevents delivery. Start 10-15% above baseline
3. **Ignoring learning phase** — Each significant edit resets 7-14 days of optimization
4. **Wrong strategy for objective** — Using ROAS Target when all conversions have equal value
5. **No baseline data** — Setting Cost Cap without knowing actual CPA first
6. **Budget-cap mismatch** — Small budget + restrictive caps prevents learning
7. **Overlapping audiences** — Multiple campaigns targeting the same audience cannibalize each other
8. **Scaling too fast** — >50% daily budget increase destroys stable campaigns

---

## 11. DELIVERY & REPORTING FORMAT

### Daily Report Structure
1. **Spend vs Budget** — Total spend today, remaining budget
2. **Campaign Performance** — Per-campaign: ROAS, CPA, CTR, conversions, spend
3. **Ad Set Changes** — What was paused/scaled and why
4. **Creative Fatigue** — Which creatives need rotation
5. **Alerts** — Any threshold breaches
6. **Recommendations** — What to do tomorrow

### Cron Schedule
- Every 15 min: Campaign health check (spend, CPA, ROAS, frequency, fatigue)
- Daily 9am: Full performance report
- Instant: Threshold breach alerts
