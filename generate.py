# generate site from static pages, loosely inspired by Jekyll
# run like this:
#   ./generate.py test/source output
# the generated `output` should be the same as `test/expected_output`

import os
import argparse
import logging
import json
import re

from jinja2 import Environment, FileSystemLoader, TemplateError, TemplateNotFound


log = logging.getLogger(__name__)


def list_files(folder_path):
    for name in os.listdir(folder_path):
        base, ext = os.path.splitext(name)
        if ext != ".rst":
            continue
        yield os.path.join(folder_path, name)

def read_file(file_path):
    with open(file_path, 'rb') as f:
        raw_metadata = ""
        for line in f:
            if line.strip() == '---':
                break
            raw_metadata += line
        content = ""
        for line in f:
            content += line
    return json.loads(raw_metadata), content

def write_output(path, html):
    # Prepare output: only allow max 2 consecutive new lines and strip any
    # trailing white space.
    # Note: Must add a newline after stripping.
    output = re.sub("\n\n(\n+)", "\n\n", html).rstrip() + "\n"

    with open(path, "w") as f:
        f.write(output)

def generate_site(input_path, output_path):
    log.info("Generating site from %r", input_path)
    jinja_env = Environment(loader=FileSystemLoader(
        os.path.join(input_path, "layout")))

    for file_path in list_files(input_path):
        metadata, content = read_file(file_path)

        try:
            template_name = metadata["layout"]
        except KeyError:
            log.error("Template doesn't contain layout")
            log.error("Parsing %s", file_path)
            continue

        try:
            template = jinja_env.get_template(template_name)
        except TemplateNotFound:
            log.error("Template not found")
            log.error("Parsing %s", template_name)
            continue

        name = os.path.splitext(os.path.basename(file_path))[0] + ".html"
        path = os.path.join(output_path, name)

        data = dict(metadata, content=content)

        try:
            html = template.render(**data)
        except TemplateError:
            log.error("There was an error in parsing template %s", template_name)
            log.error("Passed data was %s", str(data))
            continue

        log.info("Writing %s with template %s", name, template_name)
        write_output(path, html)


def main():
    parser = argparse.ArgumentParser(description="Generate site from static pages")
    parser.add_argument("input_path", metavar="input_path", type=str,
                           help="Input file")
    parser.add_argument("output_path", metavar="output_path", type=str,
                           help="Output file")

    args = parser.parse_args()

    if not os.path.isdir(args.output_path):
        os.mkdir(args.output_path)

    generate_site(args.input_path, args.output_path)


if __name__ == "__main__":
    logging.basicConfig()
    main()

