"""LAB 9 - Introductory Machine Learning with scikit-learn.

Optional Data-Science extension to the core Data Analyst toolkit.

Pipeline
--------
1. Preprocessing        - train/test split, scaling, one-hot encoding
2. Feature selection    - univariate correlation + tree-based importance
3. Regression           - linear regression, evaluated with RMSE / MAE / R2
4. Classification       - logistic regression and a decision tree
5. Evaluation           - accuracy, precision, recall, F1, confusion matrix
6. Overfitting          - train vs test gap, pruning the tree

Run:  python ml_lab.py
"""

import os
import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, mean_absolute_error, mean_squared_error,
                             precision_score, r2_score, recall_score, roc_auc_score)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "online_retail_sales_sample.csv")
EVIDENCE = os.path.join(HERE, "evidence")
os.makedirs(EVIDENCE, exist_ok=True)

RANDOM_STATE = 42
LINE = "-" * 76


def banner(t):
    print(f"\n{LINE}\n{t}\n{LINE}")


def load():
    df = pd.read_csv(DATA, parse_dates=["InvoiceDate"])
    df["month"] = df["InvoiceDate"].dt.strftime("%Y-%m")
    df["high_value"] = (df["line_total"] >= 50).astype(int)
    df = df.dropna(subset=["CustomerID"])
    return df


# ---------------------------------------------------------------------------
def exercise_1_preprocessing(df):
    banner("EXERCISE 1  Preprocessing and the train/test split")
    numeric = ["Quantity", "UnitPrice", "CustomerID"]
    categorical = ["Country", "month"]

    X = df[numeric + categorical]
    y_reg = df["line_total"]
    y_clf = df["high_value"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_reg, test_size=0.25, random_state=RANDOM_STATE)

    print("Reasoning: the model must be judged on data it has never seen, so the "
          "split happens before any fitting and is stratified by nothing here "
          "(regression). random_state makes it reproducible.")
    print(f"  full rows      : {len(X):,}")
    print(f"  training rows  : {len(X_train):,} ({len(X_train)/len(X):.0%})")
    print(f"  test rows      : {len(X_test):,} ({len(X_test)/len(X):.0%})")
    print(f"  numeric cols   : {numeric}")
    print(f"  categorical    : {categorical}")

    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
    ])
    print(f"\n  ColumnTransformer steps: {[n for n, _, _ in pre.transformers]}")
    return X, numeric, categorical, pre, y_reg, y_clf


def exercise_2_feature_selection(df, numeric):
    banner("EXERCISE 2  Feature selection")
    print("Reasoning: a feature that carries no signal about the target should be "
          "removed before modelling.")
    corr = df[numeric + ["line_total"]].corr(method="spearman")["line_total"].drop("line_total")
    print("\n  Spearman correlation with line_total:")
    for name, value in corr.sort_values(ascending=False).items():
        print(f"    {name:12s} {value:+.4f}")

    rf = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1)
    Xr = pd.get_dummies(df[numeric + ["Country", "month"]], drop_first=True)
    rf.fit(Xr, df["high_value"])
    imp = pd.Series(rf.feature_importances_, index=Xr.columns).sort_values(ascending=False)
    print("\n  Random-forest importance (top 8):")
    for name, value in imp.head(8).items():
        print(f"    {name:24s} {value:.4f}")
    print("\nInterpretation: quantity and unit price dominate, as expected - line "
          "value is their product. Country and month add a little signal.")


def exercise_3_regression(df, numeric, categorical, pre, y_reg):
    banner("EXERCISE 3  Linear regression")
    X = df[numeric + categorical]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_reg, test_size=0.25, random_state=RANDOM_STATE)

    model = Pipeline([("pre", pre), ("reg", LinearRegression())])
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, pred))
    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)
    print("Model: line_total ~ Quantity + UnitPrice + CustomerID + Country + month")
    print(f"  RMSE = {rmse:,.2f} GBP")
    print(f"  MAE  = {mae:,.2f} GBP")
    print(f"  R2   = {r2:.4f}")
    print("\nInterpretation: R2 measures the share of variance explained. Line value "
          "is quantity x price, a multiplicative relationship, so a linear model "
          "captures only part of it - exactly what the R2 shows.")


def exercise_4_classification(df, numeric, categorical, pre, y_clf):
    banner("EXERCISE 4  Logistic regression")
    X = df[numeric + categorical]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_clf, test_size=0.25, random_state=RANDOM_STATE, stratify=y_clf)

    print(f"  high-value rate: train {y_train.mean():.3f} | test {y_test.mean():.3f}")

    log = Pipeline([("pre", pre),
                    ("clf", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE))])
    log.fit(X_train, y_train)
    pred = log.predict(X_test)
    proba = log.predict_proba(X_test)[:, 1]

    dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
    print(f"\n  majority-class baseline accuracy = "
          f"{accuracy_score(y_test, dummy.predict(X_test)):.4f}   "
          f"(a model that always says 'not high-value')")
    print(f"  accuracy  = {accuracy_score(y_test, pred):.4f}")
    print(f"  precision = {precision_score(y_test, pred):.4f}")
    print(f"  recall    = {recall_score(y_test, pred):.4f}")
    print(f"  F1        = {f1_score(y_test, pred):.4f}")
    print(f"  ROC AUC   = {roc_auc_score(y_test, proba):.4f}")
    print("\n  confusion matrix (rows = actual, columns = predicted)")
    print("            not-high   high")
    cm = confusion_matrix(y_test, pred)
    print(f"  not-high  {cm[0,0]:8d} {cm[0,1]:5d}")
    print(f"  high      {cm[1,0]:8d} {cm[1,1]:5d}")
    print("\nInterpretation: precision answers 'of the lines we called high-value, how "
          "many were?'; recall answers 'of the truly high-value lines, how many did we "
          "catch?'. The two trade off.")


def exercise_5_tree_and_overfit(df, numeric, categorical, pre, y_clf):
    banner("EXERCISE 5  Decision tree and overfitting")
    X = df[numeric + categorical]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_clf, test_size=0.25, random_state=RANDOM_STATE, stratify=y_clf)

    rows = []
    for depth in (2, 4, 6, 10, None):
        tree = Pipeline([("pre", pre),
                         ("clf", DecisionTreeClassifier(max_depth=depth,
                                                       random_state=RANDOM_STATE))])
        tree.fit(X_train, y_train)
        train_acc = accuracy_score(y_train, tree.predict(X_train))
        test_acc = accuracy_score(y_test, tree.predict(X_test))
        gap = train_acc - test_acc
        rows.append((depth, train_acc, test_acc, gap))
        print(f"  max_depth={str(depth):4s}  train {train_acc:.4f}  test {test_acc:.4f}"
              f"  gap {gap:+.4f}")

    print("\nReasoning: a tree that is allowed to grow deep memorises the training "
          "rows. The widening train-test gap is the signature of overfitting.")
    print("\nInterpretation: a shallow tree generalises best here. In practice you "
          "would pick the depth with the best cross-validated score, not the best "
          "training score.")

    best = Pipeline([("pre", pre),
                     ("clf", DecisionTreeClassifier(max_depth=4, random_state=RANDOM_STATE))])
    best.fit(X_train, y_train)
    cv = cross_val_score(best, X_train, y_train, cv=5, scoring="f1")
    print(f"\n  5-fold cross-validated F1 (depth=4): {cv.mean():.4f} "
          f"(+/- {cv.std():.4f})")

    tree_only = DecisionTreeClassifier(max_depth=3, random_state=RANDOM_STATE)
    tree_only.fit(pd.get_dummies(X_train, drop_first=True), y_train)
    print("\n  human-readable tree (depth 3):")
    for line in export_text(tree_only,
                            feature_names=list(pd.get_dummies(X_train,
                                                              drop_first=True).columns)
                            ).splitlines()[:14]:
        print("   ", line)


def main():
    print("LAB 9 - INTRODUCTORY MACHINE LEARNING")
    df = load()
    print(f"dataset: {len(df):,} rows | high-value lines: {df['high_value'].mean():.1%}")
    X, numeric, categorical, pre, y_reg, y_clf = exercise_1_preprocessing(df)
    exercise_2_feature_selection(df, numeric)
    exercise_3_regression(df, numeric, categorical, pre, y_reg)
    exercise_4_classification(df, numeric, categorical, pre, y_clf)
    exercise_5_tree_and_overfit(df, numeric, categorical, pre, y_clf)
    print(f"\n{LINE}\nLAB 9 COMPLETE\n{LINE}")


if __name__ == "__main__":
    main()
