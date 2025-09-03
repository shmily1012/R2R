# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

```bash
# Install and run R2R in light mode
pip install r2r
export OPENAI_API_KEY=sk-...
python -m r2r.serve

# Run with full orchestration using Docker
export R2R_CONFIG_NAME=full OPENAI_API_KEY=sk-...
docker compose -f docker/compose.full.yaml --profile postgres up -d

# Alternative server startup
cd py && python -m r2r.serve --config-name=full

# Run server with custom config
python -m r2r.serve --config-path=/path/to/config.toml --host=0.0.0.0 --port=7272
```

## Development Commands

### Python Backend (py/)
```bash
# Install dev dependencies
pip install -e ".[core,dev]"

# Run tests
pytest tests/                          # All tests
pytest tests/unit/                     # Unit tests only
pytest tests/integration/              # Integration tests only
pytest -v tests/integration/test_documents.py  # Single test file

# Code quality
ruff check .                          # Linting
ruff format .                         # Code formatting  
mypy .                               # Type checking

# Database migrations
cd py/migrations
alembic upgrade head                  # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration
```

### JavaScript SDK (js/sdk/)
```bash
# Install and build
npm install
npm run build

# Run tests
npm test                             # All tests
npm run test:watch                   # Watch mode
npm run test:coverage               # Coverage report
npm run test:chunks                 # Specific test suite
npm run test:collections            # Collections tests
npm run test:documents             # Documents tests

# Code formatting
npm run format
```

## Architecture Overview

### Core Components

**R2R** is a production-ready RAG (Retrieval-Augmented Generation) system with a modular architecture:

- **Core Engine (py/core/)**: Main application logic with provider pattern
- **API Layer (py/core/main/api/v3/)**: FastAPI-based REST endpoints  
- **Services Layer (py/core/main/services/)**: Business logic services
- **Providers (py/core/providers/)**: Pluggable components for database, LLM, embeddings, etc.
- **SDKs**: Python (py/sdk/) and JavaScript (js/sdk/) client libraries

### Key Services

- **AuthService**: User authentication and authorization
- **IngestionService**: Document processing and chunking pipeline
- **RetrievalService**: Search and RAG functionality
- **GraphService**: Knowledge graph construction and querying  
- **ManagementService**: System administration
- **MaintenanceService**: Background maintenance tasks

### Provider Architecture

The system uses a provider pattern for extensibility:

- **Database**: PostgreSQL with pgvector for embeddings
- **LLM**: OpenAI, Anthropic, Ollama, LiteLLM support
- **Embeddings**: OpenAI, LiteLLM, Ollama providers
- **Authentication**: JWT, Supabase, Clerk integration
- **File Storage**: Local filesystem, S3-compatible storage
- **Orchestration**: Simple or Hatchet-based workflow engines

### Configuration System

Configurations are in `py/core/configs/` using TOML format:

- `full.toml`: Complete setup with all features
- `ollama.toml`: Ollama LLM integration  
- `r2r_with_auth.toml`: Authentication enabled
- Custom configs via `--config-path` or `--config-name`

### Database Schema

Uses Alembic migrations in `py/migrations/versions/`. Key tables:
- Documents, chunks, collections for content management
- Users, conversations for user interactions  
- Graphs for knowledge relationships
- Tokens, limits for usage tracking

## Docker & Orchestration

### Deployment Modes

**Light Mode** (`docker/compose.yaml`):
- R2R server + PostgreSQL + MinIO
- Basic functionality for development

**Full Mode** (`docker/compose.full.yaml`):  
- Includes Hatchet orchestration engine
- Unstructured document processing service
- Graph clustering service
- Production-ready with workflow management

### Service Ports

- R2R API Server: 7272
- R2R Dashboard: 7273  
- Hatchet Dashboard: 7274
- PostgreSQL: 5432
- MinIO: 9000/9001
- Graph Clustering: 7276

## Testing Strategy

### Integration Tests
Located in `py/tests/integration/` with comprehensive API coverage:
- Document ingestion and management
- User authentication and collections
- Retrieval and RAG functionality
- Graph construction and queries
- System administration

### JavaScript Tests
Located in `js/sdk/__tests__/` covering:
- All API endpoints through SDK
- Type transformations and utilities
- Integration with different user roles

## Configuration Examples

### Environment Variables
```bash
# Core settings
R2R_CONFIG_NAME=full
R2R_HOST=0.0.0.0  
R2R_PORT=7272
OPENAI_API_KEY=sk-...

# Database  
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres

# Optional services
TAVILY_API_KEY=tvly-...
HATCHET_CLIENT_TOKEN=...
```

### Custom User Tools
Place custom tools in `docker/user_tools/` and requirements in `user_requirements.txt` for automatic installation.

## Common Development Workflows

### Adding New API Endpoints
1. Create router in `py/core/main/api/v3/`
2. Implement service logic in `py/core/main/services/`
3. Add provider interface if needed in `py/core/providers/`
4. Add integration tests in `py/tests/integration/`
5. Update SDK methods in both Python and JavaScript

### Database Schema Changes
1. Modify models in `py/core/providers/database/`
2. Generate migration: `alembic revision --autogenerate`
3. Review and edit migration file
4. Test migration: `alembic upgrade head`

### Adding New Document Parsers
1. Create parser in appropriate `py/core/parsers/` subdirectory
2. Register in `py/core/parsers/__init__.py`
3. Add supported file type to configuration
4. Test with sample files in `py/core/examples/supported_file_types/`