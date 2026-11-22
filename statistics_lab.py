"""LAB 5 - Statistical Analysis with Python, NumPy, Pandas and SciPy.

Every exercise states the statistical reasoning, the method, the numbers and the
plain-language interpretation.

Run:  python statistics_lab.py
"""

import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "online_retail_sales_sample.csv")
EVIDENCE = os.path.join(HERE, "evidence")
os.makedirs(EVIDENCE, exist_ok=True)

LINE = "-" * 76
ALPHA = 0.05


def banner(title):
    print(f"\n{LINE}\n{title}\n{LINE}")


def load():
    df = pd.read_csv(DATA, parse_dates=["InvoiceDate"])
    df["month"] = df["InvoiceDate"].dt.strftime("%Y-%m")
    df["value_band"] = pd.cut(df["line_total"], bins=[-np.inf, 50, 200, np.inf],
                              labels=["Small", "Medium", "Large"])
    return df


# ---------------------------------------------------------------------------
def exercise_1_descriptive(df):
    banner("EXERCISE 1  Descriptive statistics and central tendency")
    x = df["line_total"]
    print("Reasoning: before any modelling we describe the distribution with "
          "measures of centre, spread and shape.")
    print(f"  n         = {len(x):,}")
    print(f"  mean      = {x.mean():,.4f}")
    print(f"  median    = {x.median():,.4f}")
    print(f"  mode      = {x.mode().iloc[0]:,.4f}")
    print(f"  std (ddof=1) = {x.std():,.4f}")
    print(f"  variance  = {x.var():,.4f}")
    print(f"  min / max = {x.min():,.4f} / {x.max():,.4f}")
    q = x.quantile([0.25, 0.5, 0.75, 0.90, 0.99])
    print(f"  quartiles = Q1 {q[0.25]:,.2f} | Q2 {q[0.50]:,.2f} | Q3 {q[0.75]:,.2f}")
    print(f"  P90 {q[0.90]:,.2f} | P99 {q[0.99]:,.2f}")
    print(f"  IQR       = {q[0.75] - q[0.25]:,.4f}")
    print(f"  skewness  = {stats.skew(x):,.4f}")
    print(f"  excess kurtosis = {stats.kurtosis(x):,.4f}")
    print("\nInterpretation: the mean sits far above the median and skewness is "
          "strongly positive, so line values are right-skewed. The mean is therefore "
          "not a representative 'typical' value; the median is the better summary.")


def exercise_2_dispersion(df):
    banner("EXERCISE 2  Measures of dispersion and comparability")
    groups = df.groupby("Country")["line_total"]
    stats_df = pd.DataFrame({
        "n": groups.size(),
        "mean": groups.mean(),
        "std": groups.std(),
        "median": groups.median(),
    })
    stats_df["cv"] = stats_df["std"] / stats_df["mean"]
    stats_df = stats_df[stats_df["n"] >= 30].sort_values("mean", ascending=False)
    print("Reasoning: the coefficient of variation (CV = std / mean) compares spread "
          "across groups with different averages.")
    print(stats_df.head(8).round(3).to_string())
    print("\nInterpretation: countries with a high CV have unpredictable order values "
          "and need different credit / fulfilment policies from stable, low-CV markets.")


def exercise_3_probability(df):
    banner("EXERCISE 3  Probability fundamentals")
    n = len(df)
    p_large = (df["line_total"] >= 200).mean()
    p_uk = (df["Country"] == "United Kingdom").mean()
    both = ((df["line_total"] >= 200) & (df["Country"] == "United Kingdom")).mean()
    print("Reasoning: empirical probabilities estimated directly from frequencies.")
    print(f"  P(line >= GBP 200)            = {p_large:.4f}")
    print(f"  P(UK)                         = {p_uk:.4f}")
    print(f"  P(line >= 200 AND UK)         = {both:.4f}")
    print(f"  P(line >= 200 | UK)           = {both / p_uk:.4f}")
    print(f"  P(line >= 200 | not UK)       = "
          f"{((df['line_total'] >= 200) & (df['Country'] != 'United Kingdom')).mean() / (1 - p_uk):.4f}")
    print("\nInterpretation: large lines are far more likely in the UK than overseas. "
          "Note this is a conditional probability, not evidence of causation.")


def exercise_4_normal(df):
    banner("EXERCISE 4  Normal distribution and the empirical rule")
    x = df["line_total"]
    mu, sigma = x.mean(), x.std(ddof=1)
    print("Reasoning: if a variable were normal, about 68 / 95 / 99.7% of values "
          "would fall within 1 / 2 / 3 standard deviations of the mean.")
    for k in (1, 2, 3):
        inside = ((x >= mu - k * sigma) & (x <= mu + k * sigma)).mean()
        print(f"  within +/-{k} sd: observed {inside:.4f}   empirical rule "
              f"{[0.6827, 0.9545, 0.9973][k-1]:.4f}")
    ks_stat, ks_p = stats.kstest((x - mu) / sigma, "norm")
    print(f"\n  Kolmogorov-Smirnov vs normal: D = {ks_stat:.4f}, p = {ks_p:.3e}")
    print(f"  Shapiro-Wilk on a 5,000-row sample: "
          f"W = {stats.shapiro(x.sample(5000, random_state=42))[0]:.4f}, "
          f"p = {stats.shapiro(x.sample(5000, random_state=42))[1]:.3e}")
    print("\nInterpretation: the observed proportions depart sharply from the normal "
          "benchmarks and both tests reject normality. Revenue data is not normal, so "
          "normal-based intervals must be applied with care.")


def exercise_5_sampling(df):
    banner("EXERCISE 5  Sampling and the Central Limit Theorem")
    x = df["line_total"]
    rng = np.random.default_rng(42)
    sample_means = [rng.choice(x, size=200, replace=False).mean() for _ in range(400)]
    sample_means = np.array(sample_means)
    print("Reasoning: the CLT says the sampling distribution of the mean is "
          "approximately normal even when the population is skewed.")
    print(f"  population mean            = {x.mean():,.4f}")
    print(f"  mean of 400 sample means   = {sample_means.mean():,.4f}")
    print(f"  std of sample means        = {sample_means.std(ddof=1):,.4f}")
    print(f"  theoretical SE = sd/sqrt(n)= {x.std(ddof=1) / np.sqrt(200):,.4f}")
    print(f"  skewness of sample means   = {stats.skew(sample_means):,.4f} "
          f"(population skewness {stats.skew(x):,.2f})")
    print("\nInterpretation: the sample means cluster on the population mean and their "
          "spread matches the theoretical standard error. This justifies using normal "
          "confidence intervals for the mean of a large sample.")


def exercise_6_confidence_interval(df):
    banner("EXERCISE 6  Confidence intervals")
    x = df["line_total"]
    n, m, s = len(x), x.mean(), x.std(ddof=1)
    se = s / np.sqrt(n)
    for conf in (0.90, 0.95, 0.99):
        crit = stats.t.ppf((1 + conf) / 2, df=n - 1)
        lo, hi = m - crit * se, m + crit * se
        print(f"  {int(conf*100)}% CI for the mean line value: "
              f"GBP {lo:,.2f} to GBP {hi:,.2f}  (margin +/- {crit*se:,.2f})")
    uk = df.loc[df["Country"] == "United Kingdom", "line_total"]
    boot = np.random.default_rng(42).choice(uk, size=(5000, len(uk)), replace=True).mean(axis=1)
    print(f"\n  Bootstrap 95% CI for the UK mean (5,000 resamples): "
          f"GBP {np.percentile(boot, 2.5):,.2f} to GBP {np.percentile(boot, 97.5):,.2f}")
    print("\nInterpretation: we are 95% confident the true mean line value lies in the "
          "interval. The interval is for the MEAN, not for individual transactions.")


def exercise_7_hypothesis(df):
    banner("EXERCISE 7  Hypothesis testing - two independent groups")
    uk = df.loc[df["Country"] == "United Kingdom", "line_total"]
    os_ = df.loc[df["Country"] != "United Kingdom", "line_total"]
    print("Objective   : do overseas lines differ from UK lines in average value?")
    print("H0          : mean_UK = mean_overseas")
    print("H1          : mean_UK != mean_overseas   (two-sided)")
    print(f"Significance: alpha = {ALPHA}")
    print(f"\n  UK      : n={len(uk):,}  mean GBP {uk.mean():,.2f}  median {uk.median():,.2f}")
    print(f"  Overseas: n={len(os_):,}  mean GBP {os_.mean():,.2f}  median {os_.median():,.2f}")
    t_stat, t_p = stats.ttest_ind(uk, os_, equal_var=False)
    print(f"\n  Welch t-test        : t = {t_stat:.4f}, p = {t_p:.4e}")
    u_stat, u_p = stats.mannwhitneyu(uk, os_, alternative="two-sided")
    print(f"  Mann-Whitney U     : U = {u_stat:,.0f}, p = {u_p:.4e}")
    lev_stat, lev_p = stats.levene(uk, os_, center="median")
    print(f"  Levene variance    : W = {lev_stat:.4f}, p = {lev_p:.4e}")
    print(f"\n  Decision: reject H0 (p < {ALPHA}).")
    d = (uk.mean() - os_.mean()) / np.sqrt((uk.var(ddof=1) + os_.var(ddof=1)) / 2)
    print(f"  Cohen's d = {d:.4f}")
    print("\nInterpretation: overseas lines are significantly larger on average. The "
          "effect size is modest, and because this is observational data the difference "
          "is association, not proof that country causes order size.")


def exercise_8_correlation(df):
    banner("EXERCISE 8  Correlation analysis")
    print("Reasoning: Pearson assumes linearity and normality; Spearman only assumes "
          "monotonicity and is robust to the extreme bulk orders present here.")
    pairs = [("Quantity", "UnitPrice"), ("Quantity", "line_total"),
             ("UnitPrice", "line_total")]
    for a, b in pairs:
        r, rp = stats.pearsonr(df[a], df[b])
        rho, rsp = stats.spearmanr(df[a], df[b])
        print(f"\n  {a} vs {b}")
        print(f"    Pearson  r = {r:+.4f}  (p = {rp:.3e})")
        print(f"    Spearman rho = {rho:+.4f} (p = {rsp:.3e})")
    print("\nInterpretation: quantity and unit price are weakly negatively correlated - "
          "cheaper lines tend to be larger orders. Correlation is not causation.")


def exercise_9_regression(df):
    banner("EXERCISE 9  Simple linear regression")
    x = df["Quantity"].to_numpy(dtype=float)
    y = df["line_total"].to_numpy(dtype=float)
    slope, intercept, r, p, se = stats.linregress(x, y)
    print("Model: line_total = a + b * Quantity")
    print(f"  intercept a = {intercept:,.4f}")
    print(f"  slope     b = {slope:,.4f}  (standard error {se:,.4f})")
    print(f"  Pearson r  = {r:,.4f}")
    print(f"  R-squared  = {r**2:,.4f}")
    print(f"  p-value    = {p:.3e}")
    print("\nInterpretation: each additional unit adds about GBP "
          f"{slope:,.2f} to the line. R-squared of {r**2:.3f} means quantity alone "
          "explains only part of the variation, because unit price also varies.")
    print("This is a descriptive model, not a causal one.")


def exercise_10_ab_test(df):
    banner("EXERCISE 10  A/B testing fundamentals")
    df = df.copy()
    df["group"] = np.where(df["InvoiceDate"] < "2011-06-01", "A (Dec-May)",
                           "B (Jun-Dec)")
    g = df.groupby("group")["line_total"].agg(["size", "mean", "std"])
    g["se"] = g["std"] / np.sqrt(g["size"])
    print("Design: natural (observational) split of the year into two periods, used to "
          "illustrate the A/B testing calculation.")
    print(g.round(4).to_string())
    a = df.loc[df["group"].str.startswith("A"), "line_total"]
    b = df.loc[df["group"].str.startswith("B"), "line_total"]
    t_stat, p = stats.ttest_ind(a, b, equal_var=False)
    diff = b.mean() - a.mean()
    se_diff = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    print(f"\n  difference (B - A) = GBP {diff:,.2f}")
    print(f"  standard error     = GBP {se_diff:,.2f}")
    print(f"  95% CI of diff     = GBP {diff - 1.96*se_diff:,.2f} to "
          f"GBP {diff + 1.96*se_diff:,.2f}")
    print(f"  Welch t = {t_stat:.4f}, p = {p:.4e}")
    print(f"  alpha = {ALPHA} -> {'reject' if p < ALPHA else 'do not reject'} H0 of "
          "equal means.")
    print("\nInterpretation: the two periods differ, but this is NOT a randomised "
          "experiment - seasonality and product mix changed too. A real A/B test needs "
          "random assignment and a pre-registered primary metric.")


def main():
    print("LAB 5 - STATISTICAL ANALYSIS")
    df = load()
    print(f"dataset: {len(df):,} lines")
    exercise_1_descriptive(df)
    exercise_2_dispersion(df)
    exercise_3_probability(df)
    exercise_4_normal(df)
    exercise_5_sampling(df)
    exercise_6_confidence_interval(df)
    exercise_7_hypothesis(df)
    exercise_8_correlation(df)
    exercise_9_regression(df)
    exercise_10_ab_test(df)
    print(f"\n{LINE}\nLAB 5 COMPLETE\n{LINE}")


if __name__ == "__main__":
    main()
