![GitHub Repo Stars](https://img.shields.io/github/stars/redoracle/WebToPDF.svg?style=social&label=Star)
![GitHub Forks](https://img.shields.io/github/forks/redoracle/WebToPDF.svg?style=social&label=Fork)
![GitHub Issues](https://img.shields.io/github/issues/redoracle/WebToPDF.svg)
![GitHub License](https://img.shields.io/github/license/redoracle/WebToPDF.svg)
![Docker Image Size](https://img.shields.io/docker/image-size/ghcr.io/redoracle/WebToPDF/latest)
![Docker Pulls](https://img.shields.io/docker/pulls/ghcr.io/redoracle/WebToPDF.svg)
![Build Status](https://github.com/redoracle/WebToPDF/actions/workflows/docker-image.yml/badge.svg)


# WebToPDF-Crawler

<div style="text-align: center;">
  <img src="https://raw.githubusercontent.com/redoracle/WebToPDF/refs/heads/main/WebToPDF%20Crawler%20Logo.webp" width="300" height="300">
</div>

## Overview

**WebToPDF-Crawler** is a versatile script designed to crawl websites starting from a specified URL, extract textual content and images from each crawled page, and compile the extracted data into a structured PDF document. The script supports various image formats, including SVG, which are converted to JPEG for seamless inclusion in the PDF. It is built with scalability, performance, and user flexibility in mind, incorporating features such as asynchronous requests, content filtering, interactive mode, and support for dynamic web content.

## Key Functionalities

- **Web Crawling**: Initiates crawling from a user-provided URL, exploring internal links up to a specified depth using a breadth-first search strategy. Optionally includes external links based on user preference.

- **Content Extraction**: For each visited page, extracts clean textual content and the first encountered image. Text is stripped of HTML tags to ensure readability.

- **Image Handling**: Supports various image formats. SVG images are converted to JPEG using `cairosvg` and `Pillow`. Other image formats are directly converted to JPEG if necessary. Color inversion issues are addressed using PIL's `ImageOps`.

- **PDF Generation**: Aggregates extracted content into a PDF document. Each crawled page contributes a section in the PDF, containing the text and the processed image. Utilizes `FPDF` for robust PDF creation, including dynamic headers, footers, and page numbering.

- **Asynchronous Operations**: Employs `aiohttp` and `asyncio` for asynchronous HTTP requests, significantly speeding up the crawling process, especially for websites with numerous internal links.

- **Dynamic Content Support**: Integrates `Selenium` to handle dynamic web content loaded via JavaScript, ensuring comprehensive content extraction from modern websites.

- **Content Filtering**: Allows users to specify filters to include or exclude certain types of content, such as text-only extraction or specific image types.

- **Interactive Mode**: Offers an interactive mode where users can choose which discovered links to follow during the crawling process, providing greater control over the crawl.

- **Crawl State Management**: Implements pause and resume functionality by saving the crawl state to disk, enabling users to manage long-running crawls efficiently.

- **Respect for `robots.txt`**: Parses and adheres to the `robots.txt` policies of websites to ensure ethical crawling practices.

- **User-Agent Customization**: Allows customization of the HTTP User-Agent string to identify the crawler appropriately and avoid being blocked by websites.

- **Command-Line Interface (CLI) Enhancements**: Provides a comprehensive CLI with options for setting crawl depth, output directories, image formats, verbose logging, and more.

## Requirements

### **Software Dependencies**

- **Python 3.12+**

### **Python Libraries**

All required Python libraries are managed using Conda. Below are the dependencies:

- [`aiohttp`](https://pypi.org/project/aiohttp/) - For asynchronous HTTP requests.
- [`asyncio`](https://docs.python.org/3/library/asyncio.html) - For managing asynchronous operations.
- [`BeautifulSoup4`](https://pypi.org/project/beautifulsoup4/) - For HTML parsing.
- [`FPDF`](https://pypi.org/project/fpdf/) - For PDF generation.
- [`Pillow`](https://pypi.org/project/Pillow/) - For image processing.
- [`cairosvg`](https://pypi.org/project/CairoSVG/) - For converting SVG images to PNG.
- [`Selenium`](https://pypi.org/project/selenium/) - For handling dynamic web content.
- [`urllib.robotparser`](https://docs.python.org/3/library/urllib.robotparser.html) - For parsing `robots.txt`.

### **Additional Requirements for Selenium**

- **WebDriver**: Selenium requires a WebDriver to interface with the chosen browser.
  - **ChromeDriver**: Download the [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) that matches your Chrome version and ensure it's in your system's PATH.

### **Font Files**

- A `fonts` directory containing:
  - `DejaVuSansCondensed.ttf`
  - `DejaVuSansCondensed-Bold.ttf`

These fonts are essential for proper text rendering in the generated PDF. You can download them from the [DejaVu Fonts](https://dejavu-fonts.github.io/) project.

## Installation

Follow these steps to set up the **WebToPDF-Crawler** environment using Conda:

### **1. Clone the Repository**

```bash
git clone https://github.com/redoracle/WebToPDF-Crawler.git
cd WebToPDF-Crawler
```

### **2. Create a New Conda Environment**

Creating a dedicated Conda environment ensures that your project dependencies are isolated, preventing conflicts with other projects.

```bash
# Create a new Conda environment named 'webtopdf' with Python version 3.12
conda create -n webtopdf python=3.12
```

### **3. Activate the Conda Environment**

Before installing any packages, activate the newly created environment:

```bash
# Activate the newly created 'webtopdf' environment
conda activate webtopdf
```

### **4. Add the `conda-forge` Channel**

The `conda-forge` channel hosts a vast collection of packages, ensuring you have access to the latest versions and dependencies.

```bash
# Add the 'conda-forge' channel to access a wider range of packages
conda config --add channels conda-forge

# Set the channel priority to 'strict' to prefer packages from higher-priority channels
conda config --set channel_priority strict
```

### **5. Install All Required Python Packages**

Install all necessary dependencies using Conda from the `conda-forge` channel:

```bash
# Install all required Python packages using Conda from the 'conda-forge' channel
conda install aiohttp beautifulsoup4 fpdf pillow cairosvg selenium cairo -c conda-forge
```

- **Explanation of Each Package:**
  - `aiohttp`: For asynchronous HTTP requests.
  - `beautifulsoup4`: For HTML parsing.
  - `fpdf`: For PDF generation.
  - `pillow`: For image processing.
  - `cairosvg`: For converting SVG images to PNG/JPEG.
  - `selenium`: For handling dynamic web content.
  - `cairo`: The underlying C library required by `cairosvg` for rendering graphics.

### **6. Verify Installation**

After installation, it's good practice to verify that all packages are correctly installed.

```bash
# List all installed packages in the current Conda environment to verify successful installation
conda list
```

- **Expected Output:**
  - A list of installed packages along with their versions. Ensure that all the required packages (`aiohttp`, `beautifulsoup4`, `fpdf`, `pillow`, `cairosvg`, `selenium`, `cairo`) are listed.

### **7. Set Up Selenium WebDriver**

Selenium requires a WebDriver to interact with web browsers. For Chrome, you'll need ChromeDriver.

#### **a. Download ChromeDriver**

1. **Check Your Chrome Version:**
   
   Open Chrome and navigate to `chrome://settings/help` to find out your Chrome version.

2. **Download the Matching ChromeDriver:**
   
   Visit the [ChromeDriver Downloads](https://sites.google.com/a/chromium.org/chromedriver/downloads) page and download the version that matches your Chrome browser.

#### **b. Install ChromeDriver**

Move the downloaded `chromedriver` to a directory that's in your system's PATH and make it executable.

```bash
# Example for Unix-based systems
mv /path/to/downloaded/chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
```

- **Explanation:**
  - Moves `chromedriver` to `/usr/local/bin/` so that it's accessible system-wide.
  - Makes `chromedriver` executable.

#### **c. Verify Installation**

```bash
# Verify that ChromeDriver is installed correctly
chromedriver --version
```

- **Expected Output:**
  - Displays the version of ChromeDriver installed, confirming successful installation.

### **8. Ensure Font Files Are Present**

Your script expects a `fonts` directory containing the required font files.

```bash
# Create the 'fonts' directory if it doesn't exist
mkdir -p ./fonts
```

1. **Download the Required Fonts:**
   
   Download the DejaVu fonts from the [DejaVu Fonts](https://dejavu-fonts.github.io/) project.

2. **Place the Fonts in the `fonts` Directory:**

```bash
# Replace '/path/to/downloaded/' with the actual path where you downloaded the fonts
cp /path/to/downloaded/DejaVuSansCondensed.ttf ./fonts/
cp /path/to/downloaded/DejaVuSansCondensed-Bold.ttf ./fonts/
```

- **Explanation:**
  - Copies the downloaded font files into the `fonts` directory.

## Usage

Run the script from the command line with the required and optional arguments as needed.

### **Basic Usage**

```bash
python WebToPDF-Crawler.py https://example.com
```

This command starts crawling at `https://example.com` with default settings (depth=3, output PDF named `web_content.pdf`).

### **Advanced Usage**

```bash
python WebToPDF-Crawler.py https://example.com \
  -d 2 \
  -o output.pdf \
  -f ./fonts/ \
  -e \
  -v \
  -c '{"text_only": true, "specific_image_types": ["png", "jpg"]}' \
  -i \
  -s
```

**Parameters:**

- `https://example.com`: The starting URL for the crawl.
- `-d 2` or `--depth 2`: Sets the maximum crawl depth to 2.
- `-o output.pdf` or `--output output.pdf`: Specifies the name of the output PDF file.
- `-f ./fonts/` or `--fonts ./fonts/`: Specifies the directory containing the required font files.
- `-e` or `--external`: Includes external links in the crawl.
- `-v` or `--verbose`: Enables verbose logging for detailed output.
- `-c '{"text_only": true, "specific_image_types": ["png", "jpg"]}'` or `--content-filter '{"text_only": true, "specific_image_types": ["png", "jpg"]}'`: Applies content filters to extract only text and specific image types.
- `-i` or `--interactive`: Enables interactive mode, prompting the user to choose whether to crawl each discovered link.
- `-s` or `--support-dynamic`: Enables support for dynamic content using Selenium.

## Docker Usage

If you prefer to use Docker for running the crawler, follow the steps below.

### **Building the Docker Image**

Navigate to the directory containing your `Dockerfile` and run:

```bash
docker build -t webtopdf-crawler .
```

### **Running the Container**

Pass command-line arguments as needed:

```bash
docker run --rm -it webtopdf-crawler https://example.com -d 2 -o output.pdf -f ./fonts/ -v
```

**Note:** Ensure that the `fonts` directory and any necessary WebDriver binaries are accessible within the Docker container.

## Configuration Options

### **Command-Line Arguments**

- **Positional Arguments:**
  - `start_url`: The initial URL to start crawling from.

- **Optional Arguments:**
  - `-d`, `--depth`: Maximum crawl depth (default: 3).
  - `-o`, `--output`: Output PDF file name (default: `web_content.pdf`).
  - `-f`, `--fonts`: Directory containing font files (default: `./fonts/`).
  - `-e`, `--external`: Include external links in the crawl.
  - `-v`, `--verbose`: Enable verbose logging.
  - `-c`, `--content-filter`: JSON string to filter content. Example:

    ```json
    '{"text_only": true, "specific_image_types": ["png", "jpg"]}'
    ```

  - `-i`, `--interactive`: Enable interactive mode to choose which links to follow.
  - `-s`, `--support-dynamic`: Support dynamic content using Selenium.

### **Content Filtering**

Specify content filters using a JSON string to include or exclude specific types of content.

**Example: Extract only text and PNG/JPG images**

```bash
-c '{"text_only": true, "specific_image_types": ["png", "jpg"]}'
```

**Options:**

- `text_only`: `true` or `false` to extract only text.
- `specific_image_types`: List of image file extensions to include (e.g., `["png", "jpg"]`).

## Features

### **Asynchronous Crawling**

Utilizes `aiohttp` and `asyncio` to perform asynchronous HTTP requests, enhancing the crawling speed and efficiency, especially for large websites with numerous internal links.

### **Dynamic Content Support**

Integrates `Selenium` to handle websites that load content dynamically via JavaScript. This ensures comprehensive content extraction from modern, interactive websites.

### **Interactive Mode**

When enabled, the crawler prompts the user to decide whether to follow each discovered link, providing granular control over the crawling process.

### **Crawl State Management**

Implements pause and resume functionality by saving the crawl state to disk (`crawl_state.json`). This allows users to manage long-running crawls without losing progress.

### **Content Filtering**

Offers advanced content filtering options, enabling users to tailor the crawl to specific needs, such as extracting only text or specific image types.

### **Respect for `robots.txt`**

Adheres to the `robots.txt` policies of websites, ensuring ethical and compliant crawling practices.

### **User-Agent Customization**

Allows customization of the HTTP User-Agent string to properly identify the crawler and reduce the risk of being blocked by target websites.

## Notes

- **Error Handling**: The script includes comprehensive error handling for network requests, image processing, and PDF generation. Issues are logged to aid in troubleshooting.

- **Logging**: Verbose logging can be enabled with the `-v` flag to receive detailed information about the crawling process, including pages crawled, images processed, and any errors encountered.

- **Performance Optimization**: The script optimizes image processing by handling conversions asynchronously and limiting concurrent operations to prevent resource exhaustion.

- **Extensibility**: The modular design allows for easy integration of additional features, such as support for more content types or integration with web APIs.

## Future Enhancements

While the script incorporates many advanced features, future improvements can include:

- **Comprehensive Unit Testing**: Develop a suite of unit tests covering all major functionalities to ensure reliability and facilitate future development.

- **Advanced Content Filtering**: Implement more sophisticated filtering options, such as CSS selectors or XPath expressions, for precise content extraction.

- **API Integration**: Automatically detect and utilize available web APIs for more efficient content retrieval when available.

- **Graphical User Interface (GUI)**: Develop a GUI for users who prefer not to use command-line tools, enhancing accessibility.

- **Distributed Crawling**: Implement distributed crawling capabilities to handle extremely large websites more efficiently.

- **Enhanced PDF Formatting**: Introduce advanced formatting options, such as custom styles, tables of contents, and embedded hyperlinks.

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [aiohttp](https://aiohttp.readthedocs.io/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [FPDF](https://pyfpdf.readthedocs.io/)
- [Pillow](https://python-pillow.org/)
- [CairoSVG](https://cairosvg.org/)
- [Selenium](https://www.selenium.dev/)
