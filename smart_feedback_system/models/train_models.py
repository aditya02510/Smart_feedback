import os
import json
import time
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_validate, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
from sklearn.pipeline import Pipeline

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.preprocessor import clean_text

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset")
DATA_FILE = os.path.join(DATA_DIR, "college_feedback_dataset.csv")
MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

SENTIMENT_MODEL_PATH = os.path.join(MODELS_DIR, "sentiment_model.joblib")
CATEGORY_MODEL_PATH = os.path.join(MODELS_DIR, "category_model.joblib")
METRICS_PATH = os.path.join(MODELS_DIR, "model_metrics.json")

def load_and_preprocess_data():
    df = pd.read_csv(DATA_FILE)
    df["clean_feedback"] = df["feedback"].astype(str).apply(clean_text)
    return df

def evaluate_models(X_train, X_test, y_train, y_test, task_name="Sentiment"):
    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=1000, C=2.0, class_weight="balanced", random_state=42),
        "Linear SVM (Calibrated)": CalibratedClassifierCV(LinearSVC(dual=False, C=1.5, class_weight="balanced", random_state=42)),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.5),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    }

    results = {}
    best_model_name = None
    best_f1 = -1
    best_pipeline = None

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        analyzer="word",
        sublinear_tf=True,
        min_df=1,
        token_pattern=r"(?u)\b\w+\b"
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    for name, clf in candidates.items():
        start_time = time.time()
        clf.fit(X_train_vec, y_train)
        train_time = time.time() - start_time

        infer_start = time.time()
        y_pred = clf.predict(X_test_vec)
        infer_time = (time.time() - infer_start) * 1000 / len(X_test)  # ms per sample

        acc = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)

        results[name] = {
            "accuracy": round(float(acc), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_weighted": round(float(f1_weighted), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "training_time_sec": round(float(train_time), 4),
            "latency_ms_per_sample": round(float(infer_time), 3)
        }

        if f1_weighted > best_f1:
            best_f1 = f1_weighted
            best_model_name = name
            best_pipeline = {
                "vectorizer": vectorizer,
                "model": clf,
                "classes": list(clf.classes_)
            }

    print(f"\n[{task_name} Analysis] Best Model: {best_model_name} (F1-Weighted: {best_f1:.4f})")
    return results, best_model_name, best_pipeline

def train_all():
    print("Loading feedback dataset...")
    df = load_and_preprocess_data()
    print(f"Total dataset records: {len(df)}")
    print("Class distributions:")
    print("Sentiment:\n", df["sentiment"].value_counts().to_dict())
    print("Category:\n", df["category"].value_counts().to_dict())

    # 1. Sentiment Task
    X = df["clean_feedback"]
    y_sent = df["sentiment"]
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
        X, y_sent, test_size=0.2, random_state=42, stratify=y_sent
    )

    sent_metrics, best_sent_name, best_sent_bundle = evaluate_models(
        X_train_s, X_test_s, y_train_s, y_test_s, task_name="Sentiment Classification"
    )

    # Train final sentiment model on full data for best real-world generalization
    final_sent_vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        analyzer="word",
        sublinear_tf=True,
        min_df=1,
        token_pattern=r"(?u)\b\w+\b"
    )
    X_full_sent = final_sent_vectorizer.fit_transform(X)
    final_sent_model = LogisticRegression(max_iter=1000, C=2.0, class_weight="balanced", random_state=42)
    final_sent_model.fit(X_full_sent, y_sent)

    joblib.dump({
        "vectorizer": final_sent_vectorizer,
        "model": final_sent_model,
        "classes": list(final_sent_model.classes_)
    }, SENTIMENT_MODEL_PATH)
    print(f"Saved final sentiment model to {SENTIMENT_MODEL_PATH}")

    # 2. Category Task
    y_cat = df["category"]
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X, y_cat, test_size=0.2, random_state=42, stratify=y_cat
    )

    cat_metrics, best_cat_name, best_cat_bundle = evaluate_models(
        X_train_c, X_test_c, y_train_c, y_test_c, task_name="Category Classification"
    )

    # Train final category model on full data
    final_cat_vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        analyzer="word",
        sublinear_tf=True,
        min_df=1,
        token_pattern=r"(?u)\b\w+\b"
    )
    X_full_cat = final_cat_vectorizer.fit_transform(X)
    final_cat_model = LogisticRegression(max_iter=1000, C=2.5, class_weight="balanced", random_state=42)
    final_cat_model.fit(X_full_cat, y_cat)

    joblib.dump({
        "vectorizer": final_cat_vectorizer,
        "model": final_cat_model,
        "classes": list(final_cat_model.classes_)
    }, CATEGORY_MODEL_PATH)
    print(f"Saved final category model to {CATEGORY_MODEL_PATH}")

    # Save comprehensive metrics report
    metrics_report = {
        "dataset_total": len(df),
        "sentiment_task": {
            "best_model": best_sent_name,
            "models": sent_metrics,
            "classes": ["Negative", "Neutral", "Positive"]
        },
        "category_task": {
            "best_model": best_cat_name,
            "models": cat_metrics,
            "classes": ["Administration", "Course", "Examination", "Faculty", "Infrastructure", "Technical"]
        }
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_report, f, indent=2)
    print(f"Saved benchmark metrics to {METRICS_PATH}")

if __name__ == "__main__":
    train_all()
