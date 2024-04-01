from textnode import TextNode, TextType, text_to_textnodes
from enum import Enum
import re

class BlockType(Enum):
	paragraph = 1
	heading = 2
	code = 3
	quote = 4
	unordered_list = 5
	ordered_list = 6

class HTMLNode:
	"""
	The HTMLNode class will represent a "node" in an HTML document tree (like a <p> tag and its contents, or an <a> tag and its contents) and is purpose-built to render itself as HTML.
	- An HTMLNode without a tag will just render as raw text
	- An HTMLNode without a value will be assumed to have children
	- An HTMLNode without children will be assumed to have a value
	- An HTMLNode without props simply won't have any attributes
	"""
	def __init__(self, tag: str | None = None, value: str | None = None, children: list | None = None, props: dict | None = None) -> None:
		self.tag = tag
		self.value = value
		self.children = children
		self.props = props

	def to_html(self) -> str:
		raise NotImplementedError
	def props_to_html(self) -> str:
		if not self.props:
			return ""
		return "".join(f' {attr}="{val}"' for attr, val in self.props.items())
	def __eq__(self, other) -> bool:
		return (self.tag == other.tag and
                self.value == other.value and
                self.children == other.children and
                self.props == other.props)
	def __repr__(self) -> str:
		tag = f'"{self.tag}"' if self.tag is not None else str(self.tag)
		value = f'"{self.value}"' if self.value is not None else str(self.value)

		return f'HTMLNode(tag:{tag}, value:{value}, children:{self.children}, props:{self.props})'

class LeafNode(HTMLNode):
	def __init__(self, tag: str | None = None, value: str | None = None, props: dict | None = None) -> None:
		assert value is not None, f"Value required"
		super().__init__(tag=tag, value=value, props=props)
	def to_html(self) -> str:
		if self.value is None:
			raise ValueError("No value found", self)
		if not self.tag:
			return self.value
		return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
	
class ParentNode(HTMLNode):
	def __init__(self, tag: str | None = None, children: list[HTMLNode] | None = None, props: dict | None = None) -> None:
		assert children, "Children required"
		super().__init__(tag=tag, children= children, props=props)
	def to_html(self) -> str:
		if not self.tag:
			raise ValueError("No tag found")
		if not self.children:
			raise ValueError("No children found")
		children_html = "".join(child.to_html() for child in self.children)
		return f'<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>'

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

def markdown_to_blocks(markdown:str) -> list[str]:
    '''It takes a raw Markdown string (representing a full document) as input and returns a list of "block" strings.'''
    blocks = markdown.split('\n\n')
    blocks = map(lambda b: b.strip('\n'), blocks)
    return list(filter(lambda b: b is not None and b, blocks))

def block_to_block_type(md_block:str) -> BlockType:
	if md_block.startswith(('#', '##', '###', '#'*4, '#'*5, '#'*6)):
		return BlockType.heading
	if md_block.startswith('```') and md_block.endswith('```'):
		return BlockType.code
	if all(line.startswith('>') for line in md_block.splitlines()):
		return BlockType.quote
	if all(line.startswith(('*', '-')) for line in md_block.splitlines()):
		return BlockType.unordered_list
	if all(len(line) >= 2 and line.startswith(f'{i}.')
			for i, line in enumerate(md_block.splitlines(), 1)):
		return BlockType.ordered_list
	return BlockType.paragraph

def block_to_html_node_heading(heading:str) -> HTMLNode:
	matches = re.findall("(#*)", heading)
	level = len(matches[0])
	return LeafNode(f'h{level}', heading.lstrip('# '))

def block_to_html_node_ul(ul:str) -> HTMLNode:
	items = ul.splitlines()
	children:list[HTMLNode] = list(map(lambda li: LeafNode("li", li.lstrip("-*").lstrip()), items))
	return ParentNode("ul", children)

def block_to_html_node_ol(ol:str) -> HTMLNode:
	items = ol.splitlines()
	children:list[HTMLNode] = list(map(lambda li: LeafNode("li", li.split('.', 1)[1].lstrip()), items))
	return ParentNode("ol", children)

def block_to_html_node(md_block:str, block_type:BlockType) -> HTMLNode:
	mapping = {
		BlockType.paragraph: (LeafNode, ("p", md_block)),
		BlockType.heading: (block_to_html_node_heading, [md_block]),
		BlockType.code: (LeafNode, ("code", md_block.strip("`").strip())),
		BlockType.quote: (LeafNode, ("blockquote", "\n".join(line.lstrip('> ') for line in md_block.splitlines()))),
		BlockType.unordered_list: (block_to_html_node_ul, [md_block]),
		BlockType.ordered_list: (block_to_html_node_ol, [md_block])
	}
	if block_type in mapping:
		f, args = mapping[block_type]
		return f(*args)
	else:
		raise Exception(f"Text type not supported {block_type}")

def htmlnode_to_htmlnode_with_inlines(html_leaf:HTMLNode) -> HTMLNode:
	assert html_leaf.value
	textnodes = text_to_textnodes(html_leaf.value)
	if len(textnodes) == 1 and textnodes[0].text_type == TextType.TEXT:
		new_html = html_leaf
	else:
		htmlnodes = list(map(lambda n: text_node_to_html_node(n), textnodes))
		new_html = ParentNode(html_leaf.tag, htmlnodes)
	return new_html

def markdown_to_html_node(markdown:str) -> HTMLNode:
	'''
	It converts a full markdown document into an HTMLNode.
	The top-level HTMLNode should just be a <div>, where each child is a block of the document.
	Each block should have its own "inline" children.
	'''
	md_blocks = markdown_to_blocks(markdown)
	html_nodes = list(map(lambda b: block_to_html_node(b, block_to_block_type(b)), md_blocks))
	new_html_nodes = []
	for hn in html_nodes:
		# if not hb.value and not hb.children:
		# 	raise Exception(f'HTMLNode with neither value nor children')
		if hn.tag == 'code':
			new_hn = hn
		elif hn.tag == "ol" or hn.tag == 'ul':
			assert hn.children
			hn.children = list(map(lambda li: htmlnode_to_htmlnode_with_inlines(li), hn.children))
			new_hn = hn
		else:
			new_hn = htmlnode_to_htmlnode_with_inlines(hn)
		new_html_nodes.append(new_hn)
	return ParentNode("div", new_html_nodes)
