# Skygrid

[![PyPI - Version](https://img.shields.io/pypi/v/beast-skygrid.svg)](https://pypi.org/project/beast-skygrid)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/beast-skygrid.svg)](https://pypi.org/project/beast-skygrid)

Skygrid is a Snakemake-based workflow tool designed for performing demographic analyses using BEAST’s skygrid model. It streamlines the entire pipeline—from sequence alignment parsing and outlier detection through BEAST MCMC sampling to post-analysis visualizations—so that you can focus on interpreting your results rather than managing complex workflows.

![](images/logo.png)

## Features

- **End-to-End Workflow:**  
  Automatically parses sequence alignments, performs root-to-tip regressions to detect outliers, executes BEAST analyses, and renders demographic plots and trees.
  
- **Customizable Configuration:**  
  Easily override workflow defaults by supplying a configuration file or specifying options on the command line. Customize clock models (strict/relaxed), chain lengths, sample sizes, and more.
  
- **Robust Resource Management:**  
  Leverages Snakemake’s advanced resource handling including multi-core execution, workflow locking, and DAG generation.

- **Seamless Integration:**  
  Integrates tools such as IQ-TREE, treetime, and R (via ggtree) to offer a comprehensive analysis suite.


## Installation

Skygrid is available on PyPI. Install it using pip:

```console
pip install beast-skygrid
```


## Quick Start

### 1. Prepare Your Data

Ensure you have a FASTA alignment file. This file is used to extract taxon names and sampling dates for your analysis. Sample dates must be in the format `>SampleName|YYYY-MM-DD`. For example:

```fasta
>Sample1|2020-01-01
ATG...
>Sample2|2020-02-01
ATG...
...
```

### 2. Run the Workflow

Invoke the skygrid workflow from the command line. For example:

```console
skygrid run --alignment your_alignment.fasta --output-dir results
```

This command will:

- **Extract Taxa & Dates:** Parse your alignment to determine the number of taxa and the sampling date range.
- **Root-to-Tip Regression & Outlier Detection:** Use root-to-tip regression to estimate the skygrid length and transition points. Optionally, filter out outlier sequences.
- **BEAST Analysis:** Generate a BEAST XML file from a Jinja2 template and run BEAST with the skygrid model.
- **Visualization:** Create skygrid plots and render the Maximum Clade Credibility (MCC) tree in SVG format.

### 3. Explore the Results

After completion, check the specified output directory (here, `results`). You will find:
- A skygrid plot (SVG, PNG, and PDF formats)
- BEAST logs and tree files
- Rendered MCC tree visualizations


## Command Line Options

To display the complete list of options, run:

```console
skygrid run -h
```

A summary of some key options:

- **Workflow Configuration Options:**
  - `--alignment` (`-a PATH`) **(required)**  
    Path to your sequence alignment file.
  - `--output-dir` (`-o PATH`)  
    Directory to save the output (default: `./skygrid`).
  - `--constant-sites TEXT`  
    Provide constant site counts in the format `'A,C,G,T'`.
  - `--discard-outliers`  
    Use a root-to-tip regression to identify and discard outlier sequences.
  - `--clock [strict|relaxed]`  
    Choose the clock model for the analysis (default: `strict`).
  - `--relaxed-mean-shape FLOAT` and `--relaxed-mean-scale FLOAT`  
    Parameters for the UCLD relaxed clock’s mean gamma prior (default: shape=0.3, scale=0.001).
  - `--fixed-clock-rate FLOAT`  
    Fix the clock rate to this value. If used with the relaxed clock the mean of the UCLD will be set to this value.
  - `--transition-points-per-year FLOAT`  
    Set the number of transition points per year for the skygrid (default: 2).
  - `--cutoff INTEGER`  
    Specify the skygrid length in years (if not provided, it is estimated from the data).
  - `--chain-length INTEGER`  
    Length of the MCMC chain (default: 10,000,000).
  - `--samples INTEGER`  
    Number of samples to extract from the chain (default: 10,000).
  - `--sample-from-prior`  
    Run the analysis by sampling from the prior distribution only.
  - `--beast-params TEXT`  
    Additional parameters to pass to BEAST (default: `-overwrite`).


## Workflow Overview

![](images/dag.png)

The skygrid workflow is divided into several key stages:

### 1. Taxa Extraction & Date Parsing

The workflow begins by parsing your FASTA alignment to extract taxon information and sampling dates. Dates must be in the format >SampleName|YYYY-MM-DD. Uncertain dates can be specified as >SampleName|YYYY-XX-XX or >SampleName|YYYY-MM-XX e.g. the sampling date for >SampleName|2020-XX-XX will be randomly sampled from the year 2020 (2020-2021).

### 2. Root-to-Tip Regression & Outlier Detection

The workflow uses root-to-tip regression (via `treetime`) to estimate the skygrid length (cutoff) and transition points (dimensions). Skygrid optionally uses a root-to-tip regression to identify and filter out outlier sequences.

### 3. BEAST Analysis

The workflow automatically generates a BEAST XML configuration file from a Jinja2 template. This XML file is used to run the BEAST analysis with parameters such as clock model, chain length, and sampling frequency. The BEAST run is executed as follows:

```python
rule beast:
    input:
        beast_XML_file = OUTDIR / "beast" / "skygrid.xml",
    output:
        log_file = OUTDIR / "beast" / "skygrid.log",
        trees_file = OUTDIR / "beast" / "skygrid.trees",
    shell:
        """
        beast {params.beast} -working {input.beast_XML_file} > {log} 2>&1
        """
```

### 4. Post-Processing & Visualization

After BEAST completes, the workflow:
- Computes the Maximum Clade Credibility (MCC) tree using `treeannotator`.
- Renders the MCC tree in SVG format with R (using scripts that leverage the `ggtree` package).
- Generates skygrid plots (SVG, PNG, PDF) to visualize changes in population size over time.


## Contributing

Contributions to skygrid are welcome! If you would like to propose improvements or bug fixes, please:

1. Fork the repository.
2. Create a feature branch for your changes.
3. Submit a pull request with a detailed description of your changes.

For major changes, please open an issue first to discuss what you would like to change.

## License

Skygrid is distributed under the terms of the [MIT License](https://spdx.org/licenses/MIT.html).

