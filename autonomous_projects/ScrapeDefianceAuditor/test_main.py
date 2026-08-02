import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict, List, Optional

import auditor


class TestScrapeDefianceAuditor(unittest.TestCase):
    """Test suite for the ScrapeDefianceAuditor project."""

    def test_parse_robots_rules(self) -> None:
        """Test parsing of robots.txt rules."""
        lines: List[str] = [
            "User-agent: *",
            "Disallow: /private/",
            "Disallow: /admin",
            "Allow: /public/",
            "Disallow: "
        ]
        rules: List[re.Pattern] = auditor.parse_robots_rules(lines)
        
        self.assertEqual(len(rules), 2)
        self.assertTrue(rules[0].match("/private/data"))
        self.assertFalse(rules[0].match("/public/data"))
        self.assertTrue(rules[1].match("/admin/settings"))
        self.assertFalse(rules[1].match("/public/admin"))

    def test_parse_log_line(self) -> None:
        """Test parsing of Combined Log Format lines."""
        valid_line: str = (
            '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] '
            '"GET /apache_pb.gif HTTP/1.0" 200 2326 '
            '"http://www.example.com/start.html" "Mozilla/4.08"'
        )
        parsed: Optional[Dict[str, Any]] = auditor.parse_log_line(valid_line)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['ip'], '127.0.0.1')
        self.assertEqual(parsed['path'], '/apache_pb.gif')
        self.assertEqual(parsed['user_agent'], 'Mozilla/4.08')

        invalid_line: str = "this is not a valid log line"
        self.assertIsNone(auditor.parse_log_line(invalid_line))

    def test_audit_scrape_defiance(self) -> None:
        """Test the single-pass state machine for auditing scrape defiance."""
        rules: List[re.Pattern] = auditor.parse_robots_rules(["Disallow: /private/"])
        
        # Case A: IP fetches robots.txt then violates
        log_lines_a: List[str] = [
            '1.2.3.4 - - [10/Oct/2000:13:55:36 -0700] "GET /robots.txt HTTP/1.0" 200 2326 "-" "Bot/1.0"',
            '1.2.3.4 - - [10/Oct/2000:13:55:37 -0700] "GET /private/data HTTP/1.0" 200 2326 "-" "Bot/1.0"'
        ]
        results_a: Dict[str, Dict[str, Any]] = auditor.audit_scrape_defiance(log_lines_a, rules)
        
        self.assertIn('1.2.3.4', results_a)
        self.assertEqual(results_a['1.2.3.4']['violations'], 1)
        self.assertTrue(results_a['1.2.3.4']['seen_robots'])

        # Case B: IP violates without fetching robots.txt
        log_lines_b: List[str] = [
            '5.6.7.8 - - [10/Oct/2000:13:55:36 -0700] "GET /private/data HTTP/1.0" 200 2326 "-" "BadBot/1.0"'
        ]
        results_b: Dict[str, Dict[str, Any]] = auditor.audit_scrape_defiance(log_lines_b, rules)
        
        self.assertIn('5.6.7.8', results_b)
        self.assertEqual(results_b['5.6.7.8']['violations'], 1)
        self.assertFalse(results_b['5.6.7.8']['seen_robots'])

    def test_cli_integration(self) -> None:
        """Test CLI integration with dummy files."""
        robots_content: str = "User-agent: *\nDisallow: /private/\n"
        log_content: str = (
            '1.2.3.4 - - [10/Oct/2000:13:55:36 -0700] "GET /robots.txt HTTP/1.0" 200 2326 "-" "Bot/1.0"\n'
            '1.2.3.4 - - [10/Oct/2000:13:55:37 -0700] "GET /private/data HTTP/1.0" 200 2326 "-" "Bot/1.0"\n'
        )

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f_robots:
            f_robots.write(robots_content)
            robots_path: str = f_robots.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f_log:
            f_log.write(log_content)
            log_path: str = f_log.name

        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', log_path, robots_path],
                capture_output=True,
                text=True
            )

            self.assertEqual(result.returncode, 0)
            output: Dict[str, Any] = json.loads(result.stdout)
            self.assertIn('1.2.3.4', output)
            self.assertEqual(output['1.2.3.4']['violations'], 1)
        finally:
            if os.path.exists(robots_path):
                os.remove(robots_path)
            if os.path.exists(log_path):
                os.remove(log_path)

    def test_cli_empty_file(self) -> None:
        """Test CLI behavior with an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f_robots:
            robots_path: str = f_robots.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f_log:
            log_path: str = f_log.name

        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', log_path, robots_path],
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 1)
        finally:
            if os.path.exists(robots_path):
                os.remove(robots_path)
            if os.path.exists(log_path):
                os.remove(log_path)


if __name__ == '__main__':
    unittest.main()