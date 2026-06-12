import sys
import os
import json
import argparse
import requests
from html.parser import HTMLParser
from collections import Counter

class LintHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.missing_alt = []
        self.ids = []
        self.inline_styles = []
        self.deprecated_tags = []
        self.deprecated_set = {'font', 'center', 'marquee'}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        # check alt on img
        if tag == 'img' and 'alt' not in attrs_dict:
            self.missing_alt.append(self.getpos())
        # collect ids
        if 'id' in attrs_dict:
            self.ids.append(attrs_dict['id'])
        # inline style detection
        if 'style' in attrs_dict:
            self.inline_styles.append((tag, self.getpos()))
        # deprecated tags
        if tag in self.deprecated_set:
            self.deprecated_tags.append((tag, self.getpos()))

class FrontEndLinter:
    def __init__(self, source, is_url=False):
        self.source = source
        self.is_url = is_url
        self.content = ''
        self.parser = LintHTMLParser()
        self.report = {}

    def load_content(self):
        if self.is_url:
            try:
                resp = requests.get(self.source, timeout=5)
                resp.raise_for_status()
                self.content = resp.text
            except Exception as e:
                raise RuntimeError(f'Failed to fetch URL: {e}')
        else:
            if not os.path.isfile(self.source):
                raise FileNotFoundError(f'File not found: {self.source}')
            try:
                with open(self.source, 'r', encoding='utf-8') as f:
                    self.content = f.read()
            except UnicodeDecodeError:
                with open(self.source, 'r', encoding='latin-1') as f:
                    self.content = f.read()
        if not self.content.strip():
            raise ValueError('Content is empty')

    def run_checks(self):
        self.parser.feed(self.content)
        # missing alt count
        self.report['missing_alt'] = len(self.parser.missing_alt)
        # duplicate ids
        id_counts = Counter(self.parser.ids)
        dup_ids = {i: c for i, c in id_counts.items() if c > 1}
        self.report['duplicate_ids'] = dup_ids
        # inline styles
        self.report['inline_styles'] = len(self.parser.inline_styles)
        # deprecated tags
        self.report['deprecated_tags'] = len(self.parser.deprecated_tags)

    def generate_report(self, as_json=False):
        if as_json:
            return json.dumps(self.report, indent=2)
        lines = []
        lines.append(f"Missing alt attributes on <img>: {self.report['missing_alt']}")
        if self.report['duplicate_ids']:
            dup = ', '.join([f'{k}({v})' for k, v in self.report['duplicate_ids'].items()])
            lines.append(f'Duplicate id attributes: {dup}')
        else:
            lines.append('Duplicate id attributes: None')
        lines.append(f'Inline style attributes: {self.report["inline_styles"]}')
        lines.append(f'Deprecated tags (font, center, marquee): {self.report["deprecated_tags"]}')
        return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='Lightweight CLI linter for AI‑generated HTML/CSS')
    parser.add_argument('source', help='Path to HTML file or URL')
    parser.add_argument('--url', action='store_true', help='Treat source as URL')
    parser.add_argument('--json', action='store_true', help='Output report as JSON')
    args = parser.parse_args()

    linter = FrontEndLinter(args.source, is_url=args.url)
    try:
        linter.load_content()
        linter.run_checks()
        output = linter.generate_report(as_json=args.json)
        print(output)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()