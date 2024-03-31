

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
	def __repr__(self) -> str:
		return f"HTMLNode(tag:{self.tag}, value:{self.value}, children:{self.children}, props:{self.props})"

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
