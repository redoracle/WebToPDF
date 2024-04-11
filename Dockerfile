# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /root

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for CairoSVG
RUN apt-get update && \
    apt-get install -y \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 shared-mime-info libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libffi-dev \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Define environment variable
ENV NAME WebToPDF-crawler

# Run WebToPDF-crawler.py when the container launches
ENTRYPOINT ["python", "/root/WebToPDF-crawler.py"]
CMD [""]
