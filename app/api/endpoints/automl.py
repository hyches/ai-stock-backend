from fastapi import APIRouter, Body
from app.services.automl import AutoMLService
import numpy as np

router = APIRouter()

@router.post("/automl/run")
def automl_run(X: list = Body(...), y: list = Body(...)):
    X = np.array(X)
    y = np.array(y)
    service = AutoMLService()
    return service.run(X, y) 