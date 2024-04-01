import unittest

from htmlnode import (HTMLNode, LeafNode, ParentNode, markdown_to_blocks, 
                      block_to_block_type, BlockType, block_to_html_node,
                      markdown_to_html_node)


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

class TestBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        markdown = """This is **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items"""
        blocks = markdown_to_blocks(markdown)
        expected_blocks = ["This is **bolded** paragraph",
                           """This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line""",
                            """* This is a list
* with items"""
        ]
        self.assertListEqual(blocks, expected_blocks)

    def test_markdown_to_blocks2(self):
        markdown = """This is **bolded** paragraph


This is another paragraph with *italic* text and `code` here
"""
        blocks = markdown_to_blocks(markdown)
        expected_blocks = ["This is **bolded** paragraph",
                           "This is another paragraph with *italic* text and `code` here"
        ]
        self.assertListEqual(blocks, expected_blocks)

    def test_block_to_block_type(self):
        blocks = ["# Title",
                  "* uil 1\n* uil", "- uil 1\n* uil 2\n* next",
                  """```
                  this is code
                  ```""",
                  """> quote line 1
> quote line 2""",
                  """1. item a
2. item b
3. item c
4. i
5. cinco
6. six
7. 7lvn
8. ocho
9. nein
10. shib""",
                  """
oh nooo
djfidjf
dfdf
"""
                  ]
        types = list(map(lambda b: block_to_block_type(b), blocks))
        expected_types = [BlockType.heading, BlockType.unordered_list, BlockType.unordered_list, BlockType.code,
                          BlockType.quote, BlockType.ordered_list, BlockType.paragraph]
        self.assertListEqual(types, expected_types)

    def test_block_to_html_node(self):
        data = [
            {
                "block":"#   Title #",
                "type": BlockType.heading,
                "html_node": LeafNode("h1", "Title #")
            },
            {
                "block":"* uil 1\n* uil",
                "type": BlockType.unordered_list,
                "html_node": ParentNode("ul", [
                    LeafNode("li", "uil 1"),
                    LeafNode("li", "uil")
                ])
            },
            {
                "block":"- uil 1\n* uil 2\n* next\n* **hello**",
                "type": BlockType.unordered_list,
                "html_node": ParentNode("ul", [
                    LeafNode("li", "uil 1"),
                    LeafNode("li", "uil 2"),
                    LeafNode("li", "next"),
                    LeafNode("li", "**hello**"),
                ]),
            },
            {
                "block":"""```
                  this is code
                  ```""",
                "type": BlockType.code,
                "html_node": LeafNode("code", "this is code")
            },
            {
                "block":"""> quote line 1
> quote line 2""",
                "type": BlockType.quote,
                "html_node": LeafNode("blockquote", "quote line 1\nquote line 2"),
            },
            {
                "block": """1. item a
2. item b
3.  item c""",
                "type": BlockType.ordered_list,
                "html_node": ParentNode("ol", [
                    LeafNode("li", "item a"),
                    LeafNode("li", "item b"),
                    LeafNode("li", "item c")
                ])
            },
            {
                "block": """oh nooo
djfidjf
dfdf""",
                "type": BlockType.paragraph,
                "html_node": LeafNode("p", """oh nooo
djfidjf
dfdf""")
            },
            {
                "block": "hey",
                "type": BlockType.paragraph,
                "html_node": LeafNode("p", "hey")
            }
        ]
        
        html_nodes = list(map(lambda d: block_to_html_node(d["block"], d["type"]), data))
        expected_html_nodes = list(map(lambda d: d["html_node"], data))
        self.assertListEqual(html_nodes, expected_html_nodes)

class TestMDtoHTML(unittest.TestCase):
    def test_markdown_to_html_node_simple(self):
        md = """
# Hi I'm the title #1

hey

"""       
        expected_html = ParentNode("div", [
            LeafNode("h1", "Hi I'm the title #1"),
            LeafNode("p", "hey")
        ])
        html = markdown_to_html_node(md)
        self.assertEqual(html, expected_html)

    def test_markdown_to_html_node_bi_in_p(self):
        md = """
# Hi I'm the title #1

hey this is **bold** and this *italic*

"""       
        expected_html = ParentNode("div", [
            LeafNode("h1", "Hi I'm the title #1"),
            ParentNode("p", [
                LeafNode(None, "hey this is "),
                LeafNode("b", "bold"),
                LeafNode(None, " and this "),
                LeafNode("i", "italic")
            ])
        ])
        html = markdown_to_html_node(md)
        self.assertEqual(html, expected_html)

    def test_markdown_to_html_node_imglink_in_p(self):
        md = """
# Hi I'm the title #1

hey this is an ![image](https://i.imgur.com/zjjcJKZ.png) and this a [link](https://i.imgur.com/3elNhQu.png)!

"""       
        expected_html = ParentNode("div", [
            LeafNode("h1", "Hi I'm the title #1"),
            ParentNode("p", [
                LeafNode(None, "hey this is an "),
                LeafNode("img", "", props={"src":"https://i.imgur.com/zjjcJKZ.png", "alt":"image"}),
                LeafNode(None, " and this a "),
                LeafNode("a", "link", props={"href":"https://i.imgur.com/3elNhQu.png"}),
                LeafNode(None, "!"),
            ])
        ])
        html = markdown_to_html_node(md)
        self.assertEqual(html, expected_html)
    
    def test_markdown_to_html_node_list(self):
        md = """
# Hi I'm the title #1

hey

* hi
* and
*   i'm a list"""       
        expected_html = ParentNode("div", [
            LeafNode("h1", "Hi I'm the title #1"),
            LeafNode("p", "hey"),
            ParentNode("ul", [
                LeafNode("li", "hi"),
                LeafNode("li", "and"),
                LeafNode("li", "i'm a list"),
            ])
        ])
        html = markdown_to_html_node(md)
        self.assertEqual(html, expected_html)
    
    def test_markdown_to_html_node_list_b(self):
        md = """
# Hi I'm the title #1

hey

1. look below
2. there is a **bold word** here
"""       
        expected_html = ParentNode("div", [
            LeafNode("h1", "Hi I'm the title #1"),
            LeafNode("p", "hey"),
            ParentNode("ol", [
                LeafNode("li", "look below"),
                ParentNode("li", [
                    LeafNode(None, "there is a "),
                    LeafNode("b", "bold word"),
                    LeafNode(None, " here")
                ]),
            ])
        ])
        html = markdown_to_html_node(md)
        self.assertEqual(html, expected_html)

    def test_markdown_to_html_node_code(self):
        md = """
# Hi I'm the title #1

hey

```
# this is real code
s, *ss = my_list
func(*args)
```
"""       
        expected_html = ParentNode("div", [
            LeafNode("h1", "Hi I'm the title #1"),
            LeafNode("p", "hey"),
            LeafNode("code", """# this is real code
s, *ss = my_list
func(*args)"""),
        ])
        html = markdown_to_html_node(md)
        self.assertEqual(html, expected_html)

    def test_markdown_to_html_node_quote(self):
        md = """
# Hi I'm the title #1

> quoting *me*
> quoting **you** and
> quoting `code`.
"""       
        expected_html = ParentNode("div", [
            LeafNode("h1", "Hi I'm the title #1"),
            ParentNode("blockquote", [
                LeafNode(None, "quoting "),
                LeafNode("i", "me"),
                LeafNode(None, "\nquoting "),
                LeafNode("b", "you"),
                LeafNode(None, " and\nquoting "),
                LeafNode("code", "code"),
                LeafNode(None, ".")
            ])
        ])
        html = markdown_to_html_node(md)
        self.assertEqual(html, expected_html)

    def test_markdown_to_html_node_h2(self):
        md = """
## Hi I'm the title **#1**

hey
"""       
        expected_html = ParentNode("div", [
            ParentNode("h2",[
                LeafNode(None, "Hi I'm the title "),
                LeafNode("b", "#1")
            ] ),
            LeafNode("p", "hey"),
        ])
        html = markdown_to_html_node(md)
        self.assertEqual(html, expected_html)


if __name__ == "__main__":
    unittest.main()

