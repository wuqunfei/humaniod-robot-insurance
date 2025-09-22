# Project Structure & Organization

## Directory Layout

```
├── src/
│   ├── services/           # Core microservices
│   │   ├── policy/         # Policy Management Service
│   │   ├── claims/         # Claims Processing Service
│   │   ├── risk/           # Risk Assessment Service
│   │   ├── payment/        # Payment Service
│   │   ├── notification/   # Notification Service
│   │   └── robot/          # Robot Integration Service
│   ├── models/             # SQLAlchemy models and Pydantic schemas
│   │   ├── robot.py        # Robot entity and specifications
│   │   ├── policy.py       # Policy entity and coverage types
│   │   ├── claim.py        # Claim entity and workflow states
│   │   └── risk.py         # Risk profile and assessment data
│   ├── repositories/       # Data access layer
│   │   ├── robot_repository.py
│   │   ├── policy_repository.py
│   │   ├── claims_repository.py
│   │   └── base_repository.py
│   ├── api/               # FastAPI routers and dependencies
│   │   ├── routers/       # API route definitions
│   │   ├── dependencies/  # Dependency injection (auth, db, etc.)
│   │   ├── middleware/    # Custom middleware
│   │   └── schemas/       # Pydantic request/response schemas
│   ├── core/              # Core application logic
│   │   ├── config.py      # Configuration management
│   │   ├── security.py    # Authentication and authorization
│   │   ├── exceptions.py  # Custom exception classes
│   │   └── database.py    # Database connection and session management
│   └── utils/             # Shared utilities
│       ├── validation.py  # Input validation helpers
│       ├── logging.py     # Logging configuration
│       └── constants.py   # Application constants
├── tests/                 # Test suites
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── e2e/              # End-to-end tests
│   ├── fixtures/         # Test data and mocks
│   └── conftest.py       # pytest configuration and fixtures
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Alembic configuration
├── docs/                 # Documentation
│   ├── api/              # Generated API documentation
│   └── architecture/     # Architecture diagrams and specs
├── scripts/              # Utility scripts
│   ├── seed_data.py      # Database seeding
│   └── export_openapi.py # OpenAPI spec export
├── .github/              # GitHub Actions workflows
│   └── workflows/        # CI/CD pipeline definitions
├── infrastructure/       # Infrastructure as code
│   ├── __main__.py      # Pulumi infrastructure definition
│   ├── Pulumi.yaml      # Pulumi project configuration
│   ├── Pulumi.dev.yaml  # Development environment config
│   ├── Pulumi.prod.yaml # Production environment config
│   ├── requirements.txt # Pulumi dependencies
│   └── README.md        # Infrastructure documentation
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── alembic.ini          # Alembic configuration
├── pyproject.toml       # Project metadata and tool configuration
├── Dockerfile           # Container configuration
├── .env.example         # Environment variables template
└── .dockerignore        # Docker ignore file
```

## Core Entity Organization

### Models (`src/models/`)
- **robot.py**: Robot specifications, owner data, diagnostic integration (SQLAlchemy + Pydantic)
- **policy.py**: Coverage types, terms, status management, compliance (SQLAlchemy + Pydantic)
- **claim.py**: Incident tracking, workflow states, settlement data (SQLAlchemy + Pydantic)
- **risk.py**: Risk profiles, scoring algorithms, premium calculations (SQLAlchemy + Pydantic)

### Services (`src/services/`)
Each service follows the same internal structure:
```
service_name/
├── __init__.py           # Package initialization
├── service.py            # Business logic implementation
├── schemas.py            # Pydantic models for service
├── exceptions.py         # Service-specific exceptions
└── tests/                # Service unit tests
    └── test_service.py
```

### API Layer (`src/api/routers/`)
- **Customer Portal**: Policy management, claims, payments
- **Manufacturer API**: Embedded insurance, bulk coverage, robot registration
- **Adjuster Dashboard**: Claims processing, assessment workflows
- **Analytics API**: Risk reporting, compliance metrics

## Naming Conventions

### Files and Directories
- **snake_case** for Python files and directories: `risk_assessment/`, `claims_processing/`
- **snake_case** for Python modules: `risk_assessment_service.py`
- **PascalCase** for classes: `RobotSpecification`, `PolicyService`
- **UPPER_SNAKE_CASE** for constants: `MAX_POLICY_DURATION`, `DEFAULT_RISK_SCORE`

### Database Tables
- **snake_case** for table names: `robot_policies`, `claim_assessments`
- **Singular** entity names: `robot`, `policy`, `claim`
- **Foreign keys**: `robot_id`, `policy_id`

### API Endpoints
- **RESTful** resource naming: `/api/v1/policies`, `/api/v1/claims`
- **Nested resources**: `/api/v1/robots/{id}/policies`
- **Actions**: `/api/v1/policies/{id}/renew`, `/api/v1/claims/{id}/settle`

## Configuration Management

### Environment-based Config
- **Development**: Local database, mock external services
- **Testing**: In-memory database, stubbed integrations
- **Production**: Managed database, real external APIs

### Service Discovery
- Each service registers health check endpoints
- API Gateway routes based on service availability
- Circuit breakers for external service failures

## Data Flow Patterns

### Request Processing
1. **API Gateway**: Authentication, rate limiting, routing
2. **Controller**: Request validation, response formatting
3. **Service**: Business logic, orchestration
4. **Repository**: Data persistence, queries
5. **External APIs**: Robot diagnostics, payments, regulatory

### Event-Driven Updates
- **Robot Diagnostics**: Real-time risk score updates
- **Policy Changes**: Notification triggers, compliance checks
- **Claims Processing**: Status updates, adjuster assignments