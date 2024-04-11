# WebToPDF-Crawler

This script initiates a web crawling operation with a provided URL, extracting content from the crawled pages, including text and the first found image. It can handle photos in a variety of formats, including SVG images that are converted to JPEG format for use in a PDF document. The script is intended to recursively crawl internal links up to a predetermined depth, only processing pages within the specified website domain.

<div style="text-align: center;">
<img src="https://raw.githubusercontent.com/redoracle/DockerSnap/main/DockerSnap%20logo.webp" width="300" height="300">
</div>


## Key Functionalities:
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

## Requirements:
- External libraries including 'requests' for HTTP requests, 'BeautifulSoup' for HTML parsing, 'FPDF' for PDF generation,
  'PIL' (Pillow) for image processing, and 'cairosvg' for SVG to PNG conversion.
- The script expects a 'fonts' directory containing 'DejaVuSansCondensed.ttf' and 'DejaVuSansCondensed-Bold.ttf' for PDF
  text rendering.

## Usage:
The script is intended to be run from the command line, with the starting URL as a required argument. It performs the
crawling, content extraction, and PDF generation operations automatically, outputting a PDF document with the aggregated
content from the crawled website.

## Example command line usage:
    python WebToPDF-crawler.py https://docs.cardano.org/introduction

This starts the crawling process at 'https://docs.cardano.org/introduction', processing internal links and generating a PDF
with the extracted content.

## Notes:
- The script includes error handling for network requests and image processing, logging issues as they occur to aid in
  troubleshooting.
- Depth of the crawl and specific behaviors related to image processing and PDF generation can be adjusted within the
  script's parameters and functions.

## TODOs:
### - Performance Improvements
Implement Asynchronous Requests: Utilize aiohttp or similar libraries to make asynchronous HTTP requests to speed up the crawling process, especially useful for deep crawls or sites with many internal links.
Optimize Image Processing: Explore ways to optimize image conversion and color correction operations, potentially by reducing image sizes or parallelizing operations where possible.

### - Feature Enhancements
Enhanced PDF Formatting: Improve the PDF output with better formatting options, such as handling headers and footers, page numbers, and dynamic content placement.
Configurable Depth and Scope: Allow users to specify the crawl depth and whether to include external links via command-line arguments or a configuration file.
Content Filtering: Implement filters or selectors to include/exclude specific types of content based on user preferences, such as text only, specific image types, or sections of a webpage.

### - Usability and Robustness
User-Friendly Error Handling: Improve error messages and handling to make them more user-friendly, helping users diagnose and fix issues more easily.
Logging and Reporting: Enhance logging capabilities to include more detailed crawl reports, such as the number of pages crawled, images processed, and any errors or warnings encountered.
Interactive Mode: Develop an interactive mode that allows users to make decisions at runtime, such as choosing which links to follow or content to download.

### - Scalability and Architecture
Modular Design: Refactor the script into a more modular architecture, separating concerns such as crawling, content extraction, and PDF generation into distinct components or classes.
Crawl Management: Implement features for managing and pausing/resuming crawls, which could include saving crawl state to disk.

### - Security and Compliance
Respect Robots.txt: Ensure the crawler respects robots.txt policies of websites to avoid crawling disallowed paths.
User-Agent Customization: Allow customization of the HTTP User-Agent string to identify the crawler properly and avoid being blocked by websites.

### - Additional Features
Command-Line Interface (CLI) Enhancements: Expand the CLI with more options for configuration, including setting output directories, choosing image formats, or verbose logging levels.
Support for More Content Types: Extend support for additional content types such as videos, embedded content, or dynamic AJAX-loaded content.
Integration with Web APIs: For sites that offer it, consider using official APIs to fetch content more efficiently than scraping HTML.

### - Testing and Documentation
Comprehensive Unit Testing: Develop a suite of unit tests covering all major functionalities to ensure reliability and ease future development.
Documentation: Provide detailed documentation on how to install, configure, and use the script, including examples and troubleshooting tips.
