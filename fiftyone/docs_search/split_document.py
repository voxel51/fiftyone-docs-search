"""
Declaration of document splitting functions.
| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import re

################################################################

def strip_table(line):
    if len(line) >= 2 and line[0] == "|" and line[-1] == "|":
        return line.replace("|", "").strip()
    else:
        return line

def strip_tables_and_whitespace(subsection_content):
    subsection_content = subsection_content.strip()
    subsection_content = strip_table(subsection_content)
    return subsection_content.replace("\n", " ")

def format_section_text_and_code(section):
    text_and_code = section.split('```')
    text = text_and_code[::2]
    code = text_and_code[1::2]
    return text, code

################################################################
##### VALIDATION FUNCTIONS #####################################

def validate(subsection_content):
    val_content = subsection_content.strip()

    vl_cond = validate_length(val_content)
    note_cond = subsection_content != "Note"
    blank_code_line_cond = re.match(r'^\[\d+\]:', val_content) is None
    net_cond = validate_nonempty_text(val_content)
    js_cond = validate_non_javascript(val_content)
    mathjax_cond = validate_non_mathjax(val_content)
    return vl_cond and note_cond and blank_code_line_cond and js_cond and mathjax_cond and net_cond

def validate_non_javascript(subsection_content):
    js_strings = [
        "(function() {",
        "@import url(",
        "position: relative;",
        "getElementById",
        "addEventListener",
        "eventList",
        "document.body",
        "the_modal",
        "window.dataLayer"
    ]

    for js_string in js_strings:
        if js_string in subsection_content:
            return False
    return True

def validate_nonempty_text(subsection_content):
    return not set(subsection_content).issubset(set(" *+|\n"))

def validate_non_mathjax(subsection_content):
    return "MathJax" not in subsection_content

def validate_length(subsection_content):
    scl = len(subsection_content)
    return scl > 4


################################################################
#### SPLITTING INTO SECTIONS ###################################

def extract_title_and_anchor(header):
    header = " ".join(header.split(" ")[1:])
    title = header.split("[")[0]
    anchor = header.split("(")[1].split(" ")[0][1:]
    return title, anchor

def split_page_into_sections(page_md):
    text_and_code = page_md.split('```')
    text = text_and_code[::2]
    code = text_and_code[1::2]

    sections = {}
    curr_section_content = ''
    section_key = None

    for i, text_block in enumerate(text):
        text_block_lines = text_block.split('\n')
        for line in text_block_lines:
            if len(line)>0 and line[0] == "#" and "(" in line:
                if curr_section_content != '':
                    sections[section_key] = curr_section_content
                    curr_section_content = ""

                title, anchor = extract_title_and_anchor(line)
                curr_section_content += f"{title}:"
                section_key = anchor

            else:
                if len(line)>0 and line[0] == "#" and " " in line:
                    curr_section_content += "\n" + line.split(" ")[1] + ":"
                else:
                    curr_section_content += "\n" + line
        if i < len(code):
            curr_section_content += '\n```' + code[i] + '```'
    
    sections[section_key] = curr_section_content
    return sections

################################################################
#### SPLITTING INTO SUBSECTIONS ################################

def add_subsection(subsection_content, subsections, block_type):
    if validate(subsection_content):
        subsection = {
            "type": block_type,
            "content": strip_tables_and_whitespace(subsection_content)
        }

        subsections.append(subsection)

def add_text_block(text_block, subsections):
    ### handle one case in Model Zoo 
    if len(text_block) > 16000:
        text_block = text_block.split("Note")[0]
    add_subsection(text_block, subsections, block_type = "text")

def add_code_block(code_block, subsections):
    add_subsection(code_block, subsections, block_type = "code")

def split_section_into_subsections(section):
    text_blocks, code_blocks = format_section_text_and_code(section)

    subsections = []

    for i, text_block in enumerate(text_blocks):
        add_text_block(text_block, subsections)
        if i < len(code_blocks):
            add_code_block(code_blocks[i], subsections)

    return subsections

################################################################

def split_page_into_subsections(page_md):
    page_sections = split_page_into_sections(page_md)
    page_subsections = {}

    for key, section in list(page_sections.items()):
        section = page_sections[key]
        page_subsections[key] = split_section_into_subsections(section)
    
    return page_subsections

################################################################
