# Machine Learning

## Supervised vs Unsupervised Learning
- Supervised Learning: Algorithms train on labeled datasets (features paired with known ground-truth targets).
  - Regression: Predicts continuous numerical targets (e.g. Linear Regression, Gradient Boosted Trees).
  - Classification: Predicts discrete categorical class labels (e.g. Logistic Regression, Random Forest, SVM).
- Unsupervised Learning: Discovers hidden patterns, groupings, or representations in unlabeled data (e.g. K-Means clustering, Principal Component Analysis (PCA)).

## Bias-Variance Tradeoff and Overfitting
- High Bias (Underfitting): Model is overly simplistic and fails to capture underlying patterns in training data (high training error and high test error). Remediated by increasing model complexity, adding features, or decreasing regularization.
- High Variance (Overfitting): Model memorizes noise and idiosyncrasies of training data, failing to generalize to unseen test data (low training error but high test error). Remediated by L1/L2 regularization, dropout, cross-validation, and acquiring more training samples.

## Evaluation Metrics
- Confusion Matrix: True Positives (TP), True Negatives (TN), False Positives (FP), False Negatives (FN).
- Precision: TP / (TP + FP). Measures accuracy of positive predictions (vital in spam detection).
- Recall (Sensitivity): TP / (TP + FN). Measures ability to identify all actual positive cases (vital in cancer detection and fraud prevention).
- F1-Score: Harmonic mean of precision and recall: 2 * (Precision * Recall) / (Precision + Recall).
- ROC-AUC: Area under the Receiver Operating Characteristic curve, measuring classification capability across all discrimination thresholds.
