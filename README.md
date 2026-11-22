# LAB 9 — Introductory Machine Learning (scikit-learn)

> **Scope note.** This lab is an **optional Data Science extension**. It is not part
> of the core Data Analyst competency set (Labs 1–8). It is included so the project
> shows the next step beyond analysis, and it is deliberately kept small and honest.

## 1. Tool introduction
scikit-learn is the standard Python library for classical machine learning: data
preprocessing, model training, evaluation and pipelines.

## 2. Purpose in professional data analytics
* predict a value or a category from historical data;
* score records (for example, flag high-value orders);
* quantify how well a model generalises before anyone acts on it.

## 3. Important features demonstrated
| Feature | Exercise |
|---|---|
| Data preprocessing (scaling, one-hot encoding) | 1 |
| Train/test split | 1 |
| Feature selection (correlation, tree importance) | 2 |
| Linear regression | 3 |
| Logistic regression | 4 |
| Decision trees | 5 |
| Model evaluation (accuracy, precision, recall, F1, ROC AUC) | 4 |
| Confusion matrix | 4 |
| Overfitting fundamentals | 5 |
| Cross-validation | 5 |
| Pipelines (`ColumnTransformer` + `Pipeline`) | 1–5 |

## 4. Practical exercises
Five exercises: preprocessing and split; feature selection; linear regression;
logistic regression; decision trees and overfitting.

## 5. Working implementation
```bash
python Machine_Learning_Lab/ml_lab.py
```

## 6. Expected output
`evidence/ml_lab_output.txt`. Headline results:

```
Linear regression   RMSE 57.36 GBP | MAE 12.18 GBP | R2 0.6374
Logistic regression accuracy 0.9515 | precision 0.7850 | recall 0.4773 | F1 0.5936
Majority-class baseline accuracy 0.9257
Decision tree depth 4: 5-fold CV F1 0.8740 (+/- 0.0494)
```

## 7. Explanation of results
Two lessons matter. First, **accuracy is misleading on imbalanced data**: a model that
always answers "not high-value" scores 92.6% accuracy, so precision, recall and F1 are
reported instead. Second, **a deeper tree is not a better tree**: training accuracy
reaches 100% while the test score plateaus, which is the signature of overfitting.
Cross-validation, not the training score, is used to pick the depth.

## 8. Common mistakes
| Mistake | Why it hurts | Fix |
|---|---|---|
| Scaling before the split | Data leakage | scale inside a `Pipeline` |
| Reporting accuracy only | Hides failure on the minority class | precision / recall / F1 |
| Tuning on the test set | Over-optimistic estimates | cross-validation on train |
| Using ID columns as features | The model memorises | drop identifiers |
| Trusting training accuracy | Overfitting | always report test / CV scores |

## 9. Mini assessment
1. What is data leakage and how does a `Pipeline` prevent it?
2. Why is accuracy a poor metric when 7% of rows are positive?
3. Explain precision vs recall with the confusion matrix.
4. How do you detect overfitting from the depth table?
5. Why is cross-validation better than a single split?

## 10. Evidence of completed work
```
Machine_Learning_Lab/
├── ml_lab.py
└── evidence/ml_lab_output.txt
```
