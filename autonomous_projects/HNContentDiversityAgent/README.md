# HNContentDiversityAgent

## Overview
The HNContentDiversityAgent is a specialized agent designed to analyze and curate content from Hacker News (HN) to enhance diversity and interest, providing a more engaging and varied front page experience. The project is divided into several components, each responsible for a specific part of the data processing pipeline.

## Architecture
### Components
- **hn_data_collector.py**: Fetches and returns a list of Hacker News (HN) posts.
- **content_analyzer.py**: Analyzes the diversity of HN posts based on their titles and content.
- **content_curator.py**: Curates a diverse set of posts based on their diversity scores.
- **presentation_layer.py**: Formats and presents the curated content in a user-friendly format.
- **test_main.py**: Contains unit tests for each component and integration tests for the entire pipeline.

### Data Flow
1. **Data Collection**: `hn_data_collector.py` fetches the top stories from HN and collects their metadata.
2. **Content Analysis**: `content_analyzer.py` preprocesses the text, calculates diversity scores, and analyzes the diversity of the posts.
3. **Curation**: `content_curator.py` curates a diverse set of posts based on their diversity scores.
4. **Presentation**: `presentation_layer.py` formats and presents the curated content.

## How it Works
### 1. Data Collection
The `get_hn_posts` function in `hn_data_collector.py` fetches the top stories from HN and collects their metadata. It uses the HN API to get the IDs of the top stories and then fetches the details of each story.

```python
from hn_data_collector import get_hn_posts

posts = get_hn_posts()
print(posts)
```

### 2. Content Analysis
The `analyze_diversity` function in `content_analyzer.py` preprocesses the text, calculates diversity scores, and analyzes the diversity of the posts. It combines the title and content of each post, preprocesses the text, and calculates a diversity score.

```python
from content_analyzer import analyze_diversity

diversity_scores = analyze_diversity(posts)
print(diversity_scores)
```

### 3. Curation
The `curate_content` function in `content_curator.py` curates a diverse set of posts based on their diversity scores. It sorts the posts by their diversity scores and selects the top 10 diverse posts.

```python
from content_curator import curate_content

curated_posts = curate_content(posts, diversity_scores)
print(curated_posts)
```

### 4. Presentation
The `present_content` function in `presentation_layer.py` formats and presents the curated content in a user-friendly format. It generates a formatted string that lists the curated posts with their titles, authors, scores, and URLs.

```python
from presentation_layer import present_content

presentation = present_content(curated_posts)
print(presentation)
```

## Running the Project
To run the HNContentDiversityAgent, you can use the following steps:

1. Install the required dependencies:
   ```bash
   pip install requests nltk
   ```

2. Run the main script:
   ```python
   from hn_data_collector import get_hn_posts
   from content_analyzer import analyze_diversity
   from content_curator import curate_content
   from presentation_layer import present_content

   # Step 1: Data Collection
   posts = get_hn_posts()

   # Step 2: Content Analysis
   diversity_scores = analyze_diversity(posts)

   # Step 3: Curation
   curated_posts = curate_content(posts, diversity_scores)

   # Step 4: Presentation
   presentation = present_content(curated_posts)
   print(presentation)
   ```

## Testing
The `test_main.py` file contains unit tests for each component and integration tests for the entire pipeline. You can run the tests using the following command:
```bash
python -m unittest test_main.py
```

## Configuration
There are no specific configuration files or settings required for this project. The HN API endpoints and other parameters are hardcoded in the respective files. If you need to modify any parameters, you can do so directly in the code.