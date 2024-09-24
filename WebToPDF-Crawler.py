"""
WebToPDF Crawler

Author: Redoracle (Improved by ChatGPT)
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
- External libraries including 'aiohttp' and 'asyncio' for asynchronous HTTP requests, 'BeautifulSoup' for HTML parsing,
  'FPDF' for PDF generation, 'Pillow' for image processing, 'cairosvg' for SVG to PNG conversion, 'selenium' for handling dynamic content,
  and 'urllib.robotparser' for parsing robots.txt.
- The script expects a 'fonts' directory containing 'DejaVuSansCondensed.ttf' and 'DejaVuSansCondensed-Bold.ttf' for PDF
  text rendering.

Usage:
The script is intended to be run from the command line, with the starting URL as a required argument. It performs the
crawling, content extraction, and PDF generation operations automatically, outputting a PDF document with the aggregated
content from the crawled website.

Example command line usage:
    python WebToPDF-Crawler.py https://cardano-community.github.io/guild-operators/docker/docker/ -d 2 -o output.pdf -f ./fonts/ -v

This starts the crawling process at 'https://cardano-community.github.io/guild-operators/docker/docker/', processing internal links up to depth 2, and generating a PDF named 'output.pdf' with verbose logging.
"""

import argparse
import sys
import os
import aiohttp
import asyncio
import logging
from bs4 import BeautifulSoup
from fpdf import FPDF
from PIL import Image, ImageOps
import cairosvg
from urllib.parse import urlparse, urljoin
import tempfile
import mimetypes
import shutil
import time
import re
import urllib.robotparser as robotparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

# Constants
DEFAULT_MAX_DEPTH = 3
DEFAULT_OUTPUT = 'web_content.pdf'
DEFAULT_FONT_DIR = './fonts/'
DEFAULT_USER_AGENT = 'WebToPDF-Crawler/1.0 (+https://github.com/your-repo)'
STATE_FILE = 'crawl_state.json'

# Configure logging
logger = logging.getLogger('WebToPDF-Crawler')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class RobotsHandler:
    """Handles robots.txt parsing and compliance."""
    def __init__(self, base_url):
        self.base_url = base_url
        self.parser = robotparser.RobotFileParser()
        self._fetch_robots()

    def _fetch_robots(self):
        """Fetch and parse robots.txt."""
        robots_url = urljoin(self.base_url, '/robots.txt')
        self.parser.set_url(robots_url)
        try:
            self.parser.read()
            logger.info(f"Robots.txt fetched from {robots_url}")
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt from {robots_url}: {e}")

    def can_fetch(self, url):
        """Check if the URL can be fetched based on robots.txt."""
        return self.parser.can_fetch(DEFAULT_USER_AGENT, url)

class ImageProcessor:
    """Handles image downloading and processing."""
    @staticmethod
    async def download_image(session, img_url):
        """Download an image and return its local path."""
        try:
            async with session.get(img_url) as response:
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '')
                extension = mimetypes.guess_extension(content_type.split(';')[0])
                if not extension:
                    extension = os.path.splitext(urlparse(img_url).path)[1] or '.jpg'
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(await response.read())
                    tmp_path = tmp_file.name
            logger.debug(f"Image downloaded: {img_url} to {tmp_path}")
            return tmp_path
        except Exception as e:
            logger.error(f"Failed to download image {img_url}: {e}")
            return None

    @staticmethod
    def convert_svg_to_jpeg(svg_path):
        """Convert SVG to JPEG using cairosvg and PIL."""
        try:
            png_path = svg_path.rsplit('.', 1)[0] + '.png'
            jpeg_path = svg_path.rsplit('.', 1)[0] + '.jpg'
            cairosvg.svg2png(url=svg_path, write_to=png_path)
            with Image.open(png_path) as img:
                img = img.convert('RGB')
                img.save(jpeg_path, 'JPEG')
            os.remove(svg_path)
            os.remove(png_path)
            logger.debug(f"SVG converted to JPEG: {jpeg_path}")
            return jpeg_path
        except Exception as e:
            logger.error(f"Error converting SVG to JPEG for {svg_path}: {e}")
            return None

    @staticmethod
    def correct_color(image_path):
        """Attempt to correct color inversion in an image."""
        try:
            with Image.open(image_path) as img:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                converted_img = ImageOps.invert(img)
                converted_img.save(image_path)
            logger.debug(f"Color corrected for image: {image_path}")
        except Exception as e:
            logger.error(f"Error correcting color for {image_path}: {e}")

    @staticmethod
    def convert_to_jpeg(img_path):
        """Converts an image to JPEG format, handling SVG files and attempting color correction."""
        try:
            if img_path.lower().endswith('.svg'):
                jpeg_path = ImageProcessor.convert_svg_to_jpeg(img_path)
                if jpeg_path:
                    ImageProcessor.correct_color(jpeg_path)
                    return jpeg_path
                else:
                    return None

            with Image.open(img_path) as img:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                jpeg_path = img_path.rsplit('.', 1)[0] + '.jpg'
                img.save(jpeg_path, 'JPEG')
            os.remove(img_path)
            ImageProcessor.correct_color(jpeg_path)
            logger.debug(f"Image converted to JPEG: {jpeg_path}")
            return jpeg_path
        except Exception as e:
            logger.error(f"Error converting image to JPEG for {img_path}: {e}")
            return None

class PDFGenerator(FPDF):
    """Handles PDF creation and formatting."""
    def __init__(self, font_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_url = ''
        self.font_dir = font_dir
        self.add_fonts()

    def add_fonts(self):
        """Add custom fonts to the PDF."""
        try:
            self.add_font('DejaVu', '', os.path.join(self.font_dir, 'DejaVuSansCondensed.ttf'), uni=True)
            self.add_font('DejaVu', 'B', os.path.join(self.font_dir, 'DejaVuSansCondensed-Bold.ttf'), uni=True)
            logger.debug("Custom fonts added to PDF.")
        except Exception as e:
            logger.error(f"Error adding fonts: {e}")
            self.set_font('Arial', '', 12)  # Fallback to default font

    def header(self):
        """Create a header for each page."""
        if self.current_url:
            last_part = self.current_url.rstrip('/').split('/')[-1] or self.current_url
            self.set_font('DejaVu', 'B', 12)
            self.cell(0, 10, last_part, 0, 1, 'C')

    def footer(self):
        """Create a footer with page numbers."""
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_content(self, text, image_path=None):
        """Add text and image to the PDF."""
        self.set_font('DejaVu', '', 10)
        self.multi_cell(0, 10, text, align='L')
        self.ln()

        if image_path:
            try:
                # Resize image if it's too large
                max_width = self.w - 20
                with Image.open(image_path) as img:
                    width, height = img.size
                    if width > max_width:
                        ratio = max_width / float(width)
                        height = int(float(height) * ratio)
                        img = img.resize((int(max_width), height), Image.ANTIALIAS)
                        img.save(image_path)

                self.image(image_path, x=10, w=max_width)
                self.ln()
                logger.debug(f"Image added to PDF: {image_path}")
            except Exception as e:
                logger.error(f"Error adding image {image_path} to PDF: {e}")

class CrawlStateManager:
    """Manages crawl state for pause and resume functionality."""
    def __init__(self, state_file=STATE_FILE):
        self.state_file = state_file

    def save_state(self, visited, queue):
        """Save the current crawl state to a file."""
        state = {
            'visited': list(visited),
            'queue': list(queue._queue)
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
        logger.info(f"Crawl state saved to {self.state_file}")

    def load_state(self):
        """Load the crawl state from a file."""
        if not os.path.exists(self.state_file):
            return set(), asyncio.Queue()
        with open(self.state_file, 'r') as f:
            state = json.load(f)
        visited = set(state.get('visited', []))
        queue = asyncio.Queue()
        for item in state.get('queue', []):
            queue.put_nowait(tuple(item))
        logger.info(f"Crawl state loaded from {self.state_file}")
        return visited, queue

class WebToPDFCrawler:
    """Main crawler class handling the crawling and PDF generation."""
    def __init__(self, start_url, base_url, max_depth, output, font_dir, include_external, content_filter, interactive, support_dynamic):
        self.start_url = start_url
        self.base_url = base_url
        self.max_depth = max_depth
        self.output = output
        self.font_dir = font_dir
        self.include_external = include_external
        self.content_filter = content_filter
        self.interactive = interactive
        self.support_dynamic = support_dynamic

        self.parsed_base = urlparse(self.base_url)
        self.base_netloc = self.parsed_base.netloc
        self.robots_handler = RobotsHandler(self.base_url)
        self.state_manager = CrawlStateManager()

        self.pdf = PDFGenerator(font_dir=self.font_dir)
        self.pdf.set_auto_page_break(auto=True, margin=15)

        self.visited, self.queue = self.state_manager.load_state()

        # Initialize Selenium WebDriver if dynamic content support is enabled
        self.driver = None
        if self.support_dynamic:
            self._init_selenium()

    def _init_selenium(self):
        """Initialize Selenium WebDriver for dynamic content."""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium WebDriver initialized for dynamic content support.")
        except Exception as e:
            logger.error(f"Error initializing Selenium WebDriver: {e}")
            self.driver = None

    async def fetch_content(self, session, url):
        """Fetch page content and return sanitized text and first image URL."""
        try:
            if self.support_dynamic and self.driver:
                self.driver.get(url)
                await asyncio.sleep(2)  # Wait for dynamic content to load
                content = self.driver.page_source
            else:
                async with session.get(url) as response:
                    response.raise_for_status()
                    content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')

            # Apply content filtering
            if self.content_filter.get('text_only'):
                for script in soup(["script", "style"]):
                    script.extract()
                text = soup.get_text(separator=' ', strip=True)
            else:
                text_elements = soup.stripped_strings
                text = ' '.join(self._sanitize_text(text) for text in text_elements)

            # Extract first image based on filter
            img_tag = soup.find('img')
            img_url = img_tag['src'] if img_tag and img_tag.get('src') else None
            if self.content_filter.get('specific_image_types') and img_tag:
                img_type = img_tag.get('type') or img_tag.get('alt')
                if img_type and img_type not in self.content_filter['specific_image_types']:
                    img_url = None

            return text, img_url
        except Exception as e:
            logger.error(f"Error processing content from {url}: {e}")
            return "", None

    def _sanitize_text(self, text):
        """Remove characters not supported by Latin-1 encoding."""
        return text.encode('latin-1', 'ignore').decode('latin-1')

    async def download_and_process_image(self, session, img_url):
        """Download and process an image, returning the local path."""
        img_path = await ImageProcessor.download_image(session, img_url)
        if img_path:
            jpeg_img_path = ImageProcessor.convert_to_jpeg(img_path)
            return jpeg_img_path
        return None

    async def process_url(self, session, url, semaphore):
        """Process a single URL: fetch content, download image, and add to PDF."""
        async with semaphore:
            if not self.robots_handler.can_fetch(url):
                logger.info(f"Disallowed by robots.txt: {url}")
                return

            logger.info(f"Processing {url}")
            text, img_url = await self.fetch_content(session, url)
            if not text:
                logger.info(f"No text content found for {url}")
                return

            image_path = None
            if img_url:
                image_path = await self.download_and_process_image(session, img_url)
                if not image_path:
                    logger.info(f"Image processing failed for {img_url}")

            self.pdf.current_url = url
            self.pdf.add_page()
            self.pdf.add_content(text, image_path)

            if image_path and os.path.exists(image_path):
                os.remove(image_path)

            # Save state after processing each URL
            self.state_manager.save_state(self.visited, self.queue)

    async def fetch_links(self, session, url, semaphore):
        """Fetch and enqueue internal links from the given URL."""
        async with semaphore:
            try:
                if self.support_dynamic and self.driver:
                    self.driver.get(url)
                    await asyncio.sleep(2)  # Wait for dynamic content to load
                    content = self.driver.page_source
                else:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    full_url = urljoin(url, href)
                    parsed_url = urlparse(full_url)
                    normalized_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
                    if self.include_external:
                        is_internal = True
                    else:
                        is_internal = (parsed_url.netloc == self.base_netloc) or (parsed_url.netloc == '')
                    if is_internal and normalized_url not in self.visited:
                        if self.interactive:
                            user_choice = self._prompt_user(full_url)
                            if not user_choice:
                                continue
                        await self.queue.put((normalized_url, self.current_depth + 1))
            except Exception as e:
                logger.error(f"Error fetching links from {url}: {e}")

    def _prompt_user(self, url):
        """Prompt user to decide whether to crawl the URL."""
        while True:
            choice = input(f"Do you want to crawl the following URL? [y/n]: {url}\n(y/n): ").lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    async def crawl(self):
        """Main crawling coroutine."""
        semaphore = asyncio.Semaphore(10)  # Limit concurrent connections
        async with aiohttp.ClientSession(headers={'User-Agent': DEFAULT_USER_AGENT}) as session:
            while not self.queue.empty():
                current_url, depth = await self.queue.get()
                if current_url in self.visited or depth > self.max_depth:
                    continue
                self.visited.add(current_url)
                self.current_depth = depth
                await self.process_url(session, current_url, semaphore)

                # Fetch and enqueue links if within depth
                if depth < self.max_depth:
                    await self.fetch_links(session, current_url, semaphore)

    def save_pdf(self):
        """Save the generated PDF to the specified output file."""
        try:
            self.pdf.output(self.output)
            logger.info(f"PDF generated successfully: {self.output}")
        except Exception as e:
            logger.error(f"Failed to save PDF: {e}")

    def close(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            logger.debug("Selenium WebDriver closed.")

    def run(self):
        """Run the crawler."""
        try:
            asyncio.run(self.crawl())
            self.save_pdf()
        except KeyboardInterrupt:
            logger.warning("Crawl interrupted by user.")
            self.state_manager.save_state(self.visited, self.queue)
        finally:
            self.close()

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Crawl a website and create a PDF with its content.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("start_url", help="The initial URL to start crawling from.")
    parser.add_argument("-d", "--depth", type=int, default=DEFAULT_MAX_DEPTH, help="Maximum crawl depth.")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help="Output PDF file name.")
    parser.add_argument("-f", "--fonts", default=DEFAULT_FONT_DIR, help="Directory containing font files.")
    parser.add_argument("-e", "--external", action='store_true', help="Include external links in the crawl.")
    parser.add_argument("-v", "--verbose", action='store_true', help="Enable verbose logging.")
    parser.add_argument("-c", "--content-filter", type=str, default='{}',
                        help="JSON string to filter content. Example: '{\"text_only\": true, \"specific_image_types\": [\"png\", \"jpg\"]}'")
    parser.add_argument("-i", "--interactive", action='store_true', help="Enable interactive mode to choose links.")
    parser.add_argument("-s", "--support-dynamic", action='store_true', help="Support dynamic content using Selenium.")
    return parser.parse_args()

def validate_fonts(font_dir):
    """Ensure required font files are present."""
    required_fonts = ['DejaVuSansCondensed.ttf', 'DejaVuSansCondensed-Bold.ttf']
    for font in required_fonts:
        if not os.path.isfile(os.path.join(font_dir, font)):
            logger.error(f"Missing font file: {font} in {font_dir}")
            sys.exit(1)
    logger.debug("All required font files are present.")

def main():
    args = parse_arguments()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate fonts
    validate_fonts(args.fonts)

    # Normalize start_url
    start_url = args.start_url if args.start_url.endswith('/') else args.start_url + '/'

    # Extract base_url
    parsed_url = urlparse(start_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"

    # Parse content filter
    try:
        content_filter = json.loads(args.content_filter)
    except json.JSONDecodeError:
        logger.error("Invalid JSON for content filter.")
        sys.exit(1)

    # Initialize crawler
    crawler = WebToPDFCrawler(
        start_url=start_url,
        base_url=base_url,
        max_depth=args.depth,
        output=args.output,
        font_dir=args.fonts,
        include_external=args.external,
        content_filter=content_filter,
        interactive=args.interactive,
        support_dynamic=args.support_dynamic
    )

    logger.info(f"Starting crawl at: {start_url} with max depth {args.depth}")
    start_time = time.time()
    crawler.run()
    end_time = time.time()
    logger.info(f"Crawling completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
