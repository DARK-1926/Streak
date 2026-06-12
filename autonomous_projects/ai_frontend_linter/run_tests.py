import os
import json
from main import FrontEndLinter

# Create a temporary HTML snippet for testing
TEST_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <img src="a.jpg">
  <img src="b.jpg" alt="desc">
  <div id="dup"></div>
  <span id="dup"></span>
  <p style="color:red;">Styled</p>
  <font>Old tag</font>
</body>
</html>
'''

def write_temp_file(content, filename='temp_test.html'):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename

def test_linter_logic():
    tmp_path = write_temp_file(TEST_HTML)
    linter = FrontEndLinter(tmp_path)
    linter.load_content()
    linter.run_checks()
    report = linter.report
    assert report['missing_alt'] == 1, 'Should detect one img without alt'
    assert report['duplicate_ids'] == {'dup': 2}, 'Should detect duplicate id'
    assert report['inline_styles'] == 1, 'One inline style expected'
    assert report['deprecated_tags'] == 1, 'One deprecated tag (font) expected'
    os.remove(tmp_path)

if __name__ == '__main__':
    test_linter_logic()
    print('All tests passed')