# ML Trading Dashboard

A full-stack application for ML-powered stock market analysis and trading, built with FastAPI and React.

## Features

### Backend (FastAPI)
- 🔐 Secure authentication with JWT
- 📊 Real-time market data integration
- 🤖 ML-powered stock predictions
- 📈 Technical analysis indicators
- 🔄 Automated trading capabilities
- 📱 RESTful API endpoints
- 🔍 Advanced search functionality
- 📊 Performance monitoring
- 🔔 Real-time notifications

### Frontend (React)
- 📱 Modern, responsive UI with Material-UI
- 📊 Interactive charts and visualizations
- 🔍 Real-time market data
- 📈 Portfolio tracking
- 📋 Watchlist management
- ⚙️ User preferences and settings
- 🔔 Real-time notifications
- 🌙 Dark/Light theme support

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- JWT Authentication
- yfinance
- scikit-learn
- pandas
- numpy
- pytest

### Frontend
- React
- TypeScript
- Material-UI
- Recharts
- Axios
- React Router
- React Query

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- Redis (optional, for caching)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ml-trading-dashboard.git
cd ml-trading-dashboard
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head
```

3. Set up the frontend:
```bash
cd app/frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

1. Start the backend server:
```bash
# From the root directory
uvicorn app.main:app --reload
```

2. Start the frontend development server:
```bash
# From app/frontend directory
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development

### Backend Development
- API endpoints are in `app/api/endpoints/`
- Database models are in `app/models/`
- Schemas are in `app/schemas/`
- Services are in `app/services/`

### Frontend Development
- Components are in `app/frontend/src/components/`
- Pages are in `app/frontend/src/pages/`
- Hooks are in `app/frontend/src/hooks/`
- API services are in `app/frontend/src/services/`

## Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd app/frontend
npm test
```

## API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Material-UI](https://mui.com/)
- [yfinance](https://pypi.org/project/yfinance/)
- [scikit-learn](https://scikit-learn.org/)

## Support

For support, email your-email@example.com or open an issue in the GitHub repository. 