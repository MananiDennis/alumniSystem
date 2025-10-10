# Alumni Tracking System - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Data Collection Methods](#data-collection-methods)
8. [Database Schema](#database-schema)
9. [API Reference](#api-reference)
10. [CLI Reference](#cli-reference)
11. [Frontend Guide](#frontend-guide)
12. [Testing](#testing)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)
15. [Contributing](#contributing)

## Overview

The Alumni Tracking System is a comprehensive solution for managing and tracking alumni career information for Edith Cowan University (ECU). The system provides multiple methods for collecting alumni data, including web research, manual entry, and legacy BrightData integration, with AI-powered data structuring and quality control.

### Key Components
- **Backend API**: FastAPI-based REST API with SQLAlchemy ORM
- **Frontend**: React web application with Material-UI
- **Database**: SQLite/PostgreSQL with SQLAlchemy
- **Data Collection**: Web research, manual entry, BrightData (legacy)
- **AI Integration**: OpenAI GPT-4 for data conversion and validation
- **CLI Tools**: Command-line interface for batch operations

### Technology Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Uvicorn
- **Frontend**: React 18, Material-UI, Axios
- **Database**: SQLite (default) / PostgreSQL
- **AI**: OpenAI GPT-4 API
- **Web Scraping**: BeautifulSoup, DuckDuckGo search
- **Testing**: pytest, React Testing Library

## Architecture

```mermaid
graph TB
    A[React Frontend] --> B[FastAPI Backend]
    B --> C[SQLAlchemy ORM]
    C --> D[(SQLite/PostgreSQL)]
    
    B --> E[Alumni Collector]
    E --> F[Web Research Service]
    E --> G[BrightData Service]
    E --> L[LinkedIn Service]
    L --> NotFit(["🚫Not Fit"])
    G --> X(["🚫Unethical"])
    E --> H[Manual Entry]
    
    F <--> I[DuckDuckGo Search]
    F <--> J[BeautifulSoup Parser]
    F <--> K[AI Verification Service]
    
    K --> OpenAI[OpenAI GPT-4]
    
    B --> M[Search Service]
    B --> N[Export Service]
    B --> O[Update Service]
    
    P[CLI Tools] --> B
```

### Core Services

#### AlumniCollector
Main service orchestrating data collection from multiple sources:
- **Web Research**: Default method using DuckDuckGo + AI
- **BrightData**: Legacy LinkedIn scraping (non-compliant)
- **Manual Entry**: Direct profile creation via API/forms

#### WebResearchService
Handles web-based alumni research:
- Generates multiple search queries per person
- Scrapes DuckDuckGo results
- Extracts professional information from web pages
- Integrates with AI for data structuring

#### AI Verification Service
Converts unstructured web data to structured profiles:
- Uses GPT-4 for intelligent data extraction
- Assigns confidence scores (0.0-1.0)
- Validates data quality and completeness
- Filters out low-confidence profiles (< 0.5)

#### Search & Export Services
- Advanced filtering by name, industry, company, location
- Excel/CSV export with custom filters
- Statistics and analytics generation

## Features

### Data Collection
- ✅ **Web Research** (Default): Free, compliant web scraping + AI
- ✅ **Manual Entry**: Direct alumni profile creation
- ⚠️ **BrightData** (Legacy): Fast but potentially non-compliant
- ✅ **Excel Upload**: Batch import from spreadsheets
- ✅ **AI-Powered Conversion**: Automatic data structuring
- ✅ **Confidence Scoring**: Quality control (0.5 threshold)

### Search & Management
- 🔍 **Advanced Search**: Multi-field filtering
- 📊 **Analytics Dashboard**: Statistics and insights
- 📤 **Export Options**: Excel/CSV with filters
- 🔄 **Profile Updates**: Automated data refresh
- 👥 **User Management**: Authentication system

### Quality Control
- 🎯 **Confidence Thresholds**: Prevents low-quality data
- ✅ **Data Validation**: Comprehensive input validation
- 🔍 **Duplicate Detection**: Prevents duplicate profiles
- 📈 **Data Freshness**: Tracks update timestamps

### User Interface
- 🌐 **Web Dashboard**: React-based management interface
- 📱 **Responsive Design**: Mobile-friendly interface
- 🎨 **Material-UI**: Modern, accessible design
- ⚡ **Real-time Updates**: Live task status monitoring

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+ & npm
- Git

### Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd AlumniSystem
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install frontend dependencies:**
```bash
cd frontend
npm install
cd ..
```

4. **Start the system:**
```bash
python start.py
```

This will start:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend Setup
```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database.connection import db_manager; db_manager.create_tables()"
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

#### Environment Configuration
Create a `.env` file in the root directory:
```bash
# OpenAI (required for web research)
OPENAI_API_KEY=your_openai_api_key_here

# BrightData (optional, legacy)
BRIGHTDATA_API_KEY=your_brightdata_key_here
BRIGHTDATA_DATASET_ID=your_dataset_id_here

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///alumni_tracking.db
# or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/alumni_tracking

# Security
SECRET_KEY=your-secret-key-here
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes (web research) | - | OpenAI API key for AI data conversion |
| `BRIGHTDATA_API_KEY` | No | - | BrightData API key (legacy) |
| `BRIGHTDATA_DATASET_ID` | No | - | BrightData dataset ID |
| `DATABASE_URL` | No | `sqlite:///alumni_tracking.db` | Database connection string |
| `SECRET_KEY` | No | Auto-generated | JWT signing key |

### Database Configuration

The system supports both SQLite (default) and PostgreSQL:

**SQLite (Development):**
```bash
DATABASE_URL=sqlite:///alumni_tracking.db
```

**PostgreSQL (Production):**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/alumni_tracking
```

### AI Configuration

Web research requires OpenAI API access:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

The AI service uses GPT-4 for:
- Converting unstructured web data to structured profiles
- Industry classification
- Confidence score assignment
- Data validation

## Usage

### Web Interface

1. **Access the dashboard** at http://localhost:3000
2. **Login** with your credentials
3. **Upload alumni names** via Excel file or manual entry
4. **Choose collection method** (Web Research recommended)
5. **Monitor progress** and view results
6. **Search and export** alumni data

### API Usage

#### Collect Alumni Data
```bash
curl -X POST "http://localhost:8000/collect" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"names": ["John Smith", "Jane Doe"], "use_web_research": true}'
```

#### Get Collection Status
```bash
curl "http://localhost:8000/collect/status/TASK_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Search Alumni
```bash
curl "http://localhost:8000/search?name=John&industry=Technology"
```

### CLI Usage

#### Web Research Collection
```bash
python -m src.cli web-research "John Smith" "Jane Doe"
```

#### Search Database
```bash
python -m src.cli search --name "John Smith"
python -m src.cli search --industry Technology --location "Perth"
```

#### Export Data
```bash
python -m src.cli export --format excel --industry Technology
```

#### View Statistics
```bash
python -m src.cli stats
```

## Data Collection Methods

### Web Research (Recommended)

**Process Flow:**
```mermaid
graph TD
    A[Input Name] --> B[Generate Search Queries]
    B --> C[DuckDuckGo Search]
    C --> D[Extract Top Results]
    D --> E[Scrape Web Pages]
    E --> F[AI Data Conversion]
    F --> G[Validate Confidence]
    G --> H{Confidence >= 0.5?}
    H -->|Yes| I[Save to Database]
    H -->|No| J[Discard Profile]
```

**Features:**
- Free (no API costs beyond OpenAI)
- Compliant with web scraping best practices
- AI-powered data structuring
- Confidence-based quality control
- Multiple search queries per person

**Configuration:**
- Requires `OPENAI_API_KEY`
- Uses DuckDuckGo for search
- BeautifulSoup for HTML parsing
- GPT-4 for data conversion

### Manual Entry

**Process:**
1. Access frontend data collection page
2. Fill alumni details manually
3. Add work history and education
4. Submit profile for storage

**Benefits:**
- Highest data quality
- Complete control over information
- No external dependencies
- Immediate availability

### BrightData (Legacy)

**Warning:** This method may violate LinkedIn's Terms of Service.

**Process:**
- Uses BrightData scraping API
- Direct LinkedIn profile access
- Fast data collection
- High accuracy but non-compliant

**Configuration:**
```bash
BRIGHTDATA_API_KEY=your_key
BRIGHTDATA_DATASET_ID=your_dataset
```

## Database Schema

### AlumniProfile Table
```sql
CREATE TABLE alumni_profiles (
    id INTEGER PRIMARY KEY,
    full_name VARCHAR NOT NULL,
    graduation_year INTEGER,
    location VARCHAR,
    industry VARCHAR,
    linkedin_url VARCHAR,
    confidence_score REAL DEFAULT 1.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### JobPosition Table
```sql
CREATE TABLE job_positions (
    id INTEGER PRIMARY KEY,
    alumni_id INTEGER REFERENCES alumni_profiles(id),
    title VARCHAR NOT NULL,
    company VARCHAR NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    industry VARCHAR,
    location VARCHAR
);
```

### DataSource Table
```sql
CREATE TABLE data_sources (
    id INTEGER PRIMARY KEY,
    alumni_id INTEGER REFERENCES alumni_profiles(id),
    source_type VARCHAR NOT NULL, -- 'web-research', 'brightdata', 'manual'
    source_url VARCHAR,
    collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score REAL DEFAULT 1.0
);
```

### User Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP
);
```

## API Reference

### Authentication Endpoints

#### POST /auth/login
Authenticate user and get JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

### Alumni Endpoints

#### GET /alumni
List all alumni profiles.

#### GET /alumni/{id}
Get specific alumni profile.

#### GET /search
Search alumni with filters.

**Query Parameters:**
- `name`: Search by name
- `industry`: Filter by industry
- `company`: Filter by company
- `location`: Filter by location

#### POST /collect
Start alumni data collection.

**Request:**
```json
{
  "names": ["John Smith", "Jane Doe"],
  "use_web_research": true
}
```

#### GET /collect/status/{task_id}
Get collection task status.

### Export Endpoints

#### GET /export
Export alumni data.

**Query Parameters:**
- `format`: `excel` or `csv`
- `industry`: Filter by industry
- `graduation_year_min`: Minimum graduation year
- `graduation_year_max`: Maximum graduation year
- `location`: Filter by location

## CLI Reference

### Collection Commands

#### `python -m src.cli web-research <names...>`
Collect alumni data using web research.

#### `python -m src.cli linkedin <names...>`
Collect alumni data using BrightData (legacy).

#### `python -m src.cli collect <names...>`
Manual collection (deprecated).

### Search Commands

#### `python -m src.cli search [options]`
Search alumni database.

**Options:**
- `--name NAME`: Search by name
- `--industry INDUSTRY`: Filter by industry
- `--company COMPANY`: Filter by company
- `--location LOCATION`: Filter by location
- `--graduation-year YEAR`: Filter by graduation year
- `--query TEXT`: Advanced text search

### Management Commands

#### `python -m src.cli stats`
Show database statistics.

#### `python -m src.cli list`
List all alumni.

#### `python -m src.cli export [options]`
Export alumni data.

**Options:**
- `--format excel|csv`: Export format
- `--industry INDUSTRY`: Filter by industry
- `--graduation-year-min YEAR`: Minimum graduation year
- `--graduation-year-max YEAR`: Maximum graduation year

#### `python -m src.cli update [options]`
Update existing profiles.

**Options:**
- `--ids ID1 ID2`: Update specific profiles
- `--max-age-days DAYS`: Update profiles older than N days

## Frontend Guide

### Pages Overview

#### Dashboard
- System statistics and overview
- Recent alumni additions
- Quick actions and navigation

#### Data Collection
- **Automated Tab**: Upload Excel files and start collection
- **Manual Tab**: Direct alumni profile entry
- Task progress monitoring

#### Alumni List
- Searchable alumni directory
- Filter by various criteria
- Export functionality

#### Analytics
- Industry distribution charts
- Geographic distribution
- Career progression insights

### Manual Data Entry

**Required Fields:**
- Full Name
- Graduation Year (dropdown)
- Location
- Industry

**Optional Fields:**
- LinkedIn URL
- Current Job Details
- Work History
- Education

**Work History Format:**
```
Job Title - Company Name - Start Date - End Date
Senior Developer - Tech Corp - 2020-01-01 - 2022-12-31
```

## Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_database.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Test Categories

#### Unit Tests
- Service layer functionality
- Data validation
- API endpoint logic

#### Integration Tests
- Database operations
- External API calls
- End-to-end workflows

#### Data Collection Tests
- Web research accuracy
- AI conversion quality
- Confidence scoring validation

## Deployment

### Docker Deployment

**Build and run:**
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

**Docker Compose Configuration:**
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/alumni
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=alumni
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

### Production Considerations

#### Environment Setup
- Use PostgreSQL in production
- Set strong `SECRET_KEY`
- Configure proper CORS origins
- Enable HTTPS

#### Security
- Use environment variables for secrets
- Implement rate limiting
- Add input validation
- Regular security updates

#### Performance
- Database indexing
- Caching layer (Redis)
- Background task processing (Celery)
- CDN for static assets

## Troubleshooting

### Common Issues

#### "OpenAI API key not configured"
**Solution:** Add `OPENAI_API_KEY` to your `.env` file.

#### "Database connection failed"
**Solution:** Check `DATABASE_URL` and ensure database is running.

#### "Frontend not loading"
**Solution:** Ensure Node.js is installed and run `npm install` in frontend directory.

#### "Collection tasks failing"
**Solution:** Check logs for specific errors. Ensure AI service is configured for web research.

#### "Low confidence scores"
**Solution:** Review AI prompts or manually adjust confidence thresholds.

### Debug Mode

Enable debug logging:
```bash
# Backend
export LOG_LEVEL=DEBUG
python start.py

# Frontend
cd frontend
npm start
```

### Log Locations

- **Backend logs**: Console output when running `start.py`
- **Database logs**: Check SQLite file or PostgreSQL logs
- **Frontend logs**: Browser developer console

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards

#### Python
- Follow PEP 8 style guide
- Use type hints
- Add docstrings to functions
- Write comprehensive tests

#### React
- Use functional components with hooks
- Follow React best practices
- Use Material-UI components
- Add PropTypes for component props

#### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Testing Requirements

- Maintain >80% code coverage
- All new features must have tests
- Integration tests for API changes
- E2E tests for frontend changes

---

**Built for Edith Cowan University Alumni Tracking**
**Version 1.0.0**
**Last Updated: October 2025**