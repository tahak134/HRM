# app/ai/trainer.py

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, mean_squared_error

# Import models directly from performance
from app.models.performance import Goal, Feedback, PerformanceReview

MODEL_PATH = "app/ai/models/performance_predictor.joblib"
META_PATH = "app/ai/models/performance_meta.joblib"


async def load_training_data():
    """Load goals, feedback, and performance reviews into a training dataframe"""
    goals = await Goal.find_all().to_list()
    feedback = await Feedback.find_all().to_list()
    reviews = await PerformanceReview.find_all().to_list()

    data = []

    for rev in reviews:
        row = {
            "employee_id": rev.employee_id,
            "overall_rating": rev.overall_rating,
            "num_strengths": len(rev.strengths),
            "num_improvements": len(rev.areas_for_improvement),
            "num_achievements": len(rev.achievements),
            "goals_achieved": len(rev.goals_achieved),
            "goals_missed": len(rev.goals_missed),
            "feedback_count": len(rev.feedback_collected),
        }

        # Feedback aggregation (basic sentiment and rating averages)
        fb_for_emp = [fb for fb in feedback if fb.receiver_id == rev.employee_id]
        if fb_for_emp:
            ratings = [fb.rating for fb in fb_for_emp if fb.rating is not None]
            sentiments = [fb.sentiment_score for fb in fb_for_emp if fb.sentiment_score is not None]
            row["avg_feedback_rating"] = np.mean(ratings) if ratings else 0
            row["avg_sentiment"] = np.mean(sentiments) if sentiments else 0
        else:
            row["avg_feedback_rating"] = 0
            row["avg_sentiment"] = 0

        # Goal progress aggregation
        goals_for_emp = [g for g in goals if g.owner_employee_id == rev.employee_id]
        if goals_for_emp:
            row["avg_goal_progress"] = np.mean([g.progress_percentage for g in goals_for_emp])
        else:
            row["avg_goal_progress"] = 0

        data.append(row)

    return pd.DataFrame(data)


async def train_model():
    df = await load_training_data()
    if df.empty:
        print("⚠️ No training data available. Fallback to rule-based recommendations.")
        return None

    X = df.drop(columns=["overall_rating", "employee_id"])
    y = (df["overall_rating"] >= 4).astype(int)  # Binary: High performer (1) vs not (0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    roc = roc_auc_score(y_test, y_pred_proba)
    rmse = mean_squared_error(y_test, y_pred_proba, squared=False)

    print(f" Model trained. ROC-AUC: {roc:.3f}, RMSE: {rmse:.3f}")

    # Save
    joblib.dump(model, MODEL_PATH)
    joblib.dump({"roc_auc": roc, "rmse": rmse, "features": list(X.columns)}, META_PATH)

    return model
