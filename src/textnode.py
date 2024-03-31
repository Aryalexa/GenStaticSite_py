from enum import Enum

class TextType(Enum):
    bold = 1
    italic = 2
    link = 3
    image = 4

class TextNode:
    def __init__(self, text:str, text_type:str, url:str=None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (self.text == other.text and
                self.text_type == other.text_type and
                self.url == other.url)

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"

