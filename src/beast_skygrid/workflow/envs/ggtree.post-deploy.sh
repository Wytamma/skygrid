#!/usr/bin/env bash
set -o pipefail

# The conda environment's root is available as $CONDA_PREFIX.
# We explicitly use its Rscript binary to ensure we run the correct version.
R="$CONDA_PREFIX/bin/Rscript"

if [ ! -x "$R" ]; then
    echo "Error: Rscript not found in $CONDA_PREFIX/bin"
    exit 1
fi

# Run an inline R command to install skyplotr from GitHub if it's not already installed.
"$R" -e "if (!requireNamespace('skyplotr', quietly = TRUE)) {
           message('Installing skyplotr from GitHub...');
           devtools::install_github('4ment/skyplotr')
         } else {
           message('skyplotr is already installed.')
         }"
