import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    # def test_eq(self):
    #     node = HTMLNode("p", "this is a paragraph")
    #     node2 = HTMLNode("p", "this is a paragraph")
    #     self.assertEqual(node, node2)
    def test_props_to_html_link(self):
        node = HTMLNode("a", "link", props={"href": "https://www.google.com", "target": "_blank"})
        html = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), html)

class TestLeafNode(unittest.TestCase):
    def test_to_html_p(self):
        node = LeafNode("p", "This is a paragraph of text.")
        html = "<p>This is a paragraph of text.</p>"
        self.assertEqual(node.to_html(), html)
    def test_to_html_a(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        html = '<a href="https://www.google.com">Click me!</a>'
        self.assertEqual(node.to_html(), html)


class TestParentNode(unittest.TestCase):
    def test_to_html1(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        html = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        self.assertEqual(node.to_html(), html)
    def test_to_html_nested(self):
        node = ParentNode(
            "div",
            [
                ParentNode(
                    "p",
                    [
                        LeafNode("b", "Bold text"),
                        LeafNode(None, "Normal text"),
                        LeafNode("i", "italic text"),
                        LeafNode(None, "Normal text"),
                    ],
                ),
                LeafNode("a", "Click me!", props={"href": "https://www.google.com"}),

            ],
        )
        html = '<div><p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p><a href="https://www.google.com">Click me!</a></div>'
        self.assertEqual(node.to_html(), html)

if __name__ == "__main__":
    unittest.main()

