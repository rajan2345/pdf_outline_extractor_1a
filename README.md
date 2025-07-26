Here's the corrected README.md file with proper Markdown syntax:

```markdown
# PDF Outline Extractor

A robust heuristic-based PDF outline extraction system developed for Adobe India Hackathon 2025 - Round 1A. This tool automatically identifies and extracts document structure and headings from PDF files using advanced typography and layout analysis techniques.

## Overview

This project addresses the complex challenge of automatically extracting meaningful document outlines from various PDF formats. After analyzing different approaches, I implemented a pure heuristic-based solution that provides reliable results without the overhead and unpredictability of machine learning models.

## 🚀 Quick Start

### Prerequisites
- Git
- Docker (recommended) OR Python 3.9+

### Installation & Usage

1. **Clone the repository**

```bash
git clone https://github.com/your-username/pdf-outline-extractor.git
cd pdf-outline-extractor
```

2. **Prepare directories**

```bash
mkdir input output
```

3. **Add your PDF files**

```bash
cp /path/to/your/document.pdf input/
```

4. **Run with Docker**

**Build the container**

```bash
docker build -t pdf-extractor .
```

**Extract outlines**

```bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-extractor
```

**WINDOWS**

```bash
docker run -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output pdf-extractor
```

5. **View results**

```bash
cat output/your_document.json
```

## 🏗️ Architecture

The system is built with a modular architecture:

```
├── src/
│   ├── extractor.py        # Core extraction engine
│   ├── detector.py         # Heuristic detection algorithms
│   ├── utils.py            # Typography analysis utilities
│   └── document_types.py   # Document-specific handlers
├── main.py                 # Application entry point
├── Dockerfile              # Containerization
└── requirements.txt        # Dependencies
```

## 🎯 Technical Approach

I designed this system around several key principles:

### Heuristic-Based Detection
Instead of relying on machine learning models, I developed rule-based algorithms that analyze:
- **Typography patterns**: Font sizes, weights, and styles
- **Layout analysis**: Text positioning, centering, and spacing
- **Content structure**: Numbering schemes, case patterns, and hierarchy

### Document Type Adaptation
The system automatically detects and adapts to different document types:
- **Academic papers**: Traditional hierarchical structure
- **Business reports**: Section-based organization
- **Promotional content**: Importance-based ranking
- **Technical manuals**: Numbered and referenced sections

### Performance Optimization
I implemented several optimizations:
- Selective text analysis to reduce processing time
- Efficient pattern matching with compiled regex
- Memory-conscious page-by-page processing
- Fallback to document TOC when available

## 📊 Output Format

Each processed PDF generates a structured JSON output:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Main Section",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Subsection",
      "page": 3
    }
  ],
  "metadata": {
    "extraction_method": "heuristic",
    "document_type": "formal",
    "processing_time": 1.23,
    "total_pages": 15,
    "total_headings": 12
  }
}
```

## 🔧 Advanced Usage

### Command Line Options

```bash
python main.py --input_dir /path/to/pdfs --output_dir /path/to/results --verbose
```

### Local Python Installation

**Set up virtual environment**

```bash
python -m venv venv
source venv/bin/activate
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Run extraction**

```bash
python main.py
```

### Batch Processing
The system automatically processes all PDF files in the input directory and generates individual JSON files plus a processing summary.

## 🎨 Design Decisions

### Why Heuristic-Only?
After evaluating various approaches, I chose a heuristic-based solution because:
- **Reliability**: Consistent results across different document types
- **Performance**: No model loading or inference overhead
- **Maintainability**: Clear, debuggable rule-based logic
- **Portability**: Minimal dependencies and resource requirements

### Typography Analysis Engine
I developed sophisticated algorithms to identify headings by analyzing:
- Relative font sizes within documents
- Bold and italic formatting patterns
- Text positioning and alignment
- Case conventions (uppercase, title case)
- Whitespace and spacing patterns

### Document Classification System
The system includes intelligent document type detection that adapts extraction strategies based on content analysis, improving accuracy across diverse document formats.

## 📈 Performance Metrics

- **Processing Speed**: 1-2 seconds per page
- **Memory Efficiency**: ~50MB per document
- **Accuracy Rate**: 85-95% depending on document quality
- **Supported Formats**: Standard PDF files (non-encrypted)

## 🛠️ Development Notes

### Key Challenges Solved
1. **Variable Typography**: Handling inconsistent font usage across documents
2. **Layout Diversity**: Adapting to different document design patterns
3. **Content Ambiguity**: Distinguishing headings from emphasized text
4. **Performance Scaling**: Efficient processing of large documents

### Technical Stack
- **PDF Processing**: PyMuPDF for reliable document parsing
- **Text Analysis**: Custom algorithms with NumPy for numerical operations
- **Containerization**: Docker for consistent deployment
- **Pattern Matching**: Optimized regex patterns for content classification

## 🚀 Getting Started - Complete Example

**Complete workflow example**

```bash
git clone https://github.com/your-username/pdf-outline-extractor.git
cd pdf-outline-extractor
```

**Build and run**

```bash
docker build -t pdf-extractor .
```
**For Linux users**
```bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-extractor
```
**For Windows users**
```bash
docker run -v $(PWD)/input:/app/input -v $(PWD)/output:/app/output pdf-extractor
```
**View results**

```bash
cat output/sample.json | head -20
```

## 📋 Requirements

- Python 3.9 or higher
- Docker (recommended for deployment)
- PyMuPDF for PDF processing
- NumPy for numerical operations

## 🔍 Troubleshooting

**No output files generated?**
- Verify PDFs are in the input directory
- Check file permissions
- Review extraction.log for detailed error information

**Unexpected results?**
- Enable verbose mode with `--verbose` flag
- Ensure PDFs are not password-protected
- Try with simpler documents first to isolate issues

## 📝 License

Developed for Adobe India Hackathon 2025 - Round 1A

---

*This project demonstrates advanced document analysis techniques using pure algorithmic approaches, achieving reliable PDF outline extraction without machine learning dependencies.*
```
