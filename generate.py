"""
Generate site from static pages, loosely inspired by Jekyll.

Run like this:
  ./generate.py test/source output
"""

import os
import argparse
import logging
import json
import re

import jinja2


log = logging.getLogger(__name__)


def list_files(folder_path):
    """A generator for all the .rst files in a given directory.

    Args:
        folder_path: The path to the directory.

    Yields:
        All the .rst files in the given directory.
    """
    for name in os.listdir(folder_path):
        ext = os.path.splitext(name)[1]
        if ext != ".rst":
            continue
        yield os.path.join(folder_path, name)

def read_file(file_path):
    """Read a jinja2 template file.

    Args:
        file_path: The path to the template file.

    Returns:
        metadata, content: 2 packed values representing the metadata and the
        actual content in the file.

    Excepts:
        ValueError: In case the metadata is not valid JSON.
    """
    with open(file_path, "r") as f:
        raw_metadata, content = f.read().split("---\n", 1)
        try:
            metadata = json.loads(raw_metadata)
        except ValueError:
            log.error("Metadata doesn't contain valid JSON")
            log.error("Parsing %s", file_path)
            raise

    return metadata, content

def write_output(path, html):
    """Write the parsed template to a file.

    Before writing the output, make sure that there can only be at most 2
    consecutive new lines and that there's no white space at the end of the
    output. Also, make sure the output ends with exactly one new line.

    Args:
        path: The path to the file.
        html: The output to be written to the file.
    """
    # Prepare output: only allow max 2 consecutive new lines and strip any
    # trailing white space.
    # Note: Must add a newline after stripping.
    output = re.sub("\n\n(\n+)", "\n\n", html).rstrip() + "\n"

    with open(path, "w") as f:
        f.write(output)

def generate_site(input_path, output_path):
    """Generate a static site from jinja2 templates.

    Args:
        input_path: The path to the templates. Must contain a layout folder.
        output_path: The path to the directory where the parsed templates will
        be generated. If it doesn't exist, it will be created.
    """
    log.info("Generating site from %r", input_path)
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(
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
        except jinja2.TemplateNotFound:
            log.error("Template not found")
            log.error("Parsing %s", template_name)
            continue
        except jinja2.TemplateSyntaxError:
            log.error("There was an error in parsing template %s", template_name)
            continue

        name = os.path.splitext(os.path.basename(file_path))[0] + ".html"
        path = os.path.join(output_path, name)

        data = dict(metadata, content=content)

        html = template.render(**data)

        log.info("Writing %s with template %s", name, template_name)
        write_output(path, html)


def main():
    """Main function.

    Accepts 2 command line arguments:
        input_path: The path to the directory containing the templates.
        output_path: The path to the directory where the parsed templates will
        be written. If it doesn't exist it's created.
    """
    parser = argparse.ArgumentParser(description="Generate site from static pages")
    parser.add_argument("input_path", metavar="input_path", type=str,
                           help="Input file")
    parser.add_argument("output_path", metavar="output_path", type=str,
                           help="Output file")

    args = parser.parse_args()

    # If the output dir doesn't exist create it.
    if not os.path.isdir(args.output_path):
        os.mkdir(args.output_path)

    generate_site(args.input_path, args.output_path)


if __name__ == "__main__":
    logging.basicConfig()
    main()

