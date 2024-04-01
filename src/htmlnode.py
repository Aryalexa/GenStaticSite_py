
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
		return f'HTMLNode(tag:"{self.tag}", value:"{self.value}", children:{self.children}, props:{self.props})'

class LeafNode(HTMLNode):
	def __init__(self, tag: str | None = None, value: str | None = None, props: dict | None = None) -> None:
		assert value, "Value required"
		super().__init__(tag=tag, value=value, props=props)
	def to_html(self) -> str:
		if not self.value:
			raise ValueError("No value found")
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

def markdown_to_blocks(markdown:str) -> list[str]:
    '''It takes a raw Markdown string (representing a full document) as input and returns a list of "block" strings.'''
    blocks = markdown.split('\n\n')
    blocks = map(lambda b: b.strip('\n'), blocks)
    return list(filter(lambda b: b is not None, blocks))

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
	print('items', items)
	children:list[HTMLNode] = list(map(lambda li: LeafNode("li", li.split('.', 1)[1].lstrip()), items))
	return ParentNode("ol", children)

def block_to_html_node(md_block:str, block_type:BlockType) -> HTMLNode:
	mapping = {
		BlockType.paragraph: (LeafNode, ["p", md_block]),
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
