import unittest
from query_analyzer import analyze_query, get_analysis_report
from optimizer import optimize_query, get_optimization_stats, normalize_keyword, remove_redundant_clauses

class TestQueryOptimizer(unittest.TestCase):
    def test_optimize_query(self) -> None:
        """Test that the optimize_query function optimizes a query correctly."""
        original_query = "The quick brown fox jumps over the lazy dog. The quick brown fox."
        optimized_query = optimize_query(original_query)
        self.assertIsInstance(optimized_query, str)
        self.assertNotEqual(original_query, optimized_query)

    def test_get_optimization_stats(self) -> None:
        """Test that the get_optimization_stats function returns the correct stats."""
        query = "The quick brown fox jumps over the lazy dog. The quick brown fox."
        stats = get_optimization_stats(query)
        self.assertIsInstance(stats, dict)
        self.assertIn("token_count", stats)
        self.assertIn("redundant_clauses_removed", stats)

    def test_normalize_keyword(self) -> None:
        """Test that the normalize_keyword function normalizes keywords correctly."""
        keyword = "Quick"
        normalized_keyword = normalize_keyword(keyword)
        self.assertEqual(normalized_keyword, "quick")

    def test_remove_redundant_clauses(self) -> None:
        """Test that the remove_redundant_clauses function removes redundant clauses correctly."""
        query = "The quick brown fox jumps over the lazy dog. The quick brown fox."
        optimized_query = remove_redundant_clauses(query)
        self.assertNotIn("The quick brown fox.", optimized_query)

class TestQueryAnalyzer(unittest.TestCase):
    def test_analyze_query(self) -> None:
        """Test that the analyze_query function analyzes a query correctly."""
        query = "The quick brown fox jumps over the lazy dog. The quick brown fox."
        analysis = analyze_query(query)
        self.assertIsInstance(analysis, dict)
        self.assertIn("total_tokens", analysis)
        self.assertIn("unique_keywords", analysis)
        self.assertIn("emails_count", analysis)
        self.assertIn("urls_count", analysis)

    def test_get_analysis_report(self) -> None:
        """Test that the get_analysis_report function generates a report correctly."""
        query = "The quick brown fox jumps over the lazy dog. The quick brown fox."
        report = get_analysis_report(query)
        self.assertIsInstance(report, str)
        self.assertIn("Total Tokens:", report)
        self.assertIn("Unique Keywords:", report)
        self.assertIn("Emails Count:", report)
        self.assertIn("URLs Count:", report)

if __name__ == "__main__":
    unittest.main()