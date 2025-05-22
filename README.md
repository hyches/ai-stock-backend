# AI Stock Portfolio Platform - Backend

A powerful backend service for AI-driven stock portfolio management, featuring stock screening, portfolio optimization, and automated research reports.

## 🚀 Features

- **Stock Screener**: Filter stocks based on technical and fundamental metrics
- **Portfolio Optimizer**: AI-powered portfolio allocation using ML models
- **Research Reports**: Automated generation of stock research reports
- **REST API**: FastAPI-based endpoints for frontend integration

## 🛠️ Tech Stack

- Python 3.9+
- FastAPI
- Pydantic
- Pandas & NumPy
- Scikit-learn
- YFinance/Alpha Vantage
- ReportLab/WeasyPrint

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-stock-backend.git
cd ai-stock-backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

## 🏃‍♂️ Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

Run the test suite:
```bash
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 