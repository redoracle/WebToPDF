#!/bin/bash
set -euo pipefail

VERSION="$1"

echo "Preparing release ${VERSION}"

# Update ARG VERSION in Dockerfile
sed -i "s/^ARG VERSION=.*/ARG VERSION=${VERSION}/" Dockerfile

echo "Updated Dockerfile ARG VERSION to ${VERSION}"

# Write flag file for the post-release steps
echo "${VERSION}" > .release-prepared
