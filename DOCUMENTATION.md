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
    C --> D[(MySQL)]
    
    B --> E[Alumni Collector]
    E --> F[Web Research Service]
    E --> G[Manual Entry]
    
    F <--> H[DuckDuckGo Search]
    F <--> I[BeautifulSoup Parser]
    F <--> J[AI Verification Service]
    
    J --> OpenAI[OpenAI GPT-4]
    
    B --> K[Search Service]
    B --> L[Export Service]
    B --> M[Update Service]
    
    N[CLI Tools] --> B
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
- The backend is built with **FastAPI** and **SQLAlchemy**, providing RESTful APIs for data management and processing. We also used external services and APIs like **DuckDuckGo**, **BeautifulSoup**, and LLMs like **OpenAI GPT-4o-mini**
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
│       ├── export_service.py     # Data export logic
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
- **collection.py**: Background data collection router managing asynchronous alumni data gathering tasks with progress tracking, supporting web research collection methods.
- **export.py**: Data export and dashboard router providing Excel/CSV export functionality with filtering options, recent alumni listings, and dashboard statistics endpoints.
- **health.py**: System health monitoring router with database connectivity checks and alumni count reporting for operational status assessment.
- **query.py**: AI-powered query router handling natural language processing for alumni data queries using OpenAI GPT-4o-mini and web research capabilities for enhanced data discovery.
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
| | `/dashboard/graduation-years` | GET | Get distribution of alumni by graduation year |
| | `/dashboard/confidence-scores` | GET | Get distribution of alumni confidence scores in ranges |
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

#### Task Collection System
- Manages asynchronous background tasks for alumni data collection, providing progress tracking and persistence across application restarts.
- **Task Management**: Uses database-backed task storage with unique UUID identifiers, status tracking, and result persistence. Supports both web research and manual collection methods with comprehensive error handling and progress reporting.

**Task Database Model (TaskDB)**:
- `id`: UUID primary key for unique task identification
- `status`: Current task state (running/completed/failed)
- `names`: JSON array of input names to process
- `method`: Collection method (web-research/manual)
- `start_time`: Task initiation timestamp
- `end_time`: Task completion timestamp
- `results_count`: Number of successful profiles collected
- `results`: JSON array of formatted alumni profiles
- `failed_names`: JSON array of names that failed collection with reasons
- `error`: General error message if task failed



#### Database folder
- Manages database connections, schema definitions, and data access operations using SQLAlchemy ORM with MySQL.
- **connection.py**: Manages database connections and sessions using SQLAlchemy. Sets up a MySQL database connection with SSL encryption, creates all database tables, and automatically adds default users (admin and faculty) if the database is empty. Provides session management utilities for database operations.
- **init_db.py**: A standalone database initialization script that creates all database tables and adds initial user data. Can be run independently to set up the database schema and populate it with default admin and faculty users. Includes proper logging for initialization status.
- **models.py**: Defines the SQLAlchemy database models (tables) using declarative base. Contains five main models: UserDB (user accounts with roles), AlumniProfileDB (main alumni profile data), WorkHistoryDB (employment history), EducationDB (education history), DataSourceDB (data collection sources and metadata), and TaskDB (background collection tasks).
```plantuml
@startuml Database ER Diagram
entity UserDB {
    * id : int <<PK>>
    --
    * email : string <<UK>>
    * password_hash : string
    * name : string
    * role : UserRole
    * created_at : datetime
    * last_login : datetime?
}

entity AlumniProfileDB {
    * id : int <<PK>>
    --
    full_name : string
    graduation_year : int
    current_job_title : string
    current_company : string
    industry : string
    location : string
    linkedin_url : string
    confidence_score : float
    last_updated : datetime
    * created_at : datetime
}

entity WorkHistoryDB {
    * id : int <<PK>>
    --
    * alumni_id : int <<FK>>
    job_title : string
    company : string
    start_date : date
    end_date : date
    is_current : bool
    industry : string
    location : string
}

entity EducationDB {
    * id : int <<PK>>
    --
    * alumni_id : int <<FK>>
    institution : string
    degree : string
    field_of_study : string
    graduation_year : int
    start_year : int
}

entity DataSourceDB {
    * id : int <<PK>>
    --
    * alumni_id : int <<FK>>
    source_type : string
    source_url : string
    data_collected : text
    collection_date : datetime
    confidence_score : float
}

entity TaskDB {
    * id : string <<PK>>
    --
    status : string
    names : text
    method : string
    start_time : datetime
    end_time : datetime?
    results_count : int
    results : text
    failed_names : text
    error : text
}

UserDB ||..o{ AlumniProfileDB : "manages"
AlumniProfileDB ||..o{ WorkHistoryDB : "has many"
AlumniProfileDB ||..o{ EducationDB : "has many"
AlumniProfileDB ||..o{ DataSourceDB : "has many"

note right of UserDB : User accounts with roles
note right of AlumniProfileDB : Main alumni profile data
note right of WorkHistoryDB : Employment history records
note right of EducationDB : Education history records
note right of DataSourceDB : Data collection sources
note right of TaskDB : Background collection tasks
@enduml
```
- **repository.py**: Contains the AlumniRepository class that serves as the data access layer. Provides comprehensive CRUD operations for alumni profiles including create, read, update, delete, and advanced search functionality with multiple filter criteria. Handles work history, education history, and data source management, with robust conversion between database models and application domain models. Includes data validation, pagination support, and proper error handling.
```plantuml
@startuml AlumniRepository Operations
left to right direction
class AlumniRepository {
    +create_alumni(alumni: AlumniProfile): AlumniProfile
    +get_alumni_by_id(alumni_id: int): AlumniProfile?
    +get_alumni_by_name(name: str): List[AlumniProfile]
    +search_alumni(name?, industry?, company?, location?, graduation_year_min?, graduation_year_max?): List[AlumniProfile]
    +get_all_alumni(limit?, offset): List[AlumniProfile]
    +update_alumni(alumni: AlumniProfile): AlumniProfile
    +delete_alumni(alumni_id: int): bool
    +add_work_history(alumni_id: int, job: JobPosition)
    +add_education_history(alumni_id: int, education: Education)
    +add_data_source(alumni_id: int, source: DataSource)
    -convert_db_to_alumni_profile(db_alumni: AlumniProfileDB): AlumniProfile
}

note right of AlumniRepository
    Data Access Layer
    Handles CRUD operations
    Manages relationships
    Converts between models
    Includes validation
end note

AlumniRepository --> AlumniProfileDB : creates/updates
AlumniRepository --> WorkHistoryDB : manages
AlumniRepository --> EducationDB : manages
AlumniRepository --> DataSourceDB : manages

package "Database Operations" as DB_OPS {
    class CreateOperation {
        +Validate Input Data
        +Convert to DB Model
        +Add Work History
        +Add Education History
        +Add Data Sources
        +Commit to DB
    }
    
    class ReadOperations {
        +Query by ID
        +Query by Name (Partial Match)
        +Advanced Search with Filters
        +Query All with Pagination
        +Convert to Domain Model
    }
    
    class UpdateOperation {
        +Validate Alumni ID
        +Update Basic Fields
        +Replace Work History
        +Replace Education History
        +Commit Changes
    }
    
    class DeleteOperation {
        +Delete Record
        +Cascade Delete Related Data
        +Commit Deletion
    }
    
    class HelperOperations {
        +Add Work History Entry
        +Add Education History Entry
        +Add Data Source Entry
    }
}

AlumniRepository --> CreateOperation : uses
AlumniRepository --> ReadOperations : uses
AlumniRepository --> UpdateOperation : uses
AlumniRepository --> DeleteOperation : uses
AlumniRepository --> HelperOperations : uses

CreateOperation --> AlumniProfile : returns
ReadOperations --> AlumniProfile : returns
UpdateOperation --> AlumniProfile : returns
DeleteOperation --> "boolean" : returns
@enduml
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
- Includes services for web research and AI verification.

##### **ai_query_service.py**
- Handles AI-powered natural language queries, converting user questions into structured database queries using OpenAI GPT-4o-mini for intelligent alumni data analysis and filtering.
```plantuml
@startuml AI Query Service Sequence Diagram
participant User
participant API
participant AIQueryService
participant OpenAI
participant SearchService
database Database

User -> API: POST /query\n"<b>Show me mining sector graduates</b>\n <b> from Perth working at Rio Tinto"
API -> AIQueryService: process_query("\nShow me mining sector graduates\nfrom Perth working at Rio Tinto")
AIQueryService -> OpenAI: Generate structured query\n from natural language
note right: Prompt: "Convert this natural language query...\nReturn only valid JSON with parameters"
OpenAI --> AIQueryService: {\n"industry": "Mining", \n"location": "Perth", \n"company": "Rio Tinto"}
AIQueryService -> SearchService: execute_structured_query\n({"industry": "Mining", "location": "Perth", "company": "Rio Tinto"})
SearchService -> Database: SELECT * FROM alumni_profiles\nWHERE industry = 'Mining'\nAND location LIKE '%Perth%'\nAND current_company LIKE '%Rio Tinto%'
Database --> SearchService: [AlumniProfile(\nid=123, \nname="John Smith", \nindustry="Mining", \nlocation="Perth", \ncurrent_company="Rio Tinto")]
SearchService --> AIQueryService: [{"\nid": 123, \n"name": "John Smith", \n"industry": "Mining", \n"location": "Perth", \n"current_job": {"title": "Senior Engineer", \n"company": "Rio Tinto"}}]
AIQueryService --> API: {"query": "Show me mining sector graduates \nfrom Perth working at Rio Tinto", \n"results": [{"id": 123, "name": "John Smith", \n"industry": "Mining", "location": "Perth", \n"current_job": {"title": "Senior Engineer", \n"company": "Rio Tinto"}}], "count": 1}
API --> User: {"results": [{"name": "John Smith", \n"industry": "Mining", "location": "Perth", \n"current_job": {"title": "Senior Engineer", \n"company": "Rio Tinto"}}], "count": 1}
@enduml
```

##### **ai_verification.py**
- Performs AI-powered verification of alumni profiles using OpenAI GPT-4o-mini, with comprehensive industry normalization and confidence scoring for data quality assurance.
```plantuml
@startuml AI Verification Service Flowchart
title AI Verification Service Process Flow

start

:New Profile Data
{name: "John Smith", company: "Rio Tinto", title: "Senior Engineer"};

if (OpenAI API Available?) then (Yes)
  :AIVerificationService.verify_profile_match()
  Generate AI Prompt with target person and scraped data;
  note right
    **AI Analysis Criteria:**
    - Name similarity (exact match, nicknames)
    - Location consistency (Australian preferred)
    - Education timing alignment
    - Career progression plausibility
    - Overall profile coherence
  end note
  
  :Call OpenAI GPT-4o-mini API
  Model: gpt-4o-mini, Temperature: 0.1, Max tokens: 500;
  
  :Parse JSON Response
  {is_match: true/false, confidence_score: 0.0-1.0, reason: "...", extracted_info: {...}};
  
  if (JSON Parse Success?) then (Yes)
    :Return VerificationResult
    is_match, confidence_score, reason, extracted_info;
  else (No)
    :Fallback to Basic Verification;
  endif
  
elseif (No)
  :Basic Verification (No AI)
  Name similarity calculation + location matching;
  note right
    **Basic Scoring:**
    - Name similarity: 70% weight
    - Location match: +30% bonus
    - Match threshold: >0.6 confidence
  end note
endif

:Industry Normalization
Map scraped industry to IndustryType enum using comprehensive mapping;
note right
    **Supported Industries:**
    Technology, Finance, Healthcare, Education,
    Consulting, Mining, Government, Non-Profit,
    Retail, Manufacturing, Other
end note

:Return VerificationResult
{is_match: bool, confidence_score: float, reason: str, extracted_info: dict};

stop

legend right
  **Verification Features:**
  - OpenAI GPT-4o-mini integration
  - Industry normalization mapping
  - Confidence scoring (0.0-1.0)
  - Fallback basic verification
  - Australian alumni focus
  - Conservative matching to avoid false positives
endlegend
@enduml
```

**Key Methods:**
- `verify_profile_match()`: Main verification method using AI analysis
- `normalize_industry()`: Maps industry strings to standardized IndustryType enum values
- `convert_web_data_to_profile()`: Converts unstructured web research into structured AlumniProfile objects
- `enhance_profile_data()`: Uses AI to clean and enhance scraped profile data
- `basic_verification()`: Fallback verification without AI using name/location matching

**Industry Mapping Examples:**
- "Information Technology" → "Technology"
- "Financial Services" → "Finance" 
- "Mining & Resources" → "Mining"
- "Government Administration" → "Government"
- Unknown industries → "Other"

##### **alumni_collector.py**
- Orchestrates data collection methods, coordinating between manual entry and web research to gather comprehensive alumni information.
```plantuml
@startuml Alumni Collector State Diagram
[*] --> CollectionRequest : Alumni names list

state DataCollection as "Data Collection Methods" {
    [*] --> Orchestrator : alumni_collector.py
    Orchestrator --> Manual : Manual Entry
    Orchestrator --> WebResearch : Web Research
    
    Manual --> Aggregator : Profile Data
    WebResearch --> Aggregator : Profile Data
    
    Aggregator --> Deduplication : Remove duplicates
    Deduplication --> Validation : AI Verification
    Validation --> Database : Save profiles
}

CollectionRequest --> DataCollection
DataCollection --> [*] : Collection complete
@enduml
```

##### **export_service.py**
- Handles exporting alumni data to Excel and CSV formats, including work history, summary statistics, and filtered exports with customizable formatting options.
```plantuml
@startuml Export Service Flowchart
title Export Service Process Flow

start

:Export Request
{type: "excel", filters: {...}};

if (Export Type?) then (Excel)
  :Generate XLSX Workbook;
  :Create Excel Writer;
else (CSV)
  :Generate CSV File;
  :Create CSV Writer;
endif

:Query Alumni Data
from database with filters;

:Apply Additional Filters
(date range, industry, location);

:Format Data Structure
Convert to export format;

if (Include Work History?) then (Yes)
  :Add Work History Sheet
  Include employment timeline;
else (No)
  :Skip Work History
  Basic profile only;
endif

:Add Summary Statistics
(count, averages, distributions);

:Apply Styling & Formatting
(headers, colors, borders);

:Save File to Storage
Generate unique filename;

:Return File URL
{url: "/exports/file.xlsx", size: "2.3MB"};

stop

legend right
  **Export Options:**
  - Excel: Multi-sheet workbook with formatting
  - CSV: Simple tabular format
  - Filters: Date, industry, location, graduation year
  - Includes: Work history, statistics, custom formatting
endlegend
@enduml
```

##### **search_service.py**
- Provides optimized search functionality for alumni data, including filtering, statistics, and distribution analysis across industries, locations, and companies.
```plantuml
@startuml Search Service Flowchart
title Search Service Process Flow

start

:Search Request
{type: "basic", filters: {...}};

switch (Request Type?)
case (Basic Search)
  :Parse Filters;
  :Build SQL Query;
case (Statistics)
  :Parse Parameters;
  :Build Aggregation Query;
case (Analytics)
  :Parse Filters;
  :Build Analytics Query;
endswitch

:Execute Query;
:Query Database;

:Process Results;

switch (Result Type?)
case (Search Results)
  :Format Alumni List;
case (Statistics)
  :Format Statistics;
case (Analytics)
  :Format Analytics;
endswitch

:Return Response;
stop

legend right
  **Search Types:**
  - Basic: Filtered alumni search
  - Statistics: Industry/company distributions
  - Analytics: Trends and insights
endlegend
@enduml
```

##### **update_service.py**
- Manages updating existing alumni profiles with fresh data from web research, including batch updates, scheduling, and statistics on profile freshness and data quality.
```plantuml
@startuml Update Service State Diagram
[*] --> ScheduledUpdate : Daily/Weekly trigger
[*] --> ManualUpdate : Admin request

ScheduledUpdate --> UpdateService : update_service.py
ManualUpdate --> UpdateService

state UpdateService as "Update Process" {
    [*] --> IdentifyStale : Find profiles >30 days old
    IdentifyStale --> FetchFreshData : Query web research
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
```plantuml
@startuml Web Research Service Flow
title Web Research Service Process Flow

start

partition "Input Processing" as Input {
  :**Receive Alumni Name**\ntarget_name (string);
  note right : e.g., "John Smith"
}

partition "Query Generation" as QueryGen {
  :**Generate Search Queries**\nCreate multiple query variations;
  note right
    **Query Types Generated:**
    1. "ECU + [Name] + Alumni"
    2. "[Name] + LinkedIn Australia"
    3. "[Name] + Professional"
  end note

  :**Query Examples**\n"John Smith ECU Edith Cowan University"\n"John Smith LinkedIn Australia"\n"John Smith professional";
}

partition "Web Search Execution" as Search {
  :**Execute DuckDuckGo Search**\nDuckDuckGo HTML Search API;
  note right
    **Search Parameters:**
    - q: generated query
    - User-Agent: Browser-like headers
    - Timeout: 10 seconds
  end note

  :**Process Search Results**\nParse HTML response with BeautifulSoup\nExtract top 5-10 search results per query;
  note right
    **Result Structure:**
    - title: Page title
    - url: Result URL
    - snippet: Description text
    - source: "DuckDuckGo"
  end note
}

partition "Content Analysis" as Analysis {
  :**Extract Professional Information**\nMultiple parallel extraction tasks;

  fork
    :**Validate ECU Connection**\nCheck for "Edith Cowan" or "ECU" mentions\nSet boolean flag for alumni relevance;
  fork again
    :**Extract LinkedIn URLs**\nFind linkedin.com/in/* patterns\nValidate professional profile URLs;
  fork again
    :**Extract Job Information**\nParse current position, company, industry\nExtract career progression indicators;
  end fork

  :**Aggregate Findings**\nCombine all extracted information\nRemove duplicates and irrelevant data;
}

partition "Quality Assessment" as Quality {
  :**Calculate Confidence Score**\nWeighted scoring based on multiple factors;
  note right
    **Scoring Criteria:**
    - ECU connection: +0.3
    - LinkedIn profile: +0.4
    - Job information: +0.3
    - Total range: 0.0 - 1.0
  end note

  if (Confidence >= 0.5?) then (yes)
    :**Accept Results**\nValid research data obtained;
  else (no)
    :**Reject Results**\nInsufficient quality detected;
    note right : May trigger additional search queries
  endif
}

partition "Data Packaging" as Packaging {
  :**Create Data Source Records**\nBuild DataSource objects with metadata;
  note right
    **DataSource Fields:**
    - source_type: "web-research"
    - source_url: Original search result URL
    - collection_date: Timestamp
    - confidence_score: Calculated quality
  end note

  :**Format Response**\nStructure research results for output\nInclude extracted information and metadata;
}

partition "Output" as Output {
  :**Return Research Results**\nList of search results with extracted data\nDeliver to calling service (AI verification, update service, etc.);
}

stop

legend right
  **Process Overview:**
  1. Generate targeted search queries
  2. Execute web searches via DuckDuckGo
  3. Parse and extract professional information
  4. Assess data quality and confidence
  5. Package results for downstream processing
endlegend
@enduml
```

### Previous Data Collection Implementations (Not Used)

During the development process, we explored several external data collection services and APIs that were ultimately not implemented due to ethical, technical, or business constraints. Below, we document these implementations for reference:

#### BrightData Integration (Not Implemented - Ethical Concerns)
BrightData (formerly Luminati Networks) is a web scraping and data collection service that provides residential proxies and scraping infrastructure. We implemented a complete integration but ultimately decided not to use it due to ethical concerns around automated LinkedIn scraping.

##### **brightdata_parser.py** (Archived)
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

##### **brightdata_service.py** (Archived)
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
    BrightDataAPI-->>BrightDataAPI: Job accepted

    BrightDataService->>BrightDataService: Poll for completion
    loop Polling
        BrightDataService->>BrightDataAPI: GET job status
        BrightDataAPI-->>BrightDataService: Status update
    end

    BrightDataService->>BrightDataAPI: GET results
    BrightDataAPI-->>BrightDataService: Raw profile data

    BrightDataService-->>Client: Parsed profile data
```

**Why BrightData Was Not Used:**
- **Ethical Concerns**: Automated scraping of LinkedIn profiles violates LinkedIn's Terms of Service and raises privacy concerns
- **Legal Risks**: Potential violations of data protection laws (GDPR, CCPA) and anti-scraping regulations
- **Platform Integrity**: Undermines LinkedIn's business model and user trust
- **Detection Risks**: LinkedIn actively blocks scraping attempts, making the solution unreliable

#### LinkedIn Official API Integration (Not Implemented - Limited Functionality)
LinkedIn provides official Partner APIs for developers, but these APIs have significant limitations for alumni data collection use cases.

##### **linkedin_official_api.py** (Archived)
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

**Why LinkedIn Official API Was Not Used:**
- **Limited Data Access**: APIs only provide basic profile information (name, headline, location) - no detailed work history, education, or contact information
- **Partnership Requirements**: Requires formal partnership with LinkedIn and approval process
- **Use Case Restrictions**: APIs are designed for lead generation, job search, and profile management, not comprehensive alumni tracking
- **Cost and Complexity**: Expensive licensing fees and complex OAuth implementation
- **Rate Limiting**: Very restrictive API limits unsuitable for batch data collection

#### Updated System Architecture (Current Implementation)
After evaluating these external services, we implemented a solution using only ethical web research methods:

```mermaid
graph TB
    A[React Frontend] --> B[FastAPI Backend]
    B --> C[SQLAlchemy ORM]
    C --> D[(MySQL)]
    
    B --> E[Alumni Collector]
    E --> F[Web Research Service]
    E --> G[Manual Entry]
    
    F <--> H[DuckDuckGo Search]
    F <--> I[BeautifulSoup Parser]
    F <--> J[AI Verification Service]
    
    J --> OpenAI[OpenAI GPT-4o-mini]
    
    B --> K[Search Service]
    B --> L[Export Service]
    B --> M[Update Service]
    
    N[CLI Tools] --> B
    
    classDef deprecated fill:#ffcccc,stroke:#ff0000,stroke-dasharray: 5 5
    classDef ethical fill:#ccffcc,stroke:#00aa00
    
    class F,G,J ethical
```

**Key Lessons Learned:**
1. **Ethics First**: Prioritize ethical data collection methods over comprehensive but questionable approaches
2. **API Limitations**: Official APIs often have significant restrictions that limit their usefulness
3. **Web Research Balance**: Public web research can provide valuable insights while respecting platform terms
4. **Transparency**: Documenting failed approaches helps future developers understand decision-making processes

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
- **DuckDuckGo**: Search engine for web research
- **OpenAI GPT-4o-mini**: AI language model for query processing and verification
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
- **MySQL**: Primary database system (Aiven Cloud MySQL for both development and production)


## Deployment Architecture
We utilized **Render** for the deployment of the backend and **Vercel** for hosting the frontend. The database was hosted on **AWS** which is managed by **Aiven**

```plantuml
@startuml Deployment Diagram

title Alumni Tracking System - Production Deployment Architecture

skinparam backgroundColor #FEFEFE
skinparam componentStyle uml2
skinparam packageStyle rect

' Color scheme
skinparam package<<Development>> {
    backgroundColor #E3F2FD
    borderColor #1976D2
}
skinparam package<<Production>> {
    backgroundColor #E8F5E8
    borderColor #388E3C
}
skinparam package<<Infrastructure>> {
    backgroundColor #F3E5F5
    borderColor #7B1FA2
}
skinparam package<<External>> {
    backgroundColor #FFEBEE
    borderColor #D32F2F
}

' Actors
actor "Developer" as Dev #1976D2
actor "End User" as User #388E3C

' Development Environment
package "Development" <<Development>> as DevEnv {
    node "Local" as Local #E3F2FD {
        database "SQLite" as LocalDB #E3F2FD
        [React Dev\n<b>port:3000] as DevFrontend #E3F2FD
        [FastAPI Dev\n<b>port:8000] as DevBackend #E3F2FD
    }
}

' Version Control & CI/CD
package "CI/CD" <<Infrastructure>> as VC {
    node "GitHub" as GitHub #F3E5F5 {
        artifact "Code" as Code #F3E5F5
        component "Actions" as CI_CD #F3E5F5
    }
}

' Production Frontend
package "Frontend" <<Production>> as FrontendDeploy {
    cloud "Vercel" as Vercel #E8F5E8 {
        [React App] as ProdFrontend #E8F5E8
        component "CDN" as CDN #E8F5E8
    }
}

' Production Backend
package "Backend" <<Production>> as BackendDeploy {
    cloud "Render" as Render #E8F5E8 {
        [FastAPI] as ProdBackend #E8F5E8
        database "Redis" as Redis #E8F5E8
        component "LB" as LB #E8F5E8
    }
}

' Database Infrastructure
package "Database" <<Infrastructure>> as DataLayer {
    cloud "Aiven" as Aiven #F3E5F5 {
        database "MySQL 8.0\n<b>database" as MySQL #F3E5F5
    }
}

' External Services
package "External APIs" <<External>> as External {
    cloud "OpenAI" as OpenAI #FFEBEE
    cloud "DuckDuckGo" as DuckDuckGo #FFEBEE
}

' Positioning
DataLayer -[hidden]d- BackendDeploy

' Development Workflow
Dev --> Local : Develop
Local --> GitHub : Push

' CI/CD Pipeline Flow
GitHub --> CI_CD : Build
CI_CD --> Vercel : Deploy FE
CI_CD --> Render : Deploy BE

' Production Data Flow
User --> ProdFrontend : HTTPS
ProdFrontend --> CDN : Assets
ProdFrontend --> LB : APIs
LB --> ProdBackend : Route
ProdBackend --> Redis : Cache
ProdBackend --> MySQL : DB

' External API Integrations
ProdBackend --> OpenAI : AI
ProdBackend --> DuckDuckGo : Search

legend right
    |= Type |= Color |
    | Development | <back:#E3F2FD><color:#1976D2>Blue</color></back> |
    | Production | <back:#E8F5E8><color:#388E3C>Green</color></back> |
    | Infrastructure | <back:#F3E5F5><color:#7B1FA2>Purple</color></back> |
    | External | <back:#FFEBEE><color:#D32F2F>Red</color></back> |
endlegend

@enduml
```
