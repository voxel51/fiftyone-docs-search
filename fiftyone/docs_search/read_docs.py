"""
Declaration of document reading functions.
| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

from glob import glob
import os.path
import os
import re

from langchain.schema import Document
from langchain.text_splitter import MarkdownTextSplitter

import fiftyone.core.utils as fou

md = fou.lazy_import("markdownify")

################################################################

splitter = MarkdownTextSplitter(chunk_size=1000)


def get_docs_list():
    FO_DIR = os.getenv("FIFTYONE_DIR")
    FO_HTML_DOCS_DIR = os.path.join(FO_DIR, "docs/build/html")

    all_docs = []
    for pattern in ["*/*.html", "*/*/*.html"]:
        all_docs += glob(
            os.path.join(FO_HTML_DOCS_DIR, pattern), recursive=True
        )
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


def remove_extra_newlines(page_md):
    lines = page_md.split("\n")
    lines = [line for line in lines if line.strip() != "!"]
    page_md = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", page_md)


def remove_empty_code_blocks(page_md):
    text_and_code = page_md.split("```")
    text_blocks = text_and_code[::2]
    code_blocks = text_and_code[1::2]
    code_blocks = [
        cb
        for cb in code_blocks
        if len(cb.strip()) > 0 and not set(cb).issubset(set("| -\n"))
    ]

    page_md = ""
    for tb, cb in zip(text_blocks, code_blocks):
        page_md += tb + "```" + cb + "```"

    page_md += text_and_code[-1]
    return re.sub(r"```py\s*```", "", page_md, flags=re.MULTILINE)


def remove_jupyter_widgets(page_md):
    lines = page_md.split("\n")
    lines = [
        line
        for line in lines
        if len(line) == 0 or (line[0] != "{" and "jupyter-widgets" not in line)
    ]
    return "\n".join(lines)


def remove_xml(page_md):
    lines = page_md.split("\n")
    lines = [line for line in lines if not line.startswith("<?xml")]
    return "\n".join(lines)


def _remove_code_block_line_numbers(code_block):
    lines = code_block.split("\n")
    lines = [re.sub(r"^\s*\d+\s*", "", line) for line in lines]
    return "\n".join(lines)


def remove_line_numbers(page_md):
    text_and_code = page_md.split("```")
    text_blocks = text_and_code[::2]
    code_blocks = text_and_code[1::2]
    code_blocks = [_remove_code_block_line_numbers(cb) for cb in code_blocks]

    page_md = ""
    for tb, cb in zip(text_blocks, code_blocks):
        page_md += tb + "```" + cb + "```"

    page_md += text_and_code[-1]
    return page_md


def remove_table_rows(page_md):
    lines = page_md.split("\n")
    lines = [
        line
        for line in lines
        if len(line) == 0 or not set(line).issubset(set("| -"))
    ]
    return "\n".join(lines)


def remove_images(page_md):
    page_md = re.sub("!\[\]\(data:image\/png;base64.*?\)", "", page_md)
    page_md = re.sub(r"^![\w-]+$", "", page_md, flags=re.MULTILINE)
    return page_md


def remove_code_cell_vestiges(page_md):
    return re.sub(r"^\[\s*\d*\]:$", "", page_md, flags=re.MULTILINE)


def add_syntax_highlight_to_code_blocks(page_md):
    text_and_code = page_md.split("```")
    text_blocks = text_and_code[::2]
    code_blocks = text_and_code[1::2]
    code_blocks = [
        cb
        for cb in code_blocks
        if len(cb.strip()) > 0 and not set(cb).issubset(set("| -"))
    ]

    page_md = ""
    for tb, cb in zip(text_blocks, code_blocks):
        page_md += tb + "```py" + cb + "```"

    page_md += text_and_code[-1]
    return page_md


def merge_adjacent_code_blocks(page_md):
    pattern = r"```\n```py"
    page_md = re.sub(pattern, "", page_md)
    return re.sub(r"```py\n```py", r"```py", page_md)


def remove_bad_elements(page_md):
    pattern = r"\(function\(\) {[\s\S]*?}\)\(\);"
    page_md = re.sub(pattern, "", page_md, flags=re.MULTILINE)

    lines = page_md.split("\n")
    lines = [line for line in lines if not line.startswith("@import")]

    bad_keywords = [
        "#focontainer",
        "#fooverlay",
        "#foactivate",
    ]

    good_lines = []
    flag = True
    for line in lines:
        if any([keyword in line for keyword in bad_keywords]):
            flag = False
        if flag:
            good_lines.append(line)
        if "}" in line and not flag:
            flag = True

    return "\n".join(good_lines)


def remove_links(page_md):
    match = re.search("\[.*?\]\(.*?\)", page_md)
    if match is not None:
        start, end = match.span()
        link = page_md[start:end]
        link_text = link[1:].split("]")[0]
        if link_text != "¶":
            return page_md[:start] + link_text + remove_links(page_md[end:])
        else:
            return page_md[:end] + link + remove_links(page_md[end:])
    return page_md


def reformat_markdown(page_md):
    page_md = page_md.replace("\_", "_").replace("\*", "*")
    page_md = remove_links(page_md)
    page_md = remove_images(page_md)
    page_md = remove_jupyter_widgets(page_md)
    page_md = remove_xml(page_md)
    page_md = remove_extra_newlines(page_md)
    page_md = remove_bad_elements(page_md)
    page_md = remove_code_cell_vestiges(page_md)
    return page_md


def remove_unicode(page_md):
    for uchar in ["\u2500", "\u2514", "\u251c", "\u2502"]:
        page_md = page_md.replace(uchar, "")
    for uchar in ["\u2588", "\u2019"]:
        page_md = page_md.replace(uchar, "'")
    for uchar in ["\u201d", "\u201c"]:
        page_md = page_md.replace(uchar, '"')
    page_md = page_md.replace("\u00a9", "copyright")
    return page_md


def parse_page_markdown(page_md):
    page_md = remove_header(page_md)
    page_md = remove_footer(page_md)
    page_md = remove_line_numbers(page_md)
    page_md = remove_table_rows(page_md)
    page_md = remove_empty_code_blocks(page_md)
    page_md = add_syntax_highlight_to_code_blocks(page_md)
    page_md = merge_adjacent_code_blocks(page_md)

    ## reformat now that the markdown is clean
    page_md = reformat_markdown(page_md)
    page_md = remove_empty_code_blocks(page_md)
    page_md = remove_extra_newlines(page_md)
    page_md = remove_unicode(page_md)
    return page_md


def get_page_markdown(filepath):
    with open(filepath) as f:
        page_html = f.read()

    page_md = md.markdownify(page_html, heading_style="ATX")
    page_md = parse_page_markdown(page_md)

    return page_md


def split_at_anchors(page_md):
    md_lines = page_md.split("\n")
    md_sections = {}
    curr_anchor = None
    curr_section = []
    for line in md_lines:
        if "Permalink" in line:
            if curr_anchor is not None:
                md_sections[curr_anchor] = "\n".join(curr_section)
            curr_section = []
            curr_anchor = line.split('"Permalink')[0].split("#")[-1].strip()
        else:
            curr_section.append(line)

    md_sections[curr_anchor] = "\n".join(curr_section)
    return md_sections


def split_section_into_chunks(text):
    document = Document(page_content=text)
    documents = splitter.split_documents([document])
    return [d.page_content for d in documents]


def split_page_into_chunks(page_md):
    md_sections = split_at_anchors(page_md)
    chunks = {}
    for anchor, section in md_sections.items():
        chunks[anchor] = split_section_into_chunks(section)

    return chunks


def get_markdown_documents(filepath):
    page_md = get_page_markdown(filepath)
    return split_page_into_chunks(page_md)
