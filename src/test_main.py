import unittest
from main import extract_title

class TestGenPage(unittest.TestCase):
	def test_extract_title(self):
		md = """

# title
"""
		expected_title = "title"
		title = extract_title(md)
		self.assertEqual(title, expected_title)
	
	def test_extract_title_sticked(self):
		md = """
#title #1  
"""
		expected_title = "title #1"
		title = extract_title(md)
		self.assertEqual(title, expected_title)
	
	def test_extract_title_spaced(self):
		md = """#   title
"""
		expected_title = "title"
		title = extract_title(md)
		self.assertEqual(title, expected_title)
	
if __name__ == "__main__":
	unittest.main()