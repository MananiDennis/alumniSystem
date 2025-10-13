# Alumni Tracking System - Complete Documentation
## Overview
This is a system that aims to track and provide a way to query to get the alumni in ECU.
The main functions of the system are:
1. Data collection either manually or via web research
2. Storage and Viewing the records of the alumnis in ECU
3. Analysis of results using AI

## The Program
- The program is divided into the frontend (for the UI and the basic interaction with the user) and the backend (for the logic)
- Below is a brief overview of how the program looks like:
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
### The frontend
- The frontend was built with **React Js** and **materials UI library**. We used **axios** to reach the backend.
```
frontend/
├── public/
│   ├── img/
│   │   └── Edith_Cowan_University_Logo.svg
│   └── index.html
├── src/
│   ├── components/
│   │   └── Layout.js          # Main layout with sidebar and navigation
│   ├── pages/
│   │   ├── Login.js           # Authentication page for user login
│   │   ├── Alumni.js          # Alumni directory with view/edit/delete
│   │   ├── Analytics.js       # AI-powered query interface
│   │   ├── Dashboard.js       # Overview dashboard
│   │   └── DataCollection.js  # Manual and web research data entry
│   ├── utils/
│   │   └── api.js             # API configuration and utilities
│   ├── App.js                 # Main app component with routing
│   └── index.js               # React entry point
├── package.json               # Dependencies and scripts
└── .env                       # Environment variables
```
#### **App.js** 
- This is the main entry point of the app.
- Retrieves the information of the previous authenticated user from the local storage and verifies its authenticity with the backend
 - Handles login and logouts
 - coordinates the rendering of the page
 - 
#### Components folder
- This contains the reusable components such as:
  **Layout.js**: Used to show the default layout with sidebar navigation and header, displayed to authenticated users.
#### **Pages folder** 
- Contains the main page components that represent different views or screens in the application.
- Each page is a full-screen component that handles specific functionality and user interactions.
- The pages include:
  - **Login.js**: Authentication page where users enter their credentials to access the system.
  - **Dashboard.js**: Overview page showing system statistics, recent activities, and quick access to main features.
  - **Alumni.js**: Alumni directory page that fetches and displays alumni records from the backend, with options to view, edit, or delete profiles.
  - **Analytics.js**: AI-powered analytics page allowing users to query alumni data using natural language and view results.
  - **DataCollection.js**: Data collection page for manual entry of alumni information or initiating automated web research collection.

#### Utils folder
- Contains utility functions and configurations shared across the application.
- The main file is:
  - **api.js**: Centralizes API endpoint URLs and configurations, using environment variables for base URLs to support different environments (development, production).


### Backend
- The backend is built with **FastAPI** and **SQLAlchemy**, providing RESTful APIs for data management and processing.
```
backend/
├── Dockerfile                    # Containerization for deployment
├── main.py                       # Application launcher (runs uvicorn)
├── requirements.txt              # Python dependencies
├── src/
│   ├── api/                      # FastAPI routers and endpoints
│   │   ├── main.py               # Main API app and router registration
│   │   ├── alumni.py             # Alumni CRUD operations
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── collection.py         # Data collection management
│   │   ├── export.py             # Data export functionality
│   │   ├── health.py             # Health check endpoint
│   │   ├── query.py              # AI-powered query processing
│   │   ├── stats.py              # Statistics and analytics
│   │   ├── upload.py             # File upload handling
│   │   └── utils.py              # API helper functions
│   ├── config/
│   │   └── settings.py           # Application configuration
│   ├── database/
│   │   ├── connection.py         # Database connection setup
│   │   ├── init_db.py            # Database initialization
│   │   ├── models.py             # SQLAlchemy models
│   │   └── repository.py         # Data access layer
│   ├── models/
│   │   ├── alumni.py             # Alumni data models
│   │   └── user.py               # User data models
│   └── services/
│       ├── ai_query_service.py   # AI query processing
│       ├── ai_verification.py    # AI-powered verification
│       ├── alumni_collector.py   # Alumni data collection
│       ├── brightdata_parser.py  # BrightData response parsing
│       ├── brightdata_service.py # BrightData API integration
│       ├── export_service.py     # Data export logic
│       ├── linkedin_official_api.py # LinkedIn API integration
│       ├── search_service.py     # Search functionality
│       ├── update_service.py     # Data update operations
│       └── web_research_service.py # Web research capabilities
└── tests/                        # Unit and integration tests
```

#### API folder
- Contains FastAPI router modules that define the REST API endpoints organized by functionality.
- **main.py**: Central FastAPI application setup with CORS middleware, authentication utilities, and legacy endpoint implementations. Includes modular router registration and serves as the main API entry point with comprehensive endpoint coverage.
- **alumni.py**: Alumni CRUD operations router providing endpoints for retrieving, viewing, and deleting individual alumni profiles, with proper error handling and data formatting.
- **auth.py**: Authentication router handling JWT token-based login, user verification, and current user information retrieval using secure password validation.
- **collection.py**: Background data collection router managing asynchronous alumni data gathering tasks with progress tracking, supporting multiple collection methods (BrightData, web research).
- **export.py**: Data export and dashboard router providing Excel/CSV export functionality with filtering options, recent alumni listings, and dashboard statistics endpoints.
- **health.py**: System health monitoring router with database connectivity checks and alumni count reporting for operational status assessment.
- **query.py**: AI-powered query router handling natural language processing for alumni data queries using OpenAI GPT-4 and web research capabilities for enhanced data discovery.
- **stats.py**: Statistics and analytics router providing distribution analysis for industries, companies, locations, and comprehensive alumni statistics for data insights.
- **upload.py**: File upload router for bulk alumni name processing from Excel/CSV files with optional automatic data collection integration.
- **utils.py**: API utility functions including standardized alumni data formatting for consistent JSON responses across all endpoints.

| File | Endpoint | Method | Description |
|------|----------|--------|-------------|
| **main.py** | `/` | GET | Welcome message and API information |
| | `/alumni/{id}` | PUT | Update an existing alumni profile |
| | `/search` | GET | Search alumni with advanced filters and pagination |
| | `/manual-collect` | POST | Manually add alumni profile data |
| | `/update` | POST | Update existing alumni profiles with fresh data |
| **alumni.py** | `/alumni` | GET | Retrieve all alumni profiles with optional filtering |
| | `/alumni/{id}` | GET | Get specific alumni profile by ID |
| | `/alumni/{id}` | DELETE | Delete an alumni profile by ID |
| **auth.py** | `/auth/login` | POST | User authentication with JWT token generation |
| | `/auth/me` | GET | Get current authenticated user information |
| **collection.py** | `/collect` | POST | Start background data collection task |
| | `/collect/status/{task_id}` | GET | Check status of data collection task |
| **export.py** | `/dashboard/stats` | GET | Get dashboard statistics and overview data |
| | `/dashboard/export` | GET | Export dashboard data in various formats |
| | `/dashboard/recent` | GET | Get recently added or updated alumni profiles |
| | `/dashboard/collect` | POST | Trigger data collection from dashboard |
| | `/export` | GET | Export alumni data to Excel/CSV with filters |
| | `/recent` | GET | Get recently added alumni profiles |
| **health.py** | `/health` | GET | System health check and database connectivity status |
| **query.py** | `/query` | POST | Process natural language queries using AI |
| | `/web-research` | POST | Perform web research for alumni information |
| **stats.py** | `/stats` | GET | Get comprehensive alumni statistics and analytics |
| | `/industries` | GET | Get distribution of alumni across different industries |
| | `/companies` | GET | Get list of top companies where alumni work |
| | `/locations` | GET | Get geographical distribution of alumni |
| **upload.py** | `/upload-names` | POST | Upload Excel/CSV files with alumni names for processing |

#### Config folder
- Holds application configuration settings, such as database URLs, API keys, and environment variables.

#### Database folder
- Manages database connections, schema definitions, and data access operations using SQLAlchemy ORM.
- **connection.py**: Manages database connections and sessions using SQLAlchemy. Sets up a SQLite database for development with connection pooling, creates all database tables, and automatically adds default users (admin and faculty) if the database is empty. Provides session management utilities for database operations.
- **init_db.py**: A standalone database initialization script that creates all database tables and adds initial user data. Can be run independently to set up the database schema and populate it with default admin and faculty users. Includes proper logging for initialization status.
- **models.py**: Defines the SQLAlchemy database models (tables) using declarative base. Contains four main models: UserDB (user accounts with roles), AlumniProfileDB (main alumni profile data), WorkHistoryDB (employment history), and DataSourceDB (data collection sources and metadata).
  ```mermaid
  erDiagram
      UserDB {
          int id PK
          string email UK
          string password_hash
          string name
          UserRole role
          datetime created_at
          datetime last_login
      }
      
      AlumniProfileDB {
          int id PK
          string full_name
          int graduation_year
          string current_job_title
          string current_company
          string industry
          string location
          string linkedin_url
          float confidence_score
          datetime last_updated
          datetime created_at
      }
      
      WorkHistoryDB {
          int id PK
          int alumni_id FK
          string job_title
          string company
          date start_date
          date end_date
          bool is_current
          string industry
          string location
      }
      
      DataSourceDB {
          int id PK
          int alumni_id FK
          string source_type
          string source_url
          text data_collected
          datetime collection_date
          float confidence_score
      }
      
      AlumniProfileDB ||--o{ WorkHistoryDB : "has many"
      AlumniProfileDB ||--o{ DataSourceDB : "has many"
  ```
- **repository.py**: Contains the AlumniRepository class that serves as the data access layer. Provides comprehensive CRUD operations for alumni profiles including create, read, update, delete, and search functionality. Handles work history and data source management, with conversion between database models and application domain models.
  ```mermaid
  flowchart TD
      A[AlumniRepository] --> B{CRUD Operation}
      
      B -->|Create| C[create_alumni]
      B -->|Read| D[get_alumni_by_id]
      B -->|Read| E[get_alumni_by_name]
      B -->|Read| F[search_alumni]
      B -->|Read| G[get_all_alumni]
      B -->|Update| H[update_alumni]
      B -->|Delete| I[delete_alumni]
      
      C --> J[Convert to DB Model]
      J --> K[Add Work History]
      K --> L[Add Data Sources]
      L --> M[Commit to DB]
      
      D --> N[Query by ID]
      E --> O[Query by Name]
      F --> P[Apply Filters]
      G --> Q[Query All with Pagination]
      
      H --> R[Update Fields]
      R --> S[Update Work History]
      S --> T[Commit Changes]
      
      I --> U[Delete Record]
      U --> V[Commit Deletion]
      
      M --> W[Return AlumniProfile]
      N --> W
      O --> W
      P --> W
      Q --> W
      T --> W
      V --> W
  ```

#### Models folder
- Defines Pydantic-style data models for application domain objects with validation and type safety.
- **alumni.py**: Contains core alumni data models including IndustryType enum, JobPosition dataclass for employment records, DataSource dataclass for tracking data collection origins, and AlumniProfile dataclass as the main alumni data structure with comprehensive validation and business logic methods.
```plantuml
@startuml Alumni Data Models
enum IndustryType {
    TECHNOLOGY
    FINANCE
    HEALTHCARE
    EDUCATION
    CONSULTING
    MINING
    GOVERNMENT
    NON_PROFIT
    RETAIL
    MANUFACTURING
    OTHER
}

class JobPosition {
    +title: str
    +company: str
    +start_date: date?
    +end_date: date?
    +is_current: bool
    +industry: str?
    +location: str?
    +__post_init__()
}

class DataSource {
    +source_type: str
    +source_url: str?
    +collection_date: datetime
    +confidence_score: float
    +__post_init__()
}

class AlumniProfile {
    +id: int?
    +full_name: str
    +graduation_year: int?
    +current_position: JobPosition?
    +work_history: List[JobPosition]
    +location: str?
    +industry: IndustryType?
    +linkedin_url: str?
    +confidence_score: float
    +last_updated: datetime
    +data_sources: List[DataSource]
    +__post_init__()
    +add_job_position()
    +get_current_job()
    +get_industry_from_current_job()
}

AlumniProfile --> JobPosition : current_position
AlumniProfile --> "*" JobPosition : work_history
AlumniProfile --> "*" DataSource : data_sources
AlumniProfile --> IndustryType : industry
@enduml
```
- **user.py**: Contains the User model extending UserDB with password hashing/verification using bcrypt, and utility methods for API serialization and authentication.
```plantuml
@startuml User Data Models
class UserDB {
    +id: int
    +email: str
    +password_hash: str
    +name: str
    +role: UserRole
    +created_at: datetime
    +last_login: datetime?
}

class User {
    +set_password(password: str)
    +check_password(password: str): bool
    +to_dict(): dict
}

User --|> UserDB : extends
@enduml
```

#### Services folder
- Contains business logic services for data collection, AI processing, export, and external API integrations.
- Includes services for BrightData, LinkedIn API, web research, and AI verification.

##### **ai_query_service.py**
- Handles AI-powered natural language queries, converting user questions into structured database queries using OpenAI GPT-4 for intelligent alumni data analysis and filtering.
```mermaid
sequenceDiagram
    participant User
    participant API
    participant AIQueryService
    participant OpenAI
    participant Database
    participant SearchService

    User->>API: POST /query (natural language question)
    API->>AIQueryService: process_query(question)
    AIQueryService->>OpenAI: Generate structured query from natural language
    OpenAI-->>AIQueryService: Structured query parameters
    AIQueryService->>SearchService: execute_structured_query(params)
    SearchService->>Database: Execute optimized query
    Database-->>SearchService: Alumni results
    SearchService-->>AIQueryService: Filtered results
    AIQueryService-->>API: Formatted response
    API-->>User: Alumni data with insights
```

##### **ai_verification.py**
- Performs AI-powered verification of alumni profiles, using OpenAI to match and validate profile data with confidence scoring for data quality assurance.
```mermaid
flowchart TD
    A[New Profile Data] --> B{Data Source}
    B -->|BrightData| C[Extract LinkedIn Data]
    B -->|Web Research| D[Extract Web Data]
    B -->|Manual Entry| E[Validate Manual Data]

    C --> F[ai_verification.py]
    D --> F
    E --> F

    F --> G[Generate Verification Prompt]
    G --> H[OpenAI GPT-4 Analysis]
    H --> I{Confidence Score}

    I -->|High ≥0.8| J[Auto-Approve Profile]
    I -->|Medium 0.5-0.8| K[Flag for Review]
    I -->|Low <0.5| L[Reject Profile]

    J --> M[Save to Database]
    K --> N[Human Review Queue]
    L --> O[Discard Data]

    M --> P[Return Verified Profile]
    N --> P
    O --> Q[Log Rejection]
```

##### **alumni_collector.py**
- Orchestrates multiple data collection methods, coordinating between manual entry, web research, BrightData scraping, and LinkedIn API to gather comprehensive alumni information.
```plantuml
@startuml Alumni Collector State Diagram
[*] --> CollectionRequest : Alumni names list

state DataCollection as "Data Collection Methods" {
    [*] --> Orchestrator : alumni_collector.py
    Orchestrator --> Manual : Manual Entry
    Orchestrator --> WebResearch : Web Research
    Orchestrator --> BrightData : BrightData Scraping
    Orchestrator --> LinkedInAPI : LinkedIn Official API
    
    Manual --> Aggregator : Profile Data
    WebResearch --> Aggregator : Profile Data
    BrightData --> Aggregator : Profile Data
    LinkedInAPI --> Aggregator : Profile Data
    
    Aggregator --> Deduplication : Remove duplicates
    Deduplication --> Validation : AI Verification
    Validation --> Database : Save profiles
}

CollectionRequest --> DataCollection
DataCollection --> [*] : Collection complete
@enduml
```

##### **brightdata_parser.py**
- Parses BrightData API responses, converting raw scraped data into structured AlumniProfile objects with proper data validation and formatting.
```mermaid
flowchart TD
    A[BrightData API Response] --> B{Response Status}
    B -->|Success| C[Extract JSON Data]
    B -->|Error| D[Handle API Error]

    C --> E[brightdata_parser.py]
    E --> F[Parse Profile Fields]
    F --> G[Extract Job History]
    F --> H[Extract Education]
    F --> I[Extract Contact Info]

    G --> J[Validate Job Data]
    H --> K[Validate Education Data]
    I --> L[Validate Contact Data]

    J --> M[Map to JobPosition]
    K --> N[Map to Education Records]
    L --> O[Map to Contact Info]

    M --> P[Create AlumniProfile]
    N --> P
    O --> P

    P --> Q[Calculate Confidence Score]
    Q --> R[Add Data Source Metadata]
    R --> S[Return Structured Profile]

    D --> T[Log Error Details]
    T --> U[Return Error Response]
```

##### **brightdata_service.py**
- Manages LinkedIn scraping via BrightData API, handling authentication, rate limiting, and data collection from LinkedIn profiles with anti-detection measures.
```mermaid
sequenceDiagram
    participant Client
    participant BrightDataService
    participant BrightDataAPI
    participant RateLimiter
    participant AntiDetection

    Client->>BrightDataService: scrape_linkedin_profile(url)
    BrightDataService->>RateLimiter: check_rate_limit()
    RateLimiter-->>BrightDataService: OK/Proceed

    BrightDataService->>AntiDetection: apply_stealth_measures()
    AntiDetection-->>BrightDataService: Stealth headers applied

    BrightDataService->>BrightDataAPI: POST scraping request
    BrightDataAPI-->>BrightDataService: Job accepted

    BrightDataService->>BrightDataService: Poll for completion
    loop Polling
        BrightDataService->>BrightDataAPI: GET job status
        BrightDataAPI-->>BrightDataService: Status update
    end

    BrightDataService->>BrightDataAPI: GET results
    BrightDataAPI-->>BrightDataService: Raw profile data

    BrightDataService-->>Client: Parsed profile data
```

##### **export_service.py**
- Handles exporting alumni data to Excel and CSV formats, including work history, summary statistics, and filtered exports with customizable formatting options.
```mermaid
flowchart TD
    A[Export Request] --> B{Export Type}
    B -->|Excel| C[Generate XLSX]
    B -->|CSV| D[Generate CSV]

    C --> E[Create Workbook]
    D --> F[Create CSV Writer]

    E --> G[Query Alumni Data]
    F --> G

    G --> H[Apply Filters]
    H --> I[Format Data]

    I --> J{Include Work History?}
    J -->|Yes| K[Add Work History Sheet]
    J -->|No| L[Skip Work History]

    K --> M[Add Summary Statistics]
    L --> M

    M --> N[Apply Styling]
    N --> O[Save File]

    O --> P[Return File URL]
```

##### **linkedin_official_api.py**
- Integrates with LinkedIn's official Partner APIs for compliant data collection, including people search and profile details with rate limiting and industry mapping.
```mermaid
sequenceDiagram
    participant App
    participant LinkedInService
    participant LinkedInAPI
    participant TokenManager
    participant RateLimiter

    App->>LinkedInService: search_people(query)
    LinkedInService->>TokenManager: get_access_token()
    TokenManager-->>LinkedInService: Valid OAuth token

    LinkedInService->>RateLimiter: check_api_limits()
    RateLimiter-->>LinkedInService: Within limits

    LinkedInService->>LinkedInAPI: GET /people/search
    LinkedInAPI-->>LinkedInService: Search results

    LinkedInService->>LinkedInService: Map industry codes
    LinkedInService->>LinkedInService: Format response

    LinkedInService-->>App: Structured alumni data
```

##### **search_service.py**
- Provides optimized search functionality for alumni data, including filtering, statistics, and distribution analysis across industries, locations, and companies.
```mermaid
flowchart TD
    A[Search Request] --> B{Request Type}

    B -->|Basic Search| C[Parse Search Filters]
    B -->|Statistics| D[Parse Stat Parameters]
    B -->|Analytics| E[Parse Analytics Filters]

    C --> F[Build SQL Query]
    D --> G[Build Aggregation Query]
    E --> H[Build Analytics Query]

    F --> I[Execute Query]
    G --> I
    H --> I

    I --> J[Database]
    J --> K[Process Results]

    K --> L{Result Type}
    L -->|Search Results| M[Format Alumni List]
    L -->|Statistics| N[Format Statistics]
    L -->|Analytics| O[Format Analytics]

    M --> P[Return Response]
    N --> P
    O --> P
```

##### **update_service.py**
- Manages updating existing alumni profiles with fresh data from BrightData, including batch updates, scheduling, and statistics on profile freshness and data quality.
```plantuml
@startuml Update Service State Diagram
[*] --> ScheduledUpdate : Daily/Weekly trigger
[*] --> ManualUpdate : Admin request

ScheduledUpdate --> UpdateService : update_service.py
ManualUpdate --> UpdateService

state UpdateService as "Update Process" {
    [*] --> IdentifyStale : Find profiles >30 days old
    IdentifyStale --> FetchFreshData : Query BrightData API
    FetchFreshData --> CompareData : Compare with existing
    CompareData --> MergeUpdates : Merge new information
    MergeUpdates --> ValidateChanges : AI verification
    ValidateChanges --> UpdateDatabase : Save changes
    UpdateDatabase --> LogUpdate : Record update statistics
}

UpdateService --> [*] : Update complete

note right of UpdateService
    Batch processing with
    progress tracking
end note
@enduml
```

##### **web_research_service.py**
- Performs web research using DuckDuckGo search to find professional information about alumni, including LinkedIn profiles and ECU connections through HTML parsing.
```mermaid
flowchart TD
    A[Alumni Name] --> B[web_research_service.py]
    B --> C[Generate Search Queries]
    C --> D["ECU + [Name] + Alumni"]
    C --> E["[Name] + LinkedIn"]
    C --> F["[Name] + Professional"]

    D --> G[DuckDuckGo Search]
    E --> G
    F --> G

    G --> H[Parse HTML Results]
    H --> I[Extract Professional Info]
    I --> J[Validate ECU Connection]
    I --> K[Extract LinkedIn URLs]
    I --> L[Extract Job Information]

    J --> M[Filter Relevant Data]
    K --> M
    L --> M

    M --> N[Calculate Confidence Score]
    N --> O[Create Data Source Records]
    O --> P[Return Research Results]
```

## Technologies Used

### Frontend Technologies
- **React**: JavaScript library for building user interfaces
- **Material-UI (MUI)**: React component library for consistent UI design
- **Axios**: HTTP client for making API requests
- **React Scripts**: Build and development scripts for React applications

### Backend Technologies
- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Uvicorn**: ASGI web server for running FastAPI applications
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) for Python
- **Pydantic**: Data validation and settings management using Python type annotations
- **Pandas**: Data manipulation and analysis library
- **OpenPyXL**: Library for reading and writing Excel files
- **BeautifulSoup4**: HTML and XML parsing library
- **BrightData**: Web scraping and data collection service
- **LinkedIn Official API**: Professional networking platform API
- **DuckDuckGo**: Search engine for web research
- **OpenAI GPT-4**: AI language model for query processing and verification
- **Requests**: HTTP library for Python
- **OpenAI**: Python client for OpenAI API
- **Celery**: Distributed task queue for asynchronous processing
- **Redis**: In-memory data structure store for caching and message brokering
- **Python-dotenv**: Loads environment variables from .env files
- **Python-multipart**: Streaming multipart parser for Python
- **Pytest**: Testing framework for Python
- **Pytest-asyncio**: Pytest plugin for testing async code

### Development and Deployment Tools
- **Docker**: Containerization platform for packaging applications
- **Git**: Version control system
- **Mermaid & PlantUML**: Text-based diagramming tools for creating flowcharts, sequence diagrams, class diagrams, and state diagrams
- **SQLite/PostgreSQL**: Database systems (SQLite for development, PostgreSQL for production)


