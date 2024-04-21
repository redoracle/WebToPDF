"""
WebToPDF Crawler

Author: Redoracle
License: MIT

This script performs a web crawling operation starting from a given URL, extracting content from the crawled pages,
including text and the first encountered image. It handles images in various formats, with special handling for SVG images
which are converted to JPEG format for inclusion in a PDF document. The script is designed to recursively crawl internal
links up to a specified depth, ensuring it only processes pages within the given website domain.

Key Functionalities:
- Web Crawling: Starts from a user-provided URL and crawls internal links up to a specified depth. It uses a breadth-first
  search strategy to explore the website structure, gathering URLs to process.
  
- Content Extraction: For each page visited during the crawl, the script extracts textual content and the first image.
  Textual content is stripped of HTML tags to gather clean text. If an image is found, it attempts to download it.
  
- Image Handling: Handles different image formats encountered during content extraction. Specifically, for SVG images,
  it converts them to PNG using 'cairosvg', then further to JPEG for compatibility. Other images are directly converted to
  JPEG if not already in that format. Color inversion issues in images are corrected using PIL's ImageOps.
  
- PDF Generation: Aggregates the extracted content into a PDF document. Each page's content from the crawl results in a
  section within the PDF, including the text and the processed image. The script uses 'FPDF' for PDF generation, formatting
  the content and embedding images appropriately.
  
- Argument Parsing: Allows the user to specify the starting URL for the crawl operation via command line arguments. This
  enables flexibility and ease of use for different websites.

Requirements:
- External libraries including 'requests' for HTTP requests, 'BeautifulSoup' for HTML parsing, 'FPDF' for PDF generation,
  'PIL' (Pillow) for image processing, and 'cairosvg' for SVG to PNG conversion.
- The script expects a 'fonts' directory containing 'DejaVuSansCondensed.ttf' and 'DejaVuSansCondensed-Bold.ttf' for PDF
  text rendering.

Usage:
The script is intended to be run from the command line, with the starting URL as a required argument. It performs the
crawling, content extraction, and PDF generation operations automatically, outputting a PDF document with the aggregated
content from the crawled website.

Example command line usage:
    python WebToPDF-Crawler.py https://cardano-community.github.io/guild-operators/docker/docker/

This starts the crawling process at 'https://cardano-community.github.io/guild-operators/docker/docker/', processing internal links and generating a PDF
with the extracted content.

Notes:
- The script includes error handling for network requests and image processing, logging issues as they occur to aid in
  troubleshooting.
- Depth of the crawl and specific behaviors related to image processing and PDF generation can be adjusted within the
  script's parameters and functions.

TODOs:
- Performance Improvements
Implement Asynchronous Requests: Utilize aiohttp or similar libraries to make asynchronous HTTP requests to speed up the crawling process, especially useful for deep crawls or sites with many internal links.
Optimize Image Processing: Explore ways to optimize image conversion and color correction operations, potentially by reducing image sizes or parallelizing operations where possible.

- Feature Enhancements
Enhanced PDF Formatting: Improve the PDF output with better formatting options, such as handling headers and footers, page numbers, and dynamic content placement.
Configurable Depth and Scope: Allow users to specify the crawl depth and whether to include external links via command-line arguments or a configuration file.
Content Filtering: Implement filters or selectors to include/exclude specific types of content based on user preferences, such as text only, specific image types, or sections of a webpage.

- Usability and Robustness
User-Friendly Error Handling: Improve error messages and handling to make them more user-friendly, helping users diagnose and fix issues more easily.
Logging and Reporting: Enhance logging capabilities to include more detailed crawl reports, such as the number of pages crawled, images processed, and any errors or warnings encountered.
Interactive Mode: Develop an interactive mode that allows users to make decisions at runtime, such as choosing which links to follow or content to download.

-Scalability and Architecture
Modular Design: Refactor the script into a more modular architecture, separating concerns such as crawling, content extraction, and PDF generation into distinct components or classes.
Crawl Management: Implement features for managing and pausing/resuming crawls, which could include saving crawl state to disk.

- Security and Compliance
Respect Robots.txt: Ensure the crawler respects robots.txt policies of websites to avoid crawling disallowed paths.
User-Agent Customization: Allow customization of the HTTP User-Agent string to identify the crawler properly and avoid being blocked by websites.

- Additional Features
Command-Line Interface (CLI) Enhancements: Expand the CLI with more options for configuration, including setting output directories, choosing image formats, or verbose logging levels.
Support for More Content Types: Extend support for additional content types such as videos, embedded content, or dynamic AJAX-loaded content.
Integration with Web APIs: For sites that offer it, consider using official APIs to fetch content more efficiently than scraping HTML.

- Testing and Documentation
Comprehensive Unit Testing: Develop a suite of unit tests covering all major functionalities to ensure reliability and ease future development.
Documentation: Provide detailed documentation on how to install, configure, and use the script, including examples and troubleshooting tips.
"""

import argparse 
import sys
import os
import requests
from bs4 import BeautifulSoup
import logging
from fpdf import FPDF
import tempfile
from PIL import Image, ImageOps
import cairosvg
from urllib.parse import urlparse, urljoin

# Set up basic logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def is_internal_link(url, base_url):
    return url.startswith(base_url) or url.startswith('/')

def convert_svg_to_png(svg_path):
    png_path = svg_path.rsplit('.', 1)[0] + '.png'
    cairosvg.svg2png(url=svg_path, write_to=png_path)
    return png_path

def convert_svg_to_jpeg(svg_path):
    jpeg_path = svg_path.rsplit('.', 1)[0] + '.jpg'
    # Directly convert SVG to JPEG
    cairosvg.svg2png(url=svg_path, write_to=jpeg_path, output_width=2000, output_height=2000)
    return jpeg_path

def correct_color(image_path):
    """Attempt to correct color inversion in an image."""
    with Image.open(image_path) as img:
        converted_img = ImageOps.invert(img)
        converted_img.save(image_path)

def convert_to_jpeg(img_path):
    """Converts an image to JPEG format, handling SVG files and attempting color correction."""
    try:
        if img_path.endswith('.svg'):
            img_path = convert_svg_to_jpeg(img_path)

        with Image.open(img_path) as img:
            if img.format == 'JPEG':
                correct_color(img_path)  # Attempt color correction on JPEG images directly
                return img_path

            # Convert to JPEG if not already
            jpeg_path = img_path.rsplit('.', 1)[0] + '.jpg'
            img.convert('RGB').save(jpeg_path, 'JPEG')
            os.unlink(img_path)  # Remove the original file

            correct_color(jpeg_path)  # Attempt color correction after conversion
            return jpeg_path
    except Exception as e:
        logging.error(f"Error converting image: {e}")
        return None


class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_url = ''
        font_path = './fonts/'  # Adjust based on your font files location
        self.add_font('DejaVu', '', font_path + 'DejaVuSansCondensed.ttf', uni=True)
        self.add_font('DejaVu', 'B', font_path + 'DejaVuSansCondensed-Bold.ttf', uni=True)

    def header(self):
        last_part = self.current_url.split('/')[-1] if self.current_url.split('/')[-1] else self.current_url
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, last_part, 0, 1, 'C')

    def chapter_body(self, body):
        self.set_font('DejaVu', '', 10)
        self.multi_cell(0, 10, body, align='L')
        self.ln()

def sanitize_text(text):
    """Remove characters not supported by Latin-1 encoding."""
    return text.encode('latin-1', 'ignore').decode('latin-1')

def fetch_content_and_images(url):
    """Fetch the content of the page and download the first image."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        text_elements = soup.stripped_strings
        sanitized_text = ' '.join(sanitize_text(text) for text in text_elements)
        
        
        img_url = soup.find('img')['src'] if soup.find('img') else None
        img_path = None
        if img_url:
            img_url = urljoin(url, img_url)
            img_response = requests.get(img_url, stream=True)
            if img_response.status_code == 200:
                suffix = '.jpg' if img_url.endswith('.svg') else '.jpg'
                f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                f.write(img_response.content)
                f.close()
                if img_url.endswith('.svg'):
                    png_path = f.name.rsplit('.', 1)[0] + '.png'
                    cairosvg.svg2png(url=f.name, write_to=png_path)
                    os.unlink(f.name)
                    img_path = convert_to_jpeg(png_path)
                else:
                    img_path = convert_to_jpeg(f.name)

        return sanitized_text, img_path
    except Exception as e:
        logging.error(f"Error fetching content from {url}: {e}")
        return "", None

# Simplified function to add content to the PDF, including hyperlinks
def add_content_with_links(pdf, content):
    for line in content.split('\n'):
        if line.startswith('http'):
            # Assuming 'line' is a URL, make it clickable
            pdf.set_text_color(0, 0, 255)  # Optional: set link color to blue
            pdf.set_font('Arial', 'U', 12)
            pdf.write(10, line, line)  # The link text and the URL are the same in this simple case
            pdf.ln(10)  # Move to the next line
        else:
            # Regular text
            pdf.set_text_color(0, 0, 0)  # Reset text color to black
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, line)
            pdf.ln(10)  # Ensure there's a gap to the next line of text or link

# Example usage in create_pdf function
def create_pdf(links):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=5)
    for url in links:
        content, img_path = fetch_content_and_images(url)  # Assume this function is adapted to return plain text content
        if img_path:
            jpeg_img_path = convert_to_jpeg(img_path)
            if jpeg_img_path:
                pdf.image(jpeg_img_path, x=10, w=100)
                os.unlink(jpeg_img_path)
        add_content_with_links(pdf, content)  # Use the new function to add content with links
    pdf.output('web_content.pdf')


def fetch_links(url, visited, base_url, depth=0, max_depth=3):
    """Fetch and return internal links from the given URL."""
    if depth > max_depth or url in visited:
        return set()
    visited.add(url)
    logging.debug(f"Fetching links from {url} at depth {depth}")
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Use urljoin to correctly handle relative and absolute URLs
            full_url = urljoin(url, href)
            # Check if the link is internal by comparing its base URL
            if full_url.startswith(base_url) and full_url not in visited:
                links.add(full_url)
        logging.info(f"Found {len(links)} internal links on {url}")
        return links
    except Exception as e:
        logging.error(f"Error fetching links from {url}: {e}")
        return set()

def scrape_links(start_url, base_url, max_depth=3):
    visited = set()
    to_visit = {start_url}
    while to_visit:
        current_url = to_visit.pop()
        if current_url not in visited:
            links = fetch_links(current_url, visited, base_url, depth=0, max_depth=max_depth)
            visited.add(current_url)
            to_visit.update(links)
    return visited


if __name__ == "__main__":
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Crawl a website and create a PDF with its content.",
                                     usage="%(prog)s [options] start_url",
                                     epilog="Example: python %(prog)s https://cardano-community.github.io/guild-operators/docker/docker/")
    
    # Add the start_url argument as a required positional argument
    parser.add_argument("start_url", help="The initial URL to start crawling from. This argument is required.")

    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Extract base_url from start_url
    parsed_url = urlparse(args.start_url)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc

    # Check if the start_url is provided, though argparse will automatically check this for us
    if not args.start_url:
        parser.print_help()  # Display the help message
        sys.exit(1)  # Exit the script with an error status

    # Proceed with the script using args.start_url as the initial URL
    start_url = args.start_url
    logging.info(f"Starting to scrape links from {start_url}")

    # Now, pass base_url to functions that require it, for example:
    internal_links = scrape_links(start_url, base_url)
    logging.info(f"Scraped {len(internal_links)} unique internal links.")
    create_pdf(internal_links)
