#!/usr/bin/env python3
"""
CLI application for processing files in directories or zip bundles.
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import shutil

# Third-party imports
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF is not installed. Please install it with: pip install PyMuPDF")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: python-dotenv is not installed. Please install it with: pip install python-dotenv")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("Error: tqdm is not installed. Please install it with: pip install tqdm")
    sys.exit(1)

try:
    import datatable as dt
except ImportError:
    print("Error: datatable is not installed. Please install it with: pip install datatable")
    sys.exit(1)

try:
    import httpx
except ImportError:
    print("Error: httpx is not installed. Please install it with: pip install httpx")
    sys.exit(1)

# Local imports
from rank_flow.utils import unzip, iterate_directory
from rank_flow.scoring import RubricScorer


def load_job_description(job_desc_file: str) -> str:
    """
    Load job description from a text file.
    
    Args:
        job_desc_file: Path to the job description text file
        
    Returns:
        Job description content as string
    """
    try:
        with open(job_desc_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        print(f"Loaded job description from: {Path(job_desc_file).absolute()}")
        print(f"Job description length: {len(content)} characters")
        return content
    except Exception as e:
        print(f"Error loading job description from {job_desc_file}: {e}")
        return ""


def load_requirements(requirements_file: str) -> str:
    """
    Load requirements from a text file.
    
    Args:
        requirements_file: Path to the requirements text file
        
    Returns:
        Requirements content as string
    """
    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        print(f"Loaded requirements from: {Path(requirements_file).absolute()}")
        print(f"Requirements length: {len(content)} characters")
        return content
    except Exception as e:
        print(f"Error loading requirements from {requirements_file}: {e}")
        return ""


def extract_pdf_text(pdf_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def get_model_config() -> Dict[str, str]:
    """
    Get available models and API keys from environment variables.
    
    Returns:
        Dictionary mapping model names to API keys
    """
    models = {}
    
    # Map environment variables to model names
    env_to_model = {
        'DEEPSEEK_R1_API_KEY': 'deepseek-r1',
        'QWEN3_API_KEY': 'qwen3',
        'JIUTIAN_API_KEY': 'jiutian-lan'
    }
    
    for env_var, model_name in env_to_model.items():
        api_key = os.getenv(env_var)
        if api_key:
            models[model_name] = api_key
    
    return models


def process_file(file_path: str, extracted_data: List[Dict[str, Any]]) -> None:
    """
    Process a file based on its extension.
    
    Args:
        file_path: Path to the file to process
        extracted_data: List to store extracted data
    """
    file_ext = Path(file_path).suffix.lower()
    file_name = Path(file_path).name
    file_size = Path(file_path).stat().st_size
    
    # Initialize data entry
    data_entry = {
        'file_path': file_path,
        'file_name': file_name,
        'file_extension': file_ext,
        'file_size_bytes': file_size,
        'extracted_text': '',
        'processing_status': 'processed',
        'error_message': ''
    }
    
    try:
        extracted_text = ""
        
        if file_ext == ".pdf":
            extracted_text = extract_pdf_text(file_path)
            if extracted_text.strip():
                data_entry['processing_status'] = 'success'
            else:
                data_entry['processing_status'] = 'no_text_found'
        
        elif file_ext == ".txt":
            # Read text file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
                data_entry['processing_status'] = 'success'
            except Exception as e:
                data_entry['processing_status'] = 'error'
                data_entry['error_message'] = f"Text file read error: {str(e)}"
            
        elif file_ext == ".docx":
            # TODO: Add DOCX processing logic here
            data_entry['processing_status'] = 'placeholder_docx'
            
        elif file_ext == ".xlsx":
            # TODO: Add Excel processing logic here
            data_entry['processing_status'] = 'placeholder_xlsx'
            
        elif file_ext == ".csv":
            # TODO: Add CSV processing logic here
            data_entry['processing_status'] = 'placeholder_csv'
            
        elif file_ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
            # TODO: Add image processing logic here
            data_entry['processing_status'] = 'placeholder_image'
            
        elif file_ext in [".mp4", ".avi", ".mov", ".mkv"]:
            # TODO: Add video processing logic here
            data_entry['processing_status'] = 'placeholder_video'
            
        elif file_ext in [".mp3", ".wav", ".flac", ".aac"]:
            # TODO: Add audio processing logic here
            data_entry['processing_status'] = 'placeholder_audio'
            
        else:
            data_entry['processing_status'] = 'unknown_type'
        
        data_entry['extracted_text'] = extracted_text
            
    except Exception as e:
        data_entry['processing_status'] = 'error'
        data_entry['error_message'] = str(e)
    
    extracted_data.append(data_entry)


def save_extracted_data(extracted_data: List[Dict[str, Any]], output_file: str = "extracted_data.json") -> None:
    """
    Save extracted data to a JSON file.
    
    Args:
        extracted_data: List of dictionaries containing extracted data
        output_file: Output file path
    """
    try:
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to JSON with proper formatting
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nExtracted data saved to: {output_path.absolute()}")
        
        # Print summary statistics
        print(f"\nSummary:")
        print(f"  Total files processed: {len(extracted_data)}")
        
        # Count by status
        status_counts = {}
        for item in extracted_data:
            status = item.get('processing_status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"  Processing status breakdown:")
        for status, count in status_counts.items():
            print(f"    {status}: {count}")
        
        # Count by file extension
        ext_counts = {}
        for item in extracted_data:
            ext = item.get('file_extension', 'unknown')
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
        
        print(f"  File extension breakdown:")
        for ext, count in ext_counts.items():
            print(f"    {ext}: {count}")
            
        # Calculate total text extracted (for PDFs)
        pdf_items = [item for item in extracted_data if item.get('file_extension') == '.pdf']
        if pdf_items:
            total_chars = sum(len(item.get('extracted_text', '')) for item in pdf_items)
            print(f"  Total characters extracted from PDFs: {total_chars:,}")
        
    except Exception as e:
        print(f"Error saving extracted data: {e}")


def extract(args):
    """
    Extract text and metadata from files in a directory or zip bundle.
    """
    input_path = Path(args.input_path)
    
    # Check if input exists
    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}")
        sys.exit(1)
    
    # Handle zip file
    if input_path.is_file() and input_path.suffix.lower() == ".zip":
        print(f"Detected zip file: {input_path}")
        
        # Create temporary extraction directory
        extract_dir = input_path.parent / f"{input_path.stem}_extracted"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            # Extract zip file
            unzip(str(input_path), str(extract_dir))
            input_path = extract_dir
        except Exception as e:
            print(f"Error extracting zip file: {e}")
            sys.exit(1)
    
    # Ensure we have a directory to process
    if not input_path.is_dir():
        print(f"Error: Input must be a directory or zip file: {input_path}")
        sys.exit(1)
    
    print(f"Processing directory: {input_path}")
    print("-" * 50)
    
    # Collect all files with progress bar
    print("Scanning directory...")
    file_list = list(tqdm(iterate_directory(str(input_path)), desc="Scanning files"))
    
    # Save and print file list
    print(f"\nFound {len(file_list)} files:")
    if args.verbose:
        for i, file_path in enumerate(file_list, 1):
            print(f"  {i:3d}. {file_path}")
    else:
        print(f"  Use -v flag to see detailed file list")
    
    # Save file list to output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    file_list_output = output_dir / "file_list.txt"
    
    with open(file_list_output, "w", encoding="utf-8") as f:
        for file_path in file_list:
            f.write(f"{file_path}\n")
    
    print(f"File list saved to: {file_list_output.absolute()}")
    print("-" * 50)
    
    # Process each file with progress bar
    print("\nProcessing files...")
    extracted_data = []
    
    for file_path in tqdm(file_list, desc="Processing files", unit="file"):
        try:
            process_file(file_path, extracted_data)
        except Exception as e:
            print(f"\nError processing {file_path}: {e}")
            # Add error entry to data
            extracted_data.append({
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'file_extension': Path(file_path).suffix.lower(),
                'file_size_bytes': 0,
                'extracted_text': '',
                'processing_status': 'error',
                'error_message': str(e)
            })
    
    # Save extracted data
    save_extracted_data(extracted_data, args.output)
    
    print("\nExtraction complete!")


def generate_rubric(args):
    """
    Generate scoring rubric based on requirements.
    """
    # Load environment variables
    load_dotenv()
    
    # Get available models
    available_models = get_model_config()
    
    if not available_models:
        print("Error: No API keys found in environment variables. Please check your .env file.")
        sys.exit(1)
    
    if args.model not in available_models:
        print(f"Error: Model {args.model} not available. Available models: {', '.join(available_models.keys())}")
        sys.exit(1)
    
    # Load requirements
    requirements = ""
    if args.requirements:
        req_path = Path(args.requirements)
        if not req_path.exists():
            print(f"Error: Requirements file does not exist: {req_path}")
            sys.exit(1)
        requirements = load_requirements(str(req_path))
        if not requirements:
            print("Error: Requirements file is empty or could not be loaded")
            sys.exit(1)
    else:
        print("Error: Requirements file is required for generating rubric")
        sys.exit(1)
    
    # Initialize scorer
    api_key = available_models[args.model]
    scorer = RubricScorer(model_name=args.model, api_key=api_key, timeout=args.timeout)
    
    print(f"Generating custom rubric using model: {args.model}")
    print(f"Requirements length: {len(requirements)} characters")
    print("-" * 50)
    
    # Generate custom rubric
    score_range = tuple(args.score_range)
    custom_rubric = scorer.generate_custom_rubric(requirements, score_range)
    
    # Save the generated rubric
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scorer.save_rubric(str(output_path))
    
    print(f"\nGenerated rubric saved to: {output_path.absolute()}")
    print(f"Score range used: {score_range[0]} - {score_range[1]}")
    
    # Display rubric summary
    rubric_criteria = custom_rubric.get('criteria', {})
    print(f"\nRubric Summary:")
    print(f"  Number of rubric items: {len(rubric_criteria)}")
    for criterion, details in rubric_criteria.items():
        print(f"  - {criterion.replace('_', ' ').title()}: {details['weight']:.1%} weight")
    
    print("\nRubric generation complete!")


def rank(args):
    """
    Rank/score extracted content using AI-powered scoring.
    """
    # Load environment variables
    load_dotenv()
    
    # Get available models
    available_models = get_model_config()
    
    if not available_models:
        print("Error: No API keys found in environment variables. Please check your .env file.")
        sys.exit(1)
    
    if args.model not in available_models:
        print(f"Error: Model {args.model} not available. Available models: {', '.join(available_models.keys())}")
        sys.exit(1)
    
    # Load extracted data
    input_path = Path(args.input_data)
    if not input_path.exists():
        print(f"Error: Input data file does not exist: {input_path}")
        sys.exit(1)
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            extracted_data = json.load(f)
    except Exception as e:
        print(f"Error loading extracted data: {e}")
        sys.exit(1)
    
    # Load requirements
    requirements = ""
    if args.requirements:
        req_path = Path(args.requirements)
        if not req_path.exists():
            print(f"Error: Requirements file does not exist: {req_path}")
            sys.exit(1)
        requirements = load_requirements(str(req_path))
        if not requirements:
            print("Warning: Requirements file is empty or could not be loaded")
    
    # Initialize scorer
    api_key = available_models[args.model]
    scorer = RubricScorer(model_name=args.model, api_key=api_key, timeout=args.timeout)
    
    # Load custom rubric if provided
    if args.rubric_file:
        rubric_path = Path(args.rubric_file)
        if rubric_path.exists():
            scorer.load_rubric(str(rubric_path))
            print(f"Loaded custom rubric from: {rubric_path}")
        else:
            print(f"Warning: Rubric file not found: {rubric_path}")
    
    # Filter items that need scoring (score is 0 or missing)
    items_to_score = []
    items_already_scored = []
    
    for item in extracted_data:
        current_score = item.get('score', 0)
        if current_score == 0:
            items_to_score.append(item)
        else:
            items_already_scored.append(item)
    
    print(f"Ranking content using model: {args.model}")
    print(f"Total items in file: {len(extracted_data)}")
    print(f"Items already scored (score > 0): {len(items_already_scored)}")
    print(f"Items to be scored (score = 0): {len(items_to_score)}")
    print("-" * 50)
    
    # Score items that need scoring
    scored_count = 0
    for item in tqdm(items_to_score, desc="Scoring content", unit="item"):
        extracted_text = item.get('extracted_text', '').strip()
        if extracted_text:
            try:
                score_result = scorer.score_content(extracted_text, requirements)
                item['score'] = score_result.get('total_score', 0)
                item['score_details'] = str(score_result.get('scores', {}))
                item['recommendation'] = score_result.get('recommendation', '')
                item['overall_assessment'] = score_result.get('overall_assessment', '')
                scored_count += 1
            except Exception as e:
                print(f"\nError scoring {item.get('file_name', 'unknown')}: {e}")
                item['score'] = 0
                item['score_details'] = f"Scoring error: {str(e)}"
                item['recommendation'] = 'manual_review'
                item['overall_assessment'] = 'Error in evaluation'
        else:
            item['score'] = 0
            item['score_details'] = 'No text content to score'
            item['recommendation'] = 'no_content'
            item['overall_assessment'] = 'No extractable content'
    
    # Sort by score (highest first)
    extracted_data.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Save ranked data
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nRanked data saved to: {output_path.absolute()}")
    
    # Display ranking summary
    all_scores = [item['score'] for item in extracted_data if item.get('score', 0) > 0]
    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        max_score = max(all_scores)
        min_score = min(all_scores)
        
        print(f"\nRanking Summary:")
        print(f"  Total items with scores: {len(all_scores)}")
        print(f"  Items newly scored: {scored_count}")
        print(f"  Items previously scored: {len(items_already_scored)}")
        print(f"  Average score: {avg_score:.1f}")
        print(f"  Highest score: {max_score:.1f}")
        print(f"  Lowest score: {min_score:.1f}")
        
        # Show top 5 items
        print(f"\nTop 5 ranked items:")
        for i, item in enumerate(extracted_data[:5], 1):
            score = item.get('score', 0)
            name = item.get('file_name', 'unknown')
            recommendation = item.get('recommendation', 'unknown')
            print(f"  {i}. {name} - Score: {score:.1f} - {recommendation}")
    
    print("\nRanking complete!")


def convert_json_to_csv(args):
    """
    Convert ranked JSON data to CSV format.
    """
    try:
        # Load JSON data
        with open(args.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("No data found in the input file.")
            return
        
        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define the columns to include
        columns = ['file_path', 'score', 'recommendation', 'overall_assessment']
        
        # Write CSV file
        with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for item in data:
                # Extract only the required columns
                row = {col: item.get(col, '') for col in columns}
                writer.writerow(row)
        
        print(f"Successfully converted {len(data)} records to CSV: {args.output}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error converting to CSV: {e}")
        sys.exit(1)

def copy_qualified_resumes(args):
    """Copy qualified resumes to a specified directory based on score criteria."""
    try:
        # Load ranked data
        with open(args.input_file, 'r', encoding='utf-8') as f:
            ranked_data = json.load(f)
        
        # Create output directory if it doesn't exist
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Filter resumes based on criteria
        qualified_resumes = []
        
        if args.min_score is not None:
            # Copy all resumes with score >= min_score
            qualified_resumes = [
                item for item in ranked_data 
                if isinstance(item.get('score'), (int, float)) and item['score'] >= args.min_score
            ]
            print(f"Found {len(qualified_resumes)} resumes with score >= {args.min_score}")
        else:
            # Copy top N resumes by score
            # Sort by score in descending order, handling None/invalid scores
            valid_scored_items = [
                item for item in ranked_data 
                if isinstance(item.get('score'), (int, float))
            ]
            sorted_resumes = sorted(valid_scored_items, key=lambda x: x['score'], reverse=True)
            qualified_resumes = sorted_resumes[:args.num]
            print(f"Selecting top {len(qualified_resumes)} resumes by score")
        
        if not qualified_resumes:
            print("No qualified resumes found matching the criteria.")
            return
        
        # Copy files
        copied_count = 0
        failed_count = 0
        
        print(f"\nCopying {len(qualified_resumes)} resumes to {output_dir}...")
        
        for item in tqdm(qualified_resumes, desc="Copying files"):
            source_path = Path(item['file_path'])
            
            if not source_path.exists():
                print(f"Warning: Source file not found: {source_path}")
                failed_count += 1
                continue
            
            # Create destination filename with score prefix for easy identification
            score = item.get('score', 0)
            original_name = source_path.name
            dest_filename = f"{score:.1f}_{original_name}"
            dest_path = output_dir / dest_filename
            
            try:
                shutil.copy2(source_path, dest_path)
                copied_count += 1
            except Exception as e:
                print(f"Error copying {source_path}: {e}")
                failed_count += 1
        
        # Create summary file
        summary_data = {
            "criteria": {
                "min_score": args.min_score,
                "num_top": args.num if args.min_score is None else None
            },
            "total_qualified": len(qualified_resumes),
            "copied_successfully": copied_count,
            "failed_to_copy": failed_count,
            "copied_files": [
                {
                    "original_path": item['file_path'],
                    "score": item.get('score', 0),
                    "recommendation": item.get('recommendation', 'N/A')
                }
                for item in qualified_resumes
            ]
        }
        
        summary_file = output_dir / "copy_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nCopy complete!")
        print(f"Successfully copied: {copied_count} files")
        if failed_count > 0:
            print(f"Failed to copy: {failed_count} files")
        print(f"Summary saved to: {summary_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{args.input_file}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during copy operation: {e}")
        sys.exit(1)

def main():
    """
    Main CLI application entry point with subcommands.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get available models
    available_models = get_model_config()
    
    # Set up main argument parser
    parser = argparse.ArgumentParser(
        description="AI-powered file processing and ranking system",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser(
        'extract',
        help='Extract text and metadata from files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rank-flow extract /path/to/directory
  rank-flow extract /path/to/archive.zip
  rank-flow extract -v /path/to/directory
        """
    )
    
    extract_parser.add_argument(
        "input_path",
        help="Directory path or zip file to process"
    )
    
    extract_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    extract_parser.add_argument(
        "-o", "--output",
        default="output/extracted_data.json",
        help="Output file for extracted data (default: output/extracted_data.json)"
    )
    
    # Generate rubric command
    rubric_parser = subparsers.add_parser(
        'generate-rubric',
        help='Generate scoring rubric based on requirements',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rank-flow generate-rubric -r requirements.txt
  rank-flow generate-rubric -r job_description.txt -m deepseek-r1
        """
    )
    
    rubric_parser.add_argument(
        "-r", "--requirements",
        required=True,
        help="Path to requirements text file (required)"
    )
    
    rubric_parser.add_argument(
        "-m", "--model",
        choices=list(available_models.keys()) if available_models else ['jiutian-lan'],
        default='jiutian-lan' if 'jiutian-lan' in available_models else list(available_models.keys())[0] if available_models else 'jiutian-lan',
        help=f"AI model to use for rubric generation (available: {', '.join(available_models.keys()) if available_models else 'none configured'})"
    )
    
    rubric_parser.add_argument(
        "-o", "--output",
        default="output/generated_rubric.json",
        help="Output file for generated rubric (default: output/generated_rubric.json)"
    )
    
    rubric_parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="API request timeout in seconds (default: 30.0)"
    )
    
    rubric_parser.add_argument(
        "--score-range",
        nargs=2,
        type=int,
        default=[0, 100],
        metavar=('MIN', 'MAX'),
        help="Score range for rubric generation (default: 0 100)"
    )
    
    # Rank command
    rank_parser = subparsers.add_parser(
        'rank',
        help='Rank/score extracted content using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rank-flow rank -i extracted_data.json -r requirements.txt
  rank-flow rank -i extracted_data.json -r requirements.txt --rubric-file custom_rubric.json
        """
    )
    
    rank_parser.add_argument(
        "-i", "--input-data",
        required=True,
        help="Path to extracted data JSON file (required)"
    )
    
    rank_parser.add_argument(
        "-r", "--requirements",
        help="Path to requirements text file"
    )
    
    rank_parser.add_argument(
        "-m", "--model",
        choices=list(available_models.keys()) if available_models else ['jiutian-lan'],
        default='jiutian-lan' if 'jiutian-lan' in available_models else list(available_models.keys())[0] if available_models else 'jiutian-lan',
        help=f"AI model to use for scoring (available: {', '.join(available_models.keys()) if available_models else 'none configured'})"
    )
    
    rank_parser.add_argument(
        "--rubric-file",
        help="Path to custom rubric JSON file"
    )
    
    rank_parser.add_argument(
        "-o", "--output",
        default="output/ranked_data.json",
        help="Output file for ranked data (default: output/ranked_data.json)"
    )
    
    rank_parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="API request timeout in seconds (default: 30.0)"
    )
    
    # Convert command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert ranked JSON data to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rank-flow convert -i output/ranked_data.json
  rank-flow convert -i output/ranked_data.json -o results.csv
        """
    )
    
    convert_parser.add_argument(
        "-i", "--input-file",
        default="output/ranked_data.json",
        help="Path to ranked JSON data file (default: output/ranked_data.json)"
    )
    
    convert_parser.add_argument(
        "-o", "--output",
        default="output/ranked_data.csv",
        help="Output CSV file path (default: output/ranked_data.csv)"
    )
    
    # Copy command
    copy_parser = subparsers.add_parser(
        'copy',
        help='Copy qualified resumes to a specified directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rank-flow copy -i output/ranked_data.json --num 10
  rank-flow copy -i output/ranked_data.json --min-score 75
  rank-flow copy -i output/ranked_data.json --num 5 -o output/top_candidates/
        """
    )
    
    copy_parser.add_argument(
        "-i", "--input-file",
        default="output/ranked_data.json",
        help="Path to ranked JSON data file (default: output/ranked_data.json)"
    )
    
    copy_parser.add_argument(
        "-o", "--output-dir",
        default="output/top_candidates/",
        help="Output directory for copied resumes (default: output/top_candidates/)"
    )
    
    # Mutually exclusive group for selection criteria
    selection_group = copy_parser.add_mutually_exclusive_group()
    
    selection_group.add_argument(
        "--num",
        type=int,
        default=5,
        help="Copy the top N resumes with highest scores (default: 5)"
    )
    
    selection_group.add_argument(
        "--min-score",
        type=float,
        help="Copy all resumes with score >= this value"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute appropriate command
    if args.command == 'extract':
        extract(args)
    elif args.command == 'generate-rubric':
        generate_rubric(args)
    elif args.command == 'rank':
        rank(args)
    elif args.command == 'convert':
        convert_json_to_csv(args)
    elif args.command == 'copy':
        copy_qualified_resumes(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()