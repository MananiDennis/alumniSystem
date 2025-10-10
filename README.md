# Alumni Tracking System

A streamlined system for tracking alumni career in## ⚖️ Legal & Ethical Compliance

**⚠️ IMPORTANT NOTICE**: This system provides two data collection methods with different compliance levels:

### **BrightData Method (Non-Compliant)**
- ❌ May violate LinkedIn's Terms of Service
- ❌ LinkedIn prohibits automated data scraping (Section 8.2.2)
- ❌ Risk of account termination and legal issues

### **LinkedIn Official API (Compliant)**
- ✅ Fully compliant with LinkedIn policies
- ✅ Uses official Partner Program APIs
- ✅ Proper authentication and rate limiting
- 🔑 Requires LinkedIn partnership and API approval

### **Recommended Safe Usage**
1. **Use Official API**: Choose the official LinkedIn API method when available
2. **Manual Data Entry**: Use the web interface for manual alumni profile creation
3. **Excel Upload Only**: Upload alumni names without auto-collection
4. **Obtain Consent**: Ensure proper consent for data collection

### **LinkedIn Official API Setup**
To use the compliant method:
1. Apply for LinkedIn Partner Program access
2. Request People Search API permissions
3. Set up OAuth2 authentication
4. Configure rate limiting (100 requests/hour)

### **Compliance Steps***dual collection methods**: BrightData API and LinkedIn's Official Partner API.

## Key Features

- **Dual Collection Methods**: Choose between BrightData (fast) or Official LinkedIn API (compliant)
- **Excel File Upload**: Upload alumni names from Excel files (GIVEN NAME, FIRST NAME columns)
- **Smart Data Collection**: Automated LinkedIn profile matching and data extraction
- **Compliance Options**: Official LinkedIn API for Terms of Service compliance
- **AI Verification**: OpenAI-powered profile matching (optional)
- **Web Interface**: React frontend for easy data management
- **Export Options**: Excel and CSV export with filtering
- **Search & Filter**: Advanced search by name, industry, company, location

## ⚖️ Collection Methods

### BrightData API (Default)
- ✅ Fast and efficient data collection
- ⚠️ **Warning**: May violate LinkedIn Terms of Service
- 🔧 No additional setup required

### LinkedIn Official API (Compliant)
- ✅ Fully compliant with LinkedIn policies
- ✅ Official partner program integration
- 🔑 Requires LinkedIn API keys and partnership
- ⏱️ Rate limited (100 requests/hour)

## 🚀 Quick Start

1. **Start the system:**
   ```bash
   python start.py
   ```
   This starts both backend (port 8000) and frontend (port 3000)

2. **Access the web interface:**
   - Open http://localhost:3000
   - Upload Excel file with alumni names
   - Choose collection method: Official API (compliant) or BrightData (non-compliant)

## 📋 Requirements

- Python 3.9+
- Node.js & npm
- **For BrightData**: BrightData account
- **For Official API**: LinkedIn Partnership Program access
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
   
   # BrightData (non-compliant method)
   BRIGHTDATA_API_KEY=your_brightdata_key_here
   
   # LinkedIn Official API (compliant method)
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret  
   LINKEDIN_ACCESS_TOKEN=your_access_token
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   ```

## � Legal & Ethical Compliance

**⚠️ IMPORTANT NOTICE**: This system includes automated LinkedIn data collection features that may violate LinkedIn's Terms of Service. Before using these features, please consider:

### **LinkedIn Policy Concerns**
- LinkedIn prohibits automated data scraping (Section 8.2.2 of User Agreement)
- Unauthorized bots and automated access are forbidden (Section 8.2.13)
- Account termination risk for policy violations

### **Recommended Safe Usage**
1. **Manual Data Entry**: Use the web interface for manual alumni profile creation
2. **Excel Upload Only**: Upload alumni names from Excel files without auto-collection
3. **Public Information**: Only collect publicly available information with proper consent
4. **LinkedIn Official APIs**: Consider LinkedIn's official Partner Program for legitimate access

### **Compliance Steps**
- Disable automated BrightData collection in production
- Use only manual data entry features
- Obtain proper consent before collecting alumni data
- Consider LinkedIn's official business solutions

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

- Only scrapes publicly available LinkedIn data
- Respects LinkedIn rate limits
- ECU graduate filtering included
- Confidence scoring for data quality

---

**Built for ECU Alumni Tracking**
