from typing import Dict, List, Set


def compute_relevance(resume: Dict[str, List[str]], job_post: Dict[str, List[str]]) -> Dict[str, object]:
    """
    Compute a weighted relevance score between a resume and a job posting.

    This function compares keywords from key sections of the job posting against
    corresponding sections in the resume. Sections are weighted as follows:
      - 'requirements': weight = 1.0
      - 'preferred': weight = 0.5

    The relevance score is calculated as:
        (sum of weights of matched keywords / total weight of all job keywords) * 100

    Additionally, a list of missing keywords (those not found in the resume) is returned.

    Args:
        resume: A dictionary mapping section names to lists of normalized words,
                as produced by `parse_document`.
        job_post: A dictionary mapping section names to lists of normalized words,
                  as produced by `parse_document`.

    Returns:
        A dictionary with two keys:
          - 'score': a float representing the percentage match (0.0 to 100.0)
          - 'missing': a list of strings representing keywords from the job post
                       that were not found in the corresponding resume sections.
    """
    # Define section weights
    section_weights = {
        'requirements': 1.0,
        'preferred': 0.5
    }

    total_weight = 0.0
    matched_weight = 0.0
    missing_keywords: List[str] = []

    # Normalize section names in resume for case-insensitive matching
    resume_sections = {section.lower(): set(words) for section, words in resume.items()}

    for section_name, job_keywords in job_post.items():
        normalized_section = section_name.lower()
        if normalized_section not in section_weights:
            continue  # Skip sections not in our weighting scheme

        weight = section_weights[normalized_section]
        resume_words = resume_sections.get(normalized_section, set())

        for keyword in job_keywords:
            total_weight += weight
            if keyword in resume_words:
                matched_weight += weight
            else:
                missing_keywords.append(keyword)

    # Avoid division by zero if job_post has no relevant keywords
    if total_weight == 0.0:
        score = 0.0
    else:
        score = (matched_weight / total_weight) * 100.0

    return {
        'score': score,
        'missing': missing_keywords
    }