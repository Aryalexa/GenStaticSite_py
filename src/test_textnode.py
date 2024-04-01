import unittest

from textnode import (
	TextNode, TextType, split_nodes_delimiter, extract_markdown_images, 
    extract_markdown_links, split_nodes_image, split_nodes_links, text_to_textnodes
)

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    def test_eq_nourl(self):
        node = TextNode("ex", TextType.LINK)
        node2 = TextNode("ex", TextType.LINK, "None")
        self.assertNotEqual(node, node2)

class TestSplitNodes(unittest.TestCase):
    # def assertListEqual(self, nodes, expected_nodes):
    #     self.assertEqual(len(nodes), len(expected_nodes))
    #     for n, en in zip(nodes, expected_nodes):
    #         self.assertEqual(n, en)

    # def test_splitdel_nothing(self):
    #     node = "This is just text and not a TextNode."
    #     new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
    #     expected_new_nodes = [node]
    #     self.assertListEqual(new_nodes, expected_new_nodes)
    
    def test_splitdel_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_new_nodes = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected_new_nodes)
    def test_splitdel_italic_err(self):
        node = TextNode("This is text with a *italic block* *word", TextType.TEXT)
        self.assertRaises(Exception, split_nodes_delimiter, *[[node], '*', TextType.ITALIC])
    
    def test_splitdel_italic(self):
        node = TextNode("This is text with a *italic block* *word*", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        expected_new_nodes = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("italic block", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("word", TextType.ITALIC)
        ]
        self.assertListEqual(new_nodes, expected_new_nodes)
    def test_splitdel_bold(self):
        node = TextNode("**bold** and nonbold and **bold****twice**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected_new_nodes = [
            TextNode("bold", TextType.BOLD),
            TextNode(" and nonbold and ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("twice", TextType.BOLD)
        ]
        self.assertListEqual(new_nodes, expected_new_nodes)

    def test_split_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
            )
        new_nodes = split_nodes_image([node])
        expected_new_nodes = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
        ]
        self.assertListEqual(new_nodes, expected_new_nodes)

    def test_split_image_empty(self):
        '''Split images when there is no images'''
        node = TextNode(
            "This is text has no links!",
            TextType.TEXT,
            )
        new_nodes = split_nodes_image([node])
        expected_new_nodes = [node]
        self.assertListEqual(new_nodes, expected_new_nodes)

    def test_split_links(self):
        node = TextNode(
            "This is text with an [link](https://i.imgur.com/zjjcJKZ.png) and another [second link](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
            )
        new_nodes = split_nodes_links([node])
        expected_new_nodes = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode("second link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"),
        ]
        self.assertListEqual(new_nodes, expected_new_nodes)

    def test_split_links2(self):
        '''link at the beginnig and at the end'''
        node = TextNode(
            "[link](https://i.imgur.com/zjjcJKZ.png) and [second link](https://i.imgur.com/3elNhQu.png)!",
            TextType.TEXT,
            )
        new_nodes = split_nodes_links([node])
        expected_new_nodes = [
            TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("second link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"),
            TextNode("!", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected_new_nodes)

    def test_text_to_textnodes(self):
        text = 'This is **text** with an *italic* word and a `code block` and an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://boot.dev)'
        nodes = text_to_textnodes(text)
        expected_nodes = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(nodes, expected_nodes)

    def test_text_to_textnodes_simple(self):
        text = 'This is a simple line'
        nodes = text_to_textnodes(text)
        expected_nodes = [
            TextNode("This is a simple line", TextType.TEXT)
        ]
        self.assertListEqual(nodes, expected_nodes)


class TestExtractMD(unittest.TestCase):
    def test_extract_images(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and ![another](https://i.imgur.com/dfsdkjfd.png)"
        imgs = extract_markdown_images(text)
        expected_imgs = [("image", "https://i.imgur.com/zjjcJKZ.png"), ("another", "https://i.imgur.com/dfsdkjfd.png")]
        self.assertEqual(len(imgs), len(expected_imgs))
        for img, eimg in zip(imgs, expected_imgs):
            self.assertEqual(img, eimg)
    def test_extract_links(self):
        text = "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)"
        links = extract_markdown_links(text)
        expected_links = [("link", "https://www.example.com"), ("another", "https://www.example.com/another")]
        self.assertEqual(len(links), len(expected_links))
        for lnk, elnk in zip(links, expected_links):
            self.assertEqual(lnk, elnk)

if __name__ == "__main__":
    unittest.main()

