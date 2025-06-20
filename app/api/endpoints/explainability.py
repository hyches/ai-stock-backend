from fastapi import APIRouter, Body
import numpy as np
from app.services.explainability import ExplainabilityService
from sklearn.ensemble import RandomForestClassifier

router = APIRouter()

# Dummy model and data for demo
X_train = np.random.rand(100, 5)
y_train = np.random.randint(0, 2, 100)
model = RandomForestClassifier().fit(X_train, y_train)
service = ExplainabilityService(model, X_train)

@router.post("/explain/shap")
def explain_shap(X: list = Body(...)):
    X = np.array(X)
    return {"shap_values": service.shap_explain(X)}

@router.post("/explain/lime")
def explain_lime(X: list = Body(...)):
    X = np.array(X)
    return {"lime_explanations": service.lime_explain(X)} 