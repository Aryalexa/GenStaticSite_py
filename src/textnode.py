
from htmlnode import LeafNode, HTMLNode
from enum import Enum
import re

class TextType(Enum):
    TEXT = 1
    BOLD = 2
    ITALIC = 3
    CODE = 4
    LINK = 5
    IMAGE = 6

class TextNode:
    def __init__(self, text:str, text_type:TextType, url:str|None=None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (self.text == other.text and
                self.text_type == other.text_type and
                self.url == other.url)

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.name}, {self.url})"

def text_node_to_html_node(text_node:TextNode) -> HTMLNode:
    mapping = {
        TextType.TEXT: (LeafNode,{"value":text_node.text}),
        TextType.BOLD: (LeafNode, {"tag":'b', "value":text_node.text}),
        TextType.ITALIC: (LeafNode, {"tag":'i', "value":text_node.text}),
        TextType.CODE: (LeafNode, {"tag":'code', "value":text_node.text}), 
        TextType.LINK: (LeafNode, {"tag":'a', "value":text_node.text, "props":{"href":text_node.url}}),
        TextType.IMAGE:(LeafNode, {"tag":'img', "value":"", "props":{"src":text_node.url, "alt":text_node.text}}),
    }
    if text_node.text_type in mapping:
        f, kwargs = mapping[text_node.text_type]
        return f(**kwargs)
    else:
        raise Exception(f"Text type not supported {text_node.text_type}")

def split_nodes_delimiter(old_nodes:list[TextNode], delimiter:str, text_type:TextType) -> list:
    new_nodes = []
    for old_node in old_nodes:
        if not isinstance(old_node, TextNode):
            new_nodes.append(old_node)
            continue
        parts = old_node.text.split(delimiter)
        if len(parts) % 2 != 1:
            raise Exception(f"matching closing delimiter {delimiter} is not found.")
        for i in range(0, len(parts)-1, 2):
            if parts[i]:
                new_nodes.append(TextNode(parts[i], old_node.text_type))
            new_nodes.append(TextNode(parts[i + 1], text_type))
        if parts[-1]:
            new_nodes.append(TextNode(parts[-1], old_node.text_type))
    return new_nodes

def extract_markdown_images(text:str) -> list[tuple[str, str]]:
    img_pattern = r"!\[(.*?)\]\((.*?)\)"
    matches = re.findall(img_pattern, text)
    return matches

def extract_markdown_links(text:str) -> list[tuple[str,str]]:
    link_pattern = r"\[(.*?)\]\((.*?)\)"
    matches = re.findall(link_pattern, text)
    return matches

def split_nodes_image(old_nodes:list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        imgs = extract_markdown_images(old_node.text)
        if not imgs:
            new_nodes.append(old_node)
            continue
        text = old_node.text
        for alt, url in imgs:
            before, after = text.split(f"![{alt}]({url})", 1)
            if before:
                new_nodes.append(TextNode(before, old_node.text_type))
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            text = after
        if text:
            new_nodes.append(TextNode(text, old_node.text_type))
    return new_nodes

def split_nodes_links(old_nodes:list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        lnks = extract_markdown_links(old_node.text)
        if not lnks:
            new_nodes.append(old_node)
            continue
        text = old_node.text
        for link_text, url in lnks:
            before, after = text.split(f"[{link_text}]({url})", 1)
            if before:
                new_nodes.append(TextNode(before, old_node.text_type))
            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            text = after
        if text:
            new_nodes.append(TextNode(text, old_node.text_type))
    return new_nodes

def text_to_textnodes(text:str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, '**', TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, '*', TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, '`', TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_links(nodes)
    return nodes
