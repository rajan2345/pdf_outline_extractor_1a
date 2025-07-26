#!/usr/bin/env python3
"""
Adobe India Hackathon 2025 - Round 1A
PDF Outline Extraction Main Entry Point - Heuristic Only
"""
import os
import sys
import argparse
import json
import logging
import time
import gc
from pathlib import Path
from typing import Dict, List, Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append('/app/src')

from extractor import extract_outline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def process_pdf(pdf_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Process a single PDF file."""
    start_time = time.time()
    
    try:
        # Extract outline
        result = extract_outline(str(pdf_path))
        
        # Prepare output filename
        output_filename = pdf_path.stem + '.json'
        output_path = output_dir / output_filename
        
        # Save result
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        processing_time = time.time() - start_time
        logger.info(f"✓ Processed {pdf_path.name} in {processing_time:.2f}s")
        
        return {
            'success': True,
            'filename': pdf_path.name,
            'output_file': output_filename,
            'processing_time': processing_time,
            'headings_count': len(result.get('outline', [])),
            'title': result.get('title', ''),
            'doc_type': result.get('metadata', {}).get('document_type', 'unknown')
        }
    
    except Exception as e:
        logger.error(f"✗ Failed to process {pdf_path.name}: {e}")
        
        # Create error output
        error_output = {
            "title": "",
            "outline": [],
            "metadata": {
                "error": str(e),
                "processing_time": time.time() - start_time
            }
        }
        
        output_filename = pdf_path.stem + '.json'
        output_path = output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(error_output, f, indent=2, ensure_ascii=False)
        
        return {
            'success': False,
            'filename': pdf_path.name,
            'error': str(e),
            'processing_time': time.time() - start_time
        }

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Adobe India Hackathon 2025 - Round 1A PDF Outline Extractor (Heuristic Only)'
    )
    
    parser.add_argument(
        '--input_dir',
        type=str,
        default='/app/input',
        help='Input directory containing PDF files'
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        default='/app/output',
        help='Output directory for JSON files'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup paths
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    # Validate input directory
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find PDF files
    pdf_files = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        sys.exit(0)
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process files
    results = []
    total_start_time = time.time()
    
    for pdf_path in pdf_files:
        result = process_pdf(pdf_path, output_dir)
        results.append(result)
        
        # Memory cleanup
        gc.collect()
    
    # Calculate statistics
    total_time = time.time() - total_start_time
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    total_headings = sum(r.get('headings_count', 0) for r in results if r['success'])
    
    # Document type statistics
    doc_types = {}
    for r in results:
        if r['success']:
            doc_type = r.get('doc_type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Adobe India Hackathon 2025 - Round 1A Results (Heuristic Only)")
    print(f"{'='*60}")
    print(f"Total files processed: {len(pdf_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total headings extracted: {total_headings}")
    print(f"Total processing time: {total_time:.2f} seconds")
    print(f"Average time per file: {total_time/len(pdf_files):.2f} seconds")
    print(f"Document types detected: {doc_types}")
    
    # Save detailed results
    summary = {
        'total_files': len(pdf_files),
        'successful': successful,
        'failed': failed,
        'total_headings': total_headings,
        'total_time': total_time,
        'document_types': doc_types,
        'results': results
    }
    
    with open(output_dir / 'processing_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Results saved to: {output_dir}")
    print(f"{'='*60}")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == '__main__':
    main()
