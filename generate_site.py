#!/usr/bin/env python3
"""
generate_site.py

This script loads a reorganized data.yaml file that has three top-level sections:
  - website_and_cv: Data common to both the website and the CV.
  - web_only: Content to be included only on the website.
  - cv_only: Content to be included only on the CV.

It then renders two Jinja2 templates:
  - index.html.jinja for the website.
  - cv.html.jinja for the CV.

It also generates a PDF version of the CV using wkhtmltopdf.
Ensure you have installed the required packages:
  pip install pyyaml jinja2 pdfkit

Also, ensure that wkhtmltopdf is installed on your system and is available in your PATH.
"""

import os
import argparse
import shutil
from copy import deepcopy

import markdown
import pdfkit
import yaml
from jinja2 import Environment, FileSystemLoader

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif")


def load_data(yaml_file):
    """Load the YAML file."""
    with open(yaml_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def render_template(template_name, context, templates_dir="templates"):
    """Render a Jinja2 template with the provided context."""
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    return template.render(context)


def save_output(content, output_path):
    """Write content to the output file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {output_path}")


def copy_static_files(static_dir, output_dir):
    """Copy static files to output directory."""
    if os.path.exists(static_dir):
        output_static_dir = os.path.join(output_dir, "static")
        if os.path.exists(output_static_dir):
            shutil.rmtree(output_static_dir)
        shutil.copytree(static_dir, output_static_dir)
        print(f"Copied static files from {static_dir} to {output_static_dir}")
    else:
        print(f"Static directory {static_dir} does not exist, skipping...")


def generate_pdf_from_html(html_file, pdf_file):
    """Generate a PDF from an HTML file using wkhtmltopdf via pdfkit."""
    pdfkit.from_file(html_file, pdf_file)
    print(f"Generated PDF: {pdf_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a static website (index.html) and a CV (cv.html and cv.pdf) from a unified data.yaml file."
    )
    parser.add_argument(
        "--yaml", default="content/website.yaml", help="Path to the YAML data file (default: data.yaml)"
    )
    parser.add_argument(
        "--templates-dir", default="templates", help="Directory containing Jinja2 templates (default: templates)"
    )
    parser.add_argument(
        "--blog-folder", default="content/blog", help="Folder containing blog post templates (default: content/blog)"
    )
    parser.add_argument("--build-site", action="store_true", help="Render the static website")
    # parser.add_argument("--build-cv", action="store_true", help="Render the CV HTML (cv.html)")
    # parser.add_argument("--build-pdf", action="store_true", help="Generate a PDF of the CV using wkhtmltopdf")
    parser.add_argument("--output", default="output", help="Output directory for generated files (default: output)")
    args = parser.parse_args()

    data = load_data(args.yaml)

    # Extract the three sections from the YAML.
    common = data.get("website_and_cv", {})
    web_extra = data.get("web_only", {})
    cv_extra = data.get("cv_only", {})

    # Build the context dictionaries.
    # Now we include the key "website_and_cv" in the context so that the templates can reference it.
    website_data = {"website_and_cv": common, "web_only": web_extra}
    cv_data = {"website_and_cv": common, "cv_only": cv_extra}

    os.makedirs(args.output, exist_ok=True)

    # Copy static files to output directory
    # copy_static_files("static", args.output)

    # Render the website template.
    if args.build_site:
        home_page_data = deepcopy(website_data)
        # home_page_data["website_and_cv"][
        #     "profile_image_url"
        # ] = f"../{home_page_data['website_and_cv']['profile_image_url']}"
        site_html = render_template("index.html.jinja", home_page_data, templates_dir=args.templates_dir)
        site_output_path = os.path.join(args.output, "index.html")
        save_output(site_html, site_output_path)

        blog_common_data = deepcopy(common)
        blog_common_data["profile_image_url"] = f"../{blog_common_data['profile_image_url']}"
        for post in web_extra.get("blog_posts", []):
            source_folder = post["source"]
            source_folder_full = os.path.join(args.blog_folder, source_folder)
            output_folder = os.path.join(args.output, source_folder)
            os.makedirs(output_folder, exist_ok=True)

            # Copy images from the blog post source folder to the output folder
            for file in os.listdir(source_folder_full):
                if os.path.splitext(file)[1] in IMAGE_EXTENSIONS:
                    source_image_path = os.path.join(source_folder_full, file)
                    output_image_path = os.path.join(output_folder, file)
                    shutil.copy2(source_image_path, output_image_path)

            # read html content from the post
            post_file = os.path.join(args.blog_folder, source_folder, "index.html")
            with open(post_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            # html_content = markdown.markdown(post_content)

            source_output_path = os.path.join(args.output, source_folder, "index.html")
            source_html = render_template(
                "blog.html.jinja",
                {"website_and_cv": blog_common_data, "post": post, "content": html_content},
                templates_dir=args.templates_dir,
            )
            save_output(source_html, source_output_path)

    # Render the CV template.
    # if args.build_cv:
    #     cv_html = render_template("cv.html.jinja", cv_data)
    #     cv_output_path = os.path.join(args.output, "cv.html")
    #     save_output(cv_html, cv_output_path)

    #     if args.build_pdf:
    #         pdf_output_path = os.path.join(args.output, "cv.pdf")
    #         generate_pdf_from_html(cv_output_path, pdf_output_path)

    copy_static_files("static", args.output)


if __name__ == "__main__":
    main()
