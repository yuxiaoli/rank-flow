# Rank Flow

An AI-powered resume ranking and evaluation system that processes PDF resumes, generates scoring rubrics, and ranks candidates based on job requirements.

## Overview

Rank Flow is a comprehensive CLI tool designed to streamline the resume screening process by:
- Extracting text content from PDF resumes
- Generating custom scoring rubrics based on job descriptions
- Ranking candidates using AI-powered evaluation
- Converting results to CSV format for analysis
- Copying top candidates for further review

## Features

- **Multi-format Support**: Processes PDF files and zip archives containing resumes
- **AI-Powered Scoring**: Uses configurable AI models for intelligent evaluation
- **Custom Rubrics**: Generates tailored scoring criteria based on job requirements
- **Flexible Output**: Supports JSON and CSV output formats
- **Top Candidate Selection**: Automatically copies qualified resumes to a separate directory
- **Progress Tracking**: Visual progress bars for batch processing

## Installation

### Prerequisites
- Python 3.11 or higher
- Poetry (for dependency management)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd rank-flow
```

2. Install dependencies:
```bash
poetry install
```

3. Set up environment variables:
Create a `.env` file in the project root with your AI model API keys:
```
API_KEY_JIUTIAN_LAN=your_api_key_here
API_KEY_QWEN3=your_api_key_here
API_KEY_DEEPSEEK_R1=your_api_key_here
```

## Usage

The application provides five main commands that work together in a typical workflow:

### 1. Extract Resume Data

Extract text and metadata from PDF resumes:

```bash
poetry run python src/rank_flow extract temp/resumes/
```

**Options:**
- `-v, --verbose`: Enable verbose output
- `-o, --output`: Specify output file (default: `output/extracted_data.json`)

### 2. Generate Scoring Rubric

Create a custom scoring rubric based on job requirements:

```bash
poetry run python src/rank_flow generate-rubric -r data/job_description.txt -m qwen3 --timeout 120
```

**Options:**
- `-r, --requirements`: Path to job description file (required)
- `-m, --model`: AI model to use (jiutian-lan, qwen3, deepseek-r1)
- `-o, --output`: Output file (default: `output/generated_rubric.json`)
- `--timeout`: API timeout in seconds (default: 30)
- `--score-range`: Score range for rubric (default: 0 100)

### 3. Rank Candidates

Score and rank resumes using the generated rubric:

```bash
poetry run python src/rank_flow rank -i output/extracted_data.json --rubric-file output/generated_rubric.json -m qwen3 --timeout 60
```

**Options:**
- `-i, --input-data`: Path to extracted data JSON (required)
- `-r, --requirements`: Path to requirements file
- `--rubric-file`: Path to custom rubric JSON file
- `-m, --model`: AI model for scoring
- `-o, --output`: Output file (default: `output/ranked_data.json`)
- `--timeout`: API timeout in seconds

### 4. Convert to CSV

Convert ranked JSON data to CSV format for analysis:

```bash
poetry run python src/rank_flow convert -i output/ranked_data.json -o output/ranked_data.csv
```

**Options:**
- `-i, --input-file`: Input JSON file (default: `output/ranked_data.json`)
- `-o, --output`: Output CSV file (default: `output/ranked_data.csv`)

### 5. Copy Top Candidates

Copy the highest-scoring resumes to a separate directory:

```bash
poetry run python src/rank_flow copy
```

**Options:**
- `-i, --input-file`: Ranked data JSON file (default: `output/ranked_data.json`)
- `-o, --output-dir`: Output directory (default: `output/top_candidates/`)
- `--num`: Number of top candidates to copy (default: 5)
- `--min-score`: Minimum score threshold for copying

## Complete Workflow

The typical workflow is automated in <mcfile name="run.bat" path="c:\workspace\python\rank-flow\scripts\run.bat"></mcfile>:

```bash
REM Generate output/extracted_data.json
poetry run python src/rank_flow extract temp/resumes/
REM Generate output/generated_rubric.json
poetry run python src/rank_flow generate-rubric -r data/job_description.txt -m qwen3 --timeout 120
REM Generate output/ranked_data.json
poetry run python src/rank_flow rank -i output/extracted_data.json --rubric-file output/generated_rubric.json -m qwen3 --timeout 60
REM Convert output/ranked_data.json to output/ranked_data.csv
poetry run python src/rank_flow convert -i output/ranked_data.json -o output/ranked_data.csv
REM Copy top candidates to output/top_candidates/
poetry run python src/rank_flow copy
```

## Project Structure

```
rank-flow/
├── src/rank_flow/           # Main application code
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── cli.py               # Command-line interface
│   ├── scoring.py           # AI scoring and rubric system
│   └── utils/               # Utility functions
├── data/                    # Sample data files
│   ├── job_description.txt  # Example job requirements
│   └── ranked_data.schema.json
├── output/                  # Generated output files
├── scripts/                 # Automation scripts
│   └── run.bat             # Complete workflow script
├── pyproject.toml          # Project configuration
└── README.md
```

## Dependencies

- **PyMuPDF**: PDF text extraction
- **python-dotenv**: Environment variable management
- **tqdm**: Progress bars
- **datatable**: Data processing
- **httpx**: HTTP client for AI API calls

## Configuration

### AI Models

The system supports multiple AI models:
- `jiutian-lan` (default)
- `qwen3`
- `deepseek-r1`

Configure API keys in your `.env` file using the format `API_KEY_{MODEL_NAME}`.

### Scoring Rubric

The system generates custom rubrics with the following criteria:
- **Relevance Alignment** (30%): How well content matches requirements
- **Quality Completeness** (25%): Overall quality and completeness
- **Technical Competency** (20%): Technical skills demonstrated
- **Presentation Clarity** (15%): Organization and professionalism
- **Innovation Uniqueness** (10%): Added value beyond basic requirements

## Output Files

- `extracted_data.json`: Raw extracted resume data
- `generated_rubric.json`: Custom scoring rubric
- `ranked_data.json`: Scored and ranked candidates
- `ranked_data.csv`: CSV format for analysis
- `top_candidates/`: Directory with copied top-scoring resumes

## License

This project is developed by Sean Li (sean.li@vectorindex.cloud).
        