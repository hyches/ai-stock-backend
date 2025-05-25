# Trading System

A modern web-based trading system built with Python (FastAPI) and React (TypeScript).

## Features

- Real-time trading signals and execution
- Portfolio management and tracking
- Multiple trading strategies support
- Backtesting capabilities
- Performance analytics and reporting
- User authentication and authorization
- Modern, responsive UI

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pandas
- NumPy
- TA-Lib

### Frontend
- React 18
- TypeScript
- Material-UI
- Recharts
- Axios

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- PostgreSQL
- TA-Lib

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/trading-system.git
cd trading-system
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

3. Set up the frontend:
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

4. Access the application:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
trading-system/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── services/
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── hooks/
│       └── utils/
├── tests/
├── alembic/
├── .env.example
├── requirements.txt
└── README.md
```

## Development

### Backend Development

- API endpoints are defined in `app/api/v1/endpoints/`
- Database models are in `app/models/`
- Pydantic schemas are in `app/schemas/`
- Business logic is in `app/services/`

### Frontend Development

- React components are in `frontend/src/components/`
- Custom hooks are in `frontend/src/hooks/`
- API integration is handled in `frontend/src/hooks/useApi.ts`

## Testing

### Backend Tests
```bash
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

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
- [Recharts](https://recharts.org/) 