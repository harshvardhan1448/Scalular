# Scalular - Tech Pack Analysis & Data Intelligence Platform

An intelligent document analysis system that extracts and standardizes technical pack information from textile and apparel documents using AI-driven data processing and structured data matching.

## 🎯 Project Overview

Scalular is a sophisticated data analytics and intelligent document processing application designed to extract, normalize, and match technical specifications from apparel industry documents. The system combines **AI-powered text analysis** with **data engineering** to transform unstructured technical pack (techpack) documents into structured, actionable data.

---

## 📊 Data Analyst Skills Demonstrated

### 1. **Data Extraction & Parsing**
- **PDF Document Processing**: Utilized PyMuPDF and PyPDF2 libraries to extract and parse text from complex technical pack documents
- **Text Mining**: Implemented intelligent text analysis to identify and extract specific attributes from unstructured data:
  - Product specifications (gender, category, product name)
  - Technical details (fabric types, GSM/weight, sizes, print types)
  - Boolean features (zipper presence, logo embroidery)

### 2. **Data Normalization & Standardization**
- **Size Range Normalization** (`_normalize_size_range` function):
  - Converts multiple size formats (XXS, XS, S, M, L, XL, XXL, XXXL, 1X, 2X, 3X, 4X) into standardized ranges
  - Implements custom ordering logic to maintain consistency
  - Handles duplicate and variant size notations
  
- **Data Quality Assurance**: 
  - Maps non-standard sizes to canonical formats
  - Validates extracted data and applies default values when extraction fails
  - Ensures data consistency across all documents

### 3. **Data Matching & Categorization**
- **Multi-level Category Matching**: 
  - Matches extracted product categories against predefined taxonomy from structured reference data (object.json)
  - Implements confidence scoring (high/medium/low) for match reliability
  - Provides reasoning for each categorization decision

- **Fabric & Specification Matching**:
  - Matches fabric descriptions against available fabric blends database
  - Correlates GSM (Grams per Square Meter) ranges with product categories
  - Validates matches against 3-dimensional lookup structure (category → fabric → GSM)

### 4. **Reference Data Management**
- **Structured Data Integration**: 
  - Loads and manages complex JSON reference data (`object.json`) containing:
    - Product categories hierarchy
    - Available fabric blends per category
    - GSM weight ranges per fabric
  - Implements efficient lookup methods for data retrieval

- **Data Relationship Mapping**:
  - Maintains hierarchical relationships (Category → Fabric → GSM Ranges)
  - Dynamically generates available options based on selected category
  - Supports complex multi-level filtering and querying

### 5. **ETL Pipeline Development**
- **Multi-stage Processing Pipeline**:
  - **Extract**: PDF to text conversion
  - **Transform**: Multi-step AI analysis
    - Basic information extraction
    - Category matching
    - Fabric identification
    - GSM range assignment
  - **Load**: Structured JSON output

- **Error Handling & Fallback Logic**:
  - Graceful degradation with sensible defaults
  - Try-catch mechanisms for data validation
  - Comprehensive error logging and troubleshooting

### 6. **Data Validation & Quality Control**
- **Validation Framework**:
  - Checks for missing file uploads
  - Validates extracted text content
  - Ensures successful AI analysis completion
  - Implements confidence thresholds for matches

- **Null/Missing Data Handling**:
  - Smart defaults for unextracted fields
  - Fallback values when primary data sources fail
  - Comprehensive error response structure

### 7. **API & Data Integration**
- **RESTful Data Service Architecture**:
  - FastAPI for high-performance data processing endpoints
  - CORS middleware for cross-origin data access
  - JSON standardized response format for downstream systems

- **Data Pipeline Integration**:
  - Google Generative AI (Gemini) for intelligent text analysis
  - Async processing for scalable data handling
  - Structured output format for downstream analytics

### 8. **Analytics Output**
The system generates structured analytics data:
```json
{
  "gender": "Product demographic (men/women/kids)",
  "product_name": "Extracted name from document",
  "zipper": "Boolean presence of zipper feature",
  "logo_embroidery": "Boolean logo/embroidery status",
  "size": "Normalized size range (e.g., S-3XL)",
  "print": "Print type from predefined taxonomy",
  "category": "Matched category from reference data",
  "quantity_in_gms": "GSM/weight range standardized",
  "fabric_and_blend": "Matched fabric specification"
}
```

---

## 🛠️ Technology Stack

**Data Processing & Analytics:**
- Python 3.x
- Pandas (2.2.3) - Data manipulation and analysis
- openpyxl, xlrd - Excel data handling
- PyMuPDF (fitz) - PDF parsing and text extraction

**AI & Intelligence:**
- Google Generative AI (Gemini 1.5 Flash) - Intelligent text analysis
- Regular expressions - Pattern matching and data extraction

**API & Web Framework:**
- FastAPI (0.68.1) - Modern REST API framework
- Uvicorn (0.15.0) - ASGI server
- Jinja2 - Template rendering

**Document Processing:**
- PyPDF2, pdfkit - PDF manipulation
- pytesseract (0.3.10) - OCR capabilities
- Pillow (10.2.0) - Image processing

---

## 📁 Project Structure

```
Scalular/
├── api.py                 # Main FastAPI application and endpoints
├── fabric_matcher.py      # Core analytics engine and data processing
├── object.json            # Reference data database (categories, fabrics, GSM ranges)
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates for web interface
├── static/                # CSS, JavaScript, and assets
├── temp/                  # Temporary file storage during processing
└── README.md             # This file
```

---

## 🚀 Key Features

1. **Intelligent Document Analysis**: Leverages AI to understand and extract complex technical specifications from unstructured documents

2. **Data Standardization**: Automatically normalizes and validates all extracted data against predefined business rules

3. **Accuracy Through Matching**: Multi-level matching against reference databases ensures high accuracy and consistency

4. **Scalable Architecture**: Async processing and modern API design support high-volume document processing

5. **Comprehensive Data Integration**: Seamlessly combines multiple data sources (documents, reference databases, AI analysis) into unified output

---

## 📈 Data Analytics Capabilities

- **Document-to-Data Transformation**: Convert unstructured PDFs into structured, analyzable datasets
- **Data Normalization**: Standardize diverse input formats into consistent taxonomies
- **Quality Assurance**: Validate and score data matches with confidence metrics
- **Reference Data Management**: Manage complex hierarchical reference data for accurate categorization
- **Error Tracking**: Comprehensive logging for data quality monitoring
- **Scalable Processing**: Handle high-volume document ingestion and processing

---

## 💡 Technical Achievements

✅ **Multi-stage ETL Pipeline** - Efficient extract-transform-load workflow
✅ **Hierarchical Data Matching** - 3-level category matching for accuracy
✅ **Intelligent Normalization** - Complex size and specification standardization
✅ **Error Resilience** - Graceful fallbacks and comprehensive error handling
✅ **Performance Optimization** - Async processing and efficient data lookup
✅ **API-First Design** - RESTful architecture for seamless integration

---

## 🔧 Installation & Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "api_key=YOUR_GEMINI_API_KEY" > .env

# Run the application
uvicorn api:app --reload
```

Access the application at `http://localhost:8000/extract_info`

---

## 📊 Data Output Format

The system produces standardized JSON analytics output:

```json
{
  "gender": "men",
  "product_name": "Crewneck T-shirt",
  "zipper": false,
  "logo_embroidery": true,
  "size": "S-3XL",
  "print": "solid",
  "category": "crewneck-t-shirts",
  "quantity_in_gms": "160-180",
  "fabric_and_blend": "Single-Jersey-(Combed)"
}
```

---

## 📚 Learning & Impact

This project demonstrates:
- **Data Engineering Skills**: Building scalable data pipelines
- **Data Analysis**: Extracting insights from unstructured data
- **Business Analytics**: Understanding domain-specific data requirements (apparel/textile industry)
- **Software Engineering**: Clean code, error handling, and API design
- **AI Integration**: Leveraging modern AI models for data understanding

---

## 📝 License

This project is open source and available for reference and educational purposes.

---

**Created by**: Harshvardhan Sharma  
**Repository**: [Scalular](https://github.com/harshvardhan1448/Scalular)
