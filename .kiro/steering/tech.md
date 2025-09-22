# Technology Stack & Build System

## Architecture Pattern

**Microservices Architecture** with the following core services:
- Policy Management Service
- Claims Processing Service  
- Risk Assessment Service
- Payment Service
- Notification Service
- Robot Integration Service

## Tech Stack

### Backend
- **Runtime**: Python 3.11+
- **Web Framework**: FastAPI with automatic OpenAPI 3.0 generation
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Authentication**: JWT-based auth with role-based access control using python-jose
- **API Gateway**: Centralized routing, rate limiting, and load balancing
- **Async Processing**: asyncio for concurrent operations

### Data & Integration
- **Robot Integration**: IoT telemetry and diagnostic data processing with Pydantic models
- **External APIs**: Payment processors, regulatory APIs, robot diagnostic systems using httpx
- **Real-time Processing**: Robot data analysis and risk score updates with Celery/Redis
- **Data Validation**: Pydantic for request/response validation and serialization

### Infrastructure
- **Cloud Platform**: Azure Container Apps for serverless container deployment
- **Database**: Azure Database for PostgreSQL (Flexible Server)
- **Container Registry**: Azure Container Registry (ACR)
- **CI/CD**: GitHub Actions for automated deployment pipeline
- **Configuration**: Environment variables and .env files for local development
- **Circuit Breakers**: Fault tolerance and graceful degradation using tenacity
- **Health Checks**: Database and service monitoring with custom health endpoints
- **Logging**: Structured logging with loguru and Azure Application Insights
- **Secrets Management**: Azure Key Vault for production secrets

## Development Standards

### Code Quality
- **Test Coverage**: 90% minimum for core business logic
- **Testing Strategy**: pytest for unit, integration, end-to-end, performance, and security testing
- **Error Handling**: Comprehensive error categories with audit trails using custom exception classes
- **Validation**: Pydantic models for input validation at API boundaries and business logic layers
- **Type Hints**: Full type annotation coverage with mypy static type checking

### API Design
- **OpenAPI 3.0**: Automatic specification generation with FastAPI
- **RESTful**: Standard HTTP methods and status codes
- **Idempotent**: Safe retry operations for critical workflows
- **Versioning**: API versioning strategy for backward compatibility
- **Documentation**: Auto-generated interactive docs with Swagger UI

## Common Commands

### Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
pytest --cov=src --cov-report=html

# Development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Code quality
black src/ tests/          # Code formatting
isort src/ tests/          # Import sorting
flake8 src/ tests/         # Linting
mypy src/                  # Type checking
```

### Database
```bash
# Run migrations
alembic upgrade head
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"

# Seed data
python scripts/seed_data.py
```

### API Documentation
```bash
# Generate OpenAPI spec (automatic with FastAPI)
# Access at http://localhost:8000/docs (Swagger UI)
# Access at http://localhost:8000/redoc (ReDoc)

# Export OpenAPI spec
python scripts/export_openapi.py
```

### Infrastructure Management
```bash
# Navigate to infrastructure directory
cd infrastructure

# Install Pulumi dependencies
pip install -r requirements.txt

# Initialize Pulumi stack
pulumi stack init dev

# Configure secrets
pulumi config set --secret app:postgresAdminPassword YourSecurePassword123!

# Deploy infrastructure
pulumi up

# View stack outputs
pulumi stack output

# Destroy infrastructure
pulumi destroy
```

### Azure Deployment
```bash
# Build and push container
docker build -t humanoid-robot-insurance .
az acr build --registry <registry-name> --image humanoid-robot-insurance:latest .

# Deploy to Container Apps
az containerapp update --name humanoid-robot-insurance --resource-group <rg-name> --image <registry-name>.azurecr.io/humanoid-robot-insurance:latest

# View logs
az containerapp logs show --name humanoid-robot-insurance --resource-group <rg-name>
```