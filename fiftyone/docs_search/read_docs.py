"""
Declaration of document reading functions.
| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

from glob import glob
from markdownify import markdownify
import os.path
import os
import re

################################################################



def get_docs_list():
    FO_DIR = os.getenv('FIFTYONE_DIR')
    FO_HTML_DOCS_DIR = os.path.join(FO_DIR, 'docs/build/html')
    
    all_docs = []
    for pattern in ['*/*.html', '*/*/*.html']:
        all_docs += glob(os.path.join(FO_HTML_DOCS_DIR, pattern), recursive=True)
    return [doc for doc in all_docs if "api/" not in doc]

################################################################
def remove_footer(page_md):
    return page_md.split("[Next ![]")[0]

def remove_header(page_md):
    md_lines = page_md.split("\n")

    body_lines = []
    in_body = False
    for mdl in md_lines:
        if len(mdl) > 0 and mdl[0] == "#":
            in_body = True
        if in_body:
            body_lines.append(mdl)
    page_md = "\n".join(body_lines)
    return page_md

def remove_line_numbers(page_md):
    lines = page_md.split('\n')
    lines = [
        re.sub(r'^\s*\d+\s*', '', line)
        for line in lines
    ]
    
    page_md = '\n'.join(lines)
    return page_md

def remove_table_rows(page_md):
    lines = page_md.split('\n')
    lines = [line
        for line in lines
        if len(line) == 0 or not set(line).issubset(set("| -"))
        ]
    page_md = '\n'.join(lines)
    return page_md

def remove_extra_newlines(page_md):
    page_md = re.sub(r'\n{3,}', '\n\n', page_md)
    return page_md

def remove_unicode(page_md):
    for uchar in ["\u2500", "\u2514", "\u251c", "\u2502"]:
        page_md = page_md.replace(uchar, "")
    for uchar in ["\u2588", "\u2019"]:
        page_md = page_md.replace(uchar, "'")
    for uchar in ["\u201d", "\u201c"]:
        page_md = page_md.replace(uchar, "\"")
    page_md = page_md.replace("\u00a9", "copyright")
    return page_md

def remove_bolding(page_md):
    page_md = page_md.replace("**", "")
    return page_md

def remove_empty_code_blocks(page_md):
    parts = page_md.split('```')
    parts = [
            p
            for i, p in enumerate(parts)
            if i % 2 == 0 or p != "\n"
            ]
    return "```".join(parts)

################################################################

def remove_links(page_md):
    match = re.search('\[.*?\]\(.*?\)', page_md)
    if match is not None:
        start, end = match.span()
        link = page_md[start:end]
        link_text = link[1:].split(']')[0]
        if link_text != "¶":
            return page_md[:start] + link_text + remove_links(page_md[end:])
        else:
            return page_md[:end] + link + remove_links(page_md[end:])
    return page_md

def remove_images(page_md):
    return re.sub('!\[\]\(data:image\/png;base64.*?\)', '', page_md)

def remove_jupyter_widgets(page_md):
    lines = page_md.split('\n')
    lines = [
        line
        for line in lines
        if len(line)==0 or (line[0]!= "{" and "jupyter-widgets" not in line)
    ]
    return "\n".join(lines)

def remove_xml(page_md):
    lines = page_md.split('\n')
    lines = [line for line in lines if not line.startswith('<?xml')]
    return "\n".join(lines)

def reformat_markdown(page_md):
    page_md = page_md.replace("\_", "_").replace("\*", "*")
    page_md = remove_links(page_md)
    page_md = remove_images(page_md)
    page_md = remove_jupyter_widgets(page_md)
    page_md = remove_xml(page_md)
    return page_md

################################################################

def parse_page_markdown(page_md):
    page_md = remove_header(page_md)
    page_md = remove_footer(page_md)
    page_md = remove_line_numbers(page_md)
    page_md = remove_table_rows(page_md)
    page_md = remove_extra_newlines(page_md)
    page_md = remove_empty_code_blocks(page_md)
    page_md = remove_extra_newlines(page_md)
    page_md = remove_bolding(page_md)
    page_md = remove_unicode(page_md)

    ### reformat now that the markdown is clean
    page_md = reformat_markdown(page_md)
    return page_md

################################################################

def get_page_markdown(html_file):
    with open(html_file) as f:
        page_html = f.read()
    page_md = markdownify(page_html, heading_style="ATX")
    page = parse_page_markdown(page_md)
    return page

################################################################
