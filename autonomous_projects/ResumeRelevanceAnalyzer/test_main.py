import json
import os
import subprocess
import sys
import tempfile
import unittest
from typing import List, Dict

from src.parser import parse_document
from src.scorer import compute_relevance
from src.cli import main


class TestParser(unittest.TestCase):
    def test_parse_document_normal_case(self) -> None:
        lines = [
            "Experience:",
            "Worked at Google from 2020 to 2023.",
            "Skills:",
            "Python, Java, C++",
            "Education:",
            "BSc in Computer Science"
        ]
        result = parse_document(lines)
        expected = {
            'experience': ['worked', 'at', 'google', 'from', '2020', 'to', '2023.'],
            'skills': ['python,', 'java,', 'c++'],
            'education': ['bsc', 'in', 'computer', 'science']
        }
        self.assertEqual(result, expected)

    def test_parse_document_empty_input(self) -> None:
        result = parse_document([])
        self.assertEqual(result, {})

    def test_parse_document_malformed_headers(self) -> None:
        lines = [
            "Not a header",
            "Another line without colon",
            "Valid Header:",
            "Content here",
            "Invalid:Header",  # no space before colon
            "More content"
        ]
        result = parse_document(lines)
        expected = {
            'valid header': ['content', 'here', 'invalid:header', 'more', 'content']
        }
        self.assertEqual(result, expected)

    def test_parse_document_unicode(self) -> None:
        lines = [
            "Résumé Sections:",
            "Worked with naïve algorithms and café culture."
        ]
        result = parse_document(lines)
        expected = {
            'résumé sections': ['worked', 'with', 'naïve', 'algorithms', 'and', 'café', 'culture.']
        }
        self.assertEqual(result, expected)

    def test_parse_document_multiple_whitespace(self) -> None:
        lines = [
            "Summary:",
            "   This    is     a      test.   "
        ]
        result = parse_document(lines)
        expected = {
            'summary': ['this', 'is', 'a', 'test.']
        }
        self.assertEqual(result, expected)

    def test_parse_document_no_content_after_header(self) -> None:
        lines = ["Header:"]
        result = parse_document(lines)
        expected = {'header': []}
        self.assertEqual(result, expected)


class TestScorer(unittest.TestCase):
    def test_compute_relevance_full_match(self) -> None:
        resume = {
            'requirements': ['python', 'java', 'sql'],
            'preferred': ['aws', 'docker']
        }
        job_post = {
            'requirements': ['python', 'java', 'sql'],
            'preferred': ['aws', 'docker']
        }
        result = compute_relevance(resume, job_post)
        self.assertAlmostEqual(result['score'], 100.0)
        self.assertEqual(result['missing'], [])

    def test_compute_relevance_partial_match(self) -> None:
        resume = {
            'requirements': ['python', 'sql'],
            'preferred': ['docker']
        }
        job_post = {
            'requirements': ['python', 'java', 'sql'],
            'preferred': ['aws', 'docker']
        }
        result = compute_relevance(resume, job_post)
        # requirements: 2/3 matched (weight 1.0 each) → 2.0 / 3.0
        # preferred: 1/2 matched (weight 0.5 each) → 0.5 / 1.0
        # total weight = 3.0 + 1.0 = 4.0
        # matched weight = 2.0 + 0.5 = 2.5
        # score = (2.5 / 4.0) * 100 = 62.5
        self.assertAlmostEqual(result['score'], 62.5)
        self.assertEqual(set(result['missing']), {'java', 'aws'})

    def test_compute_relevance_no_match(self) -> None:
        resume = {
            'requirements': ['c++', 'rust'],
            'preferred': ['kubernetes']
        }
        job_post = {
            'requirements': ['python', 'java'],
            'preferred': ['aws']
        }
        result = compute_relevance(resume, job_post)
        self.assertAlmostEqual(result['score'], 0.0)
        self.assertEqual(set(result['missing']), {'python', 'java', 'aws'})

    def test_compute_relevance_ignores_unweighted_sections(self) -> None:
        resume = {
            'requirements': ['python'],
            'education': ['bsc']
        }
        job_post = {
            'requirements': ['python'],
            'education': ['msc']  # not weighted, so ignored
        }
        result = compute_relevance(resume, job_post)
        self.assertAlmostEqual(result['score'], 100.0)
        self.assertEqual(result['missing'], [])

    def test_compute_relevance_empty_job_post(self) -> None:
        resume = {'requirements': ['python']}
        job_post = {}
        result = compute_relevance(resume, job_post)
        self.assertAlmostEqual(result['score'], 0.0)
        self.assertEqual(result['missing'], [])

    def test_compute_relevance_case_insensitive_section_matching(self) -> None:
        resume = {
            'Requirements': ['python'],
            'PREFERRED': ['aws']
        }
        job_post = {
            'requirements': ['python', 'java'],
            'preferred': ['aws', 'docker']
        }
        result = compute_relevance(resume, job_post)
        self.assertAlmostEqual(result['score'], 50.0)  # only python and aws matched
        self.assertEqual(set(result['missing']), {'java', 'docker'})


class TestCLI(unittest.TestCase):
    def _run_cli(self, resume_content: str, job_content: str) -> subprocess.CompletedProcess:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as rf:
            rf.write(resume_content)
            resume_path = rf.name

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as jf:
            jf.write(job_content)
            job_path = jf.name

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'src.cli', resume_path, job_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            return result
        finally:
            os.unlink(resume_path)
            os.unlink(job_path)

    def test_cli_valid_files(self) -> None:
        resume = "Requirements:\nPython Java SQL\nPreferred:\nAWS Docker"
        job = "Requirements:\nPython Java\nPreferred:\nAWS"
        result = self._run_cli(resume, job)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertIn('score', output)
        self.assertIn('missing', output)
        self.assertIsInstance(output['score'], (int, float))
        self.assertGreaterEqual(output['score'], 0.0)
        self.assertLessEqual(output['score'], 100.0)
        self.assertIsInstance(output['missing'], list)

    def test_cli_unicode_content(self) -> None:
        resume = "Requirements:\nPython naïve café"
        job = "Requirements:\nPython naïve"
        result = self._run_cli(resume, job)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertAlmostEqual(output['score'], 100.0)
        self.assertEqual(output['missing'], [])

    def test_cli_empty_resume_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            resume_path = f.name
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write("Requirements:\nPython")
            job_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'src.cli', resume_path, job_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("empty", result.stderr.lower())
        finally:
            os.unlink(resume_path)
            os.unlink(job_path)

    def test_cli_nonexistent_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write("Requirements:\nPython")
            job_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'src.cli', '/nonexistent/resume.txt', job_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("not found", result.stderr.lower())
        finally:
            os.unlink(job_path)

    def test_cli_no_overlap_score_zero(self) -> None:
        resume = "Requirements:\nC++ Rust"
        job = "Requirements:\nPython Java"
        result = self._run_cli(resume, job)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertAlmostEqual(output['score'], 0.0)
        self.assertEqual(set(output['missing']), {'python', 'java'})


if __name__ == '__main__':
    unittest.main()