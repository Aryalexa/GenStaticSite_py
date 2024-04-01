import os
import shutil
import re
from htmlnode import markdown_to_html_node


def log(*msgs):
    print(*msgs)

def copy_directory(src_dir:str, dst_dir:str):
    print(f"copying... {src_dir} -> {dst_dir}")
    if not os.path.exists(src_dir):
        raise Exception(f'source directory not found {src_dir}')
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    if not os.path.exists(dst_dir):
        parent = os.path.dirname(dst_dir)
        if not os.path.exists(parent):
            raise Exception('destination parent directory does not exist.')
        os.mkdir(dst_dir)
    contents = os.listdir(src_dir)
    for file_or_dir in contents:
        content_src_dir = os.path.join(src_dir, file_or_dir)
        content_dst_dir = os.path.join(dst_dir, file_or_dir)
        if os.path.isfile(content_src_dir):
            copied_file = shutil.copy(content_src_dir, content_dst_dir)
            log("copied", copied_file)
        else:
            copy_directory(content_src_dir, content_dst_dir)

def extract_title(markdown:str) -> str:
    for line in markdown.splitlines():
        matches = re.findall(r"^#([^#].*)", line)
        if matches:
            return matches[0].strip()
    raise Exception("No title found")

def create_dir(directory:str) -> None:
    if os.path.exists(directory):
        return
    else:
        parent = os.path.dirname(directory)
        create_dir(parent)
        os.mkdir(directory)

def generate_page(from_path, template_path, dest_path):
    log(f"Generating page from {from_path} to {dest_path} using {template_path}")

    if not os.path.exists(from_path) or not os.path.isfile(from_path):
        raise Exception(f'Cannot read "from" from {from_path}')
    if not os.path.exists(template_path) or not os.path.isfile(template_path):
        raise Exception(f'Cannot read "template" from {template_path}') 
    with open(from_path) as from_file:
        markdown = from_file.read()
    with open(template_path) as template_file:
        template = template_file.read()
    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    template = template.replace('{{ Title }}', title).replace('{{ Content }}', html)
    if not os.path.exists(dest_path):
        parent = os.path.dirname(dest_path)
        if not os.path.exists(parent):
            create_dir(parent)
    with open(dest_path, 'w') as dest_file:
        dest_file.write(template)

def main():
    print('Hello')
    copy_directory("./static", "./public")
    generate_page("./content/index.md", "template.html", "public/index.html")
    print("done")

if __name__ == "__main__":
    main()
