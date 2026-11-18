import re
import unittest
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[1] / 'docs/research'


class ResearchIndexTest(unittest.TestCase):
    def test_every_research_file_is_indexed_and_links_resolve(self):
        index = (RESEARCH / 'README.md').read_text(encoding='utf-8')
        links = set(re.findall(r'\]\(([^)#]+)\)', index))
        files = {p.name for p in RESEARCH.iterdir() if p.suffix in ('.md', '.json') and p.name != 'README.md'}
        self.assertEqual(sorted(files - links), [], 'research files missing from the index')
        self.assertEqual(sorted(links - files), [], 'index links without a file')


if __name__ == '__main__':
    unittest.main()
