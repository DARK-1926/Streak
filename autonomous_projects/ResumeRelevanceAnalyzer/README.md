# ResumeRelevanceAnalyzer

ResumeRelevanceAnalyzer scores how well your resume matches a job post—offline, no AI. It helps job seekers identify which applications are worth pursuing by analyzing the alignment between resume content and job requirements.

## Features

- **Offline Processing**: No internet connection required, no data leaves your machine
- **ATS-Aware Scoring**: Mimics common Applicant Tracking System (ATS) keyword matching
- **Section-Aware Analysis**: Understands document structure (Skills, Experience, Requirements, etc.)
- **Weighted Scoring**: Prioritizes critical requirements over nice-to-have skills
- **Missing Keywords Report**: Shows specific terms to add to improve match rate
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **No Dependencies**: Uses only Python standard library
- **Memory Efficient**: Uses memory mapping for large file handling

## How it Works

The analyzer operates in three stages:

1. **Parsing**: The `parser.py` module identifies document sections (like "Skills:", "Experience:", "Requirements:") and normalizes the text by converting to lowercase and collapsing whitespace.

2. **Keyword Extraction**: Each section is split into individual words/terms that serve as keywords for matching.

3. **Relevance Scoring**: The `scorer.py` module compares keywords between the resume and job description, applying different weights:
   - Requirements: Full weight (1.0)
   - Preferred qualifications: Half weight (0.5)
   - Other sections: Ignored for scoring

The final score represents the percentage of weighted keywords from the job posting that appear in the corresponding resume sections.

## Installation

No installation required! This tool uses only Python standard library components.

Requires Python 3.8 or higher.

## Usage

```bash
python -m src.cli resume.txt job.txt
```

### Example

```bash
# Analyze resume.txt against job_description.txt
python -m src.cli my_resume.txt job_posting.txt
```

Output:
```json
{
  "score": 75.5,
  "missing": ["AWS", "Docker", "microservices"]
}
```

## Input Format

Both input files should be plain text with clear section headers ending in colons:

```
Experience:
- Worked at Company A for 3 years
- Led team of 5 developers

Skills:
- Python, JavaScript, SQL
- AWS, Docker, Kubernetes

Education:
- B.S. Computer Science
```

## Output

The tool outputs a JSON object with:
- `score`: A number between 0.0 and 100.0 indicating match percentage
- `missing`: An array of keywords from the job posting not found in the resume

## Architecture

- `src/parser.py`: Contains `parse_document()` for section-aware text parsing
- `src/scorer.py`: Contains `compute_relevance()` for weighted keyword matching
- `src/cli.py`: Command-line interface with memory-mapped file handling
- `test_main.py`: Comprehensive unit tests covering all functionality

## Testing

Run the full test suite with:
```bash
python -m pytest test_main.py -v
```

Tests cover:
- Normal parsing scenarios
- Edge cases (empty files, malformed text, Unicode)
- Correct scoring calculations
- CLI argument handling
- Cross-platform compatibility

## Contributing

This project welcomes contributions. Please ensure all new code includes:
- Type hints for all function signatures
- Complete docstrings
- Unit tests covering new functionality
- Adherence to PEP 8 style guidelines

## License

MIT License - see LICENSE file for details.