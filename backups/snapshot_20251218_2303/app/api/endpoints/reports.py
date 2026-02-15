from fastapi import APIRouter
from typing import List, Dict
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[Dict])
def get_reports():
    """
    Retrieve a list of mock reports.
    """
    # Mock data
    return [
        {
            "id": 1,
            "name": "AAPL Q2 2024 Financial Analysis",
            "createdAt": "2024-05-20T10:00:00Z",
            "url": "/reports/aapl-q2-2024.pdf"
        },
        {
            "id": 2,
            "name": "GOOGL Competitor Report",
            "createdAt": "2024-05-18T14:30:00Z",
            "url": "/reports/googl-competitors-2024.pdf"
        },
        {
            "id": 3,
            "name": "TSLA Risk Assessment",
            "createdAt": "2024-05-15T11:00:00Z",
            "url": "/reports/tsla-risk-assessment-2024.pdf"
        }
    ] 