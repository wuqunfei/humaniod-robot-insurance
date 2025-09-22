# Humanoid Robot Insurance Platform

A cloud-based SaaS solution providing comprehensive insurance services specifically tailored for humanoid robots. The platform integrates traditional insurance workflows with modern IoT capabilities and AI-driven risk assessment.

## Features

- **Specialized Insurance Products**: Tailored coverage for humanoid robots with unique risk profiles
- **Real-time Risk Assessment**: Using robot diagnostic data and telemetry
- **Streamlined Claims Processing**: Automated damage evaluation and settlement
- **API-First Architecture**: Enabling manufacturer partnerships and embedded insurance
- **Multi-stakeholder Support**: Customers, manufacturers, adjusters, and compliance officers

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cloud**: Azure Container Apps, Azure Database for PostgreSQL
- **CI/CD**: GitHub Actions
- **Authentication**: JWT with role-based access control
- **Documentation**: Auto-generated OpenAPI 3.0 specification

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (for background tasks)
- Azure CLI (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd humanoid-robot-insurance
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Azure Deployment

### Prerequisites

- Azure CLI installed and logged in
- Pulumi CLI installed
- Azure subscription with appropriate permissions
- GitHub repository with secrets configured

### Infrastructure Setup

1. **Navigate to infrastructure directory**
   ```bash
   cd infrastructure
   ```

2. **Install Pulumi dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Pulumi stack**
   ```bash
   pulumi stack init dev
   pulumi config set azure-native:region "East US"
   pulumi config set app:environment dev
   pulumi config set app:postgresAdminLogin adminuser
   pulumi config set --secret app:postgresAdminPassword YourSecurePassword123!
   ```

4. **Deploy Azure resources**
   ```bash
   pulumi up
   ```

4. **Configure GitHub Secrets**
   - `AZURE_CREDENTIALS`: Service principal credentials
   - `PULUMI_ACCESS_TOKEN`: Pulumi access token
   - `PULUMI_STACK_NAME`: Pulumi stack name (e.g., dev)
   - `AZURE_CLIENT_ID`: Azure service principal client ID
   - `AZURE_CLIENT_SECRET`: Azure service principal client secret
   - `AZURE_TENANT_ID`: Azure tenant ID
   - `AZURE_SUBSCRIPTION_ID`: Azure subscription ID
   - `AZURE_CONTAINER_APP_NAME`: Container app name
   - `AZURE_RESOURCE_GROUP`: Resource group name

### Deployment Pipeline

The GitHub Actions workflow automatically:
- Runs tests and code quality checks
- Builds and pushes Docker images to Azure Container Registry
- Deploys to Azure Container Apps on main branch pushes

## API Documentation

The API follows OpenAPI 3.0 specification with automatic documentation generation. Key endpoints include:

- **Health Check**: `GET /health`
- **Robot Management**: `POST /api/v1/robots`, `GET /api/v1/robots/{id}`
- **Policy Management**: `POST /api/v1/policies`, `GET /api/v1/policies/{id}`
- **Claims Processing**: `POST /api/v1/claims`, `GET /api/v1/claims/{id}`

## Project Structure

```
├── src/                    # Application source code
│   ├── api/               # FastAPI routers and dependencies
│   ├── core/              # Core application logic
│   ├── models/            # SQLAlchemy models and Pydantic schemas
│   ├── repositories/      # Data access layer
│   ├── services/          # Business logic services
│   └── utils/             # Shared utilities
├── infrastructure/        # Infrastructure as code (Pulumi)
├── tests/                 # Test suites
├── alembic/              # Database migrations
├── .github/workflows/    # CI/CD pipelines
└── docs/                 # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass and code quality checks pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.