# Alumni Tracking System

A streamlined system for tracking alumni career information using web research and manual data collection methods.

## Key Features

- **Web Research Collection**: Automated web search for alumni information using DuckDuckGo
- **Manual Data Entry**: Web interface for manual alumni profile creation
- **Excel File Upload**: Upload alumni names from Excel files (GIVEN NAME, FIRST NAME columns)
- **AI Verification**: OpenAI-powered profile matching and data enhancement
- **Web Interface**: React frontend for easy data management
- **Export Options**: Excel and CSV export with filtering
- **Search & Filter**: Advanced search by name, industry, company, location

## 📊 Collection Methods

### Web Research (Default)
- ✅ Uses public web search (DuckDuckGo)
- ✅ No API keys required
- ✅ Fully compliant with web scraping policies
- 🔧 Automatic search and AI-powered data extraction

### Manual Data Entry
- ✅ User-controlled data input
- ✅ Web interface for profile creation
- ✅ Full control over data quality
- 🔧 No external dependencies


## 🚀 Quick Start

### 1. Backend Setup (FastAPI)

From the `backend` directory:

```pwsh
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
```

#### Run the backend (development):

```pwsh
# Option 1: Hot-reload (recommended for development)
uvicorn main:app --reload

# Option 2: Use the launcher script
python main.py
```

If you see 'uvicorn' is not recognized, make sure you activated your virtual environment, or run:
```pwsh
pip install uvicorn
```

The backend will be available at http://localhost:8000

### 2. Frontend Setup (React)

```pwsh
cd frontend
npm install
npm start
```

The frontend will be available at http://localhost:3000

---

**Access the web interface:**
- Open http://localhost:3000
- Upload Excel file with alumni names
- Use web research or manual entry to collect data

## 📋 Requirements

- Python 3.9+
- Node.js & npm
- OpenAI API key (optional, for AI verification)

## ⚙️ Setup

1. **Clone and install:**
   ```bash
   git clone <repository>
   cd AlumniSystem
   pip install -r requirements.txt
   ```

2. **Environment variables (.env):**
   ```bash
   # OpenAI (optional)
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   ```

## 🔒 Legal & Ethical Compliance

**✅ COMPLIANT SYSTEM**: This system uses only ethical data collection methods:

### **Safe Data Collection**
1. **Web Research**: Public web search using DuckDuckGo (no scraping)
2. **Manual Data Entry**: User-controlled profile creation
3. **Public Information Only**: Only collects publicly available information
4. **Consent Recommended**: Obtain proper consent for data collection

### **Compliance Features**
- No automated scraping of social media platforms
- No unauthorized API access
- Respectful web crawling with delays
- Transparent data collection methods

---

Your Excel file should have these columns:
```
| GIVEN NAME | FIRST NAME |
|------------|------------|
| John       | Smith      |
| Jane       | Doe        |
```

## 🔧 API Endpoints

- `GET /alumni` - List all alumni
- `POST /upload-names` - Upload Excel file with auto-collection
- `POST /collect` - Collect data for specific names
- `GET /export` - Export data to Excel/CSV
- `GET /stats` - Get system statistics

## 📁 Project Structure

```
AlumniSystem/
├── src/
│   ├── api/              # FastAPI backend
│   ├── services/         # Business logic
│   ├── database/         # Data models & repository
│   └── models/           # Alumni profile models
├── frontend/             # React web interface
├── requirements.txt      # Python dependencies
└── start.py             # System startup script
```

## 🔒 Notes

- Uses public web search for data collection
- Respects web crawling best practices
- ECU graduate filtering included
- Confidence scoring for data quality
- AI-powered profile verification (optional)

---

**Built for ECU Alumni Tracking**
