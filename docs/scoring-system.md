# Momentum Scoring System

The **Momentum Scorer Engine** (`src/engine/scorer.py`) quantitatively assesses crypto tokens based on velocity, trading volume, buy pressure, liquidity depth, and token maturity.

> **Disclaimer**: The calculated Alpha Score represents **signal confidence based on quantitative heuristics**, not guaranteed financial return or price performance.

---

## 🧮 Scoring Formulation

The composite score is derived from six discrete heuristic dimensions, capped at 100 points, followed by a risk penalty deduction.

$$\text{MomentumScore} = S_{\text{age}} + S_{\text{volume}} + S_{\text{velocity}} + S_{\text{pressure}} + S_{\text{liquidity}} + S_{\text{social}}$$

$$\text{FinalScore} = \max\left(0, \min\left(100, \text{MomentumScore} - \text{RiskPenalty}\right)\right)$$

---

## 📊 Score Breakdown by Category

### 1. Token Age Score ($S_{\text{age}}$) - Max 25 Points
Rewards early token detection:

| Token Age ($\text{Minutes}$) | Points Allocated |
| :--- | :--- |
| $\le 10\text{ mins}$ | **+25 Points** |
| $\le 30\text{ mins}$ | **+20 Points** |
| $\le 60\text{ mins}$ | **+10 Points** |
| $> 60\text{ mins}$ | **0 Points** (Filtered out if $\text{age} > \text{MAX\_AGE\_MINUTES}$) |

### 2. Trading Volume Score ($S_{\text{volume}}$) - Max 20 Points
Evaluates 1-hour trading volume depth:

| 1-Hour Volume ($\text{USD}$) | Points Allocated |
| :--- | :--- |
| $\ge \$100,000$ | **+20 Points** |
| $\ge \$50,000$ | **+15 Points** |
| $\ge \$20,000$ | **+10 Points** |
| $< \$20,000$ | **0 Points** |

### 3. Momentum Velocity Score ($S_{\text{velocity}}$) - Max 30 Points
Measures Volume Per Minute ($\text{VPM}$), indicating rapid accumulation:

$$\text{VPM} = \frac{\text{Volume}_{h1}}{\max(\text{Age}_{\text{minutes}}, 1)}$$

| Volume Per Minute ($\text{VPM}$) | Points Allocated |
| :--- | :--- |
| $\ge \$5,000\text{ / min}$ | **+30 Points** |
| $\ge \$3,000\text{ / min}$ | **+25 Points** |
| $\ge \$2,000\text{ / min}$ | **+20 Points** |
| $\ge \$1,000\text{ / min}$ | **+10 Points** |
| $< \$1,000\text{ / min}$ | **0 Points** |

### 4. Buy Pressure Ratio ($S_{\text{pressure}}$) - Max 20 Points
Compares buy orders versus sell orders over the last hour:

$$\text{Ratio} = \begin{cases} 
\frac{\text{Buys}_{h1}}{\text{Sells}_{h1}} & \text{if } \text{Sells}_{h1} > 0 \\ 
\text{Buys}_{h1} & \text{if } \text{Sells}_{h1} = 0 
\end{cases}$$

| Buy / Sell Ratio | Points Allocated |
| :--- | :--- |
| $\ge 2.0$ | **+20 Points** |
| $\ge 1.5$ | **+15 Points** |
| $\ge 1.2$ | **+10 Points** |
| $< 1.2$ | **0 Points** |

### 5. Liquidity Depth Bonus ($S_{\text{liquidity}}$) - Max 10 Points
Rewards deep liquidity pools reducing slippage risks:

| Liquidity Pool USD ($LP$) | Points Allocated |
| :--- | :--- |
| $\ge \$20,000$ | **+10 Points** |
| $\ge \$10,000$ | **+5 Points** |
| $< \$10,000$ | **0 Points** |

### 6. Social Presence Bonus ($S_{\text{social}}$) - Max 5 Points
* $+5\text{ Points}$ if token profile lists 2 or more verified social links (e.g. Website, Twitter/X, Telegram).

---

## 🛡️ Risk Penalty Adjustment

If the token's calculated `risk_score` exceeds 20 points, a proportional penalty is deducted:

$$\text{RiskPenalty} = \max\left(0, \lfloor (\text{RiskScore} - 20) \times 0.5 \rfloor \right)$$

---

## 🎯 Signal Tiers

| Tier Name | Score Range | Icon | Telegram Header | Description |
| :--- | :--- | :--- | :--- | :--- |
| **ALPHA_SIGNAL** | $\ge 70$ | 🔥 | `🔥 ALPHA SIGNAL` | Exceptional momentum, rapid volume velocity, and high buy pressure. |
| **EARLY_SIGNAL** | $55 - 69$ | 🚀 | `🚀 EARLY SIGNAL` | Emerging momentum with healthy liquidity and positive buy pressure. |
| **WATCHLIST** | $40 - 54$ | 👀 | `👀 WATCHLIST` | Early volume accumulation; requires observation. |
| **DISCARDED** | $< 40$ | ❌ | *(No Alert)* | Below qualification threshold. |
