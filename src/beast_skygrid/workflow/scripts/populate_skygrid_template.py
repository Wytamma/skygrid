#!/usr/bin/env python3
from pathlib import Path
from typing_extensions import Annotated

from jinja2 import StrictUndefined, Template
from beast_skygrid.workflow.utils import taxa_from_fasta
import typer

def populate_template(
        template_path: Annotated[Path, typer.Argument(help="Path to the input Beast template file.", exists=True, file_okay=True, dir_okay=False)],
        alignment_path: Annotated[Path, typer.Argument(help="Path to the input alignment file.", exists=True, file_okay=True, dir_okay=False)],
        dimensions: Annotated[int, typer.Option(help="Number of dimensions in the SkyGrid model.")],
        cutoff: Annotated[float, typer.Option(help="Estiamted tMRCA of the tree.")],
        output: Annotated[Path, typer.Option(help="Path to the output Beast XML file.", dir_okay=False, writable=True)] = None,
        clock: Annotated[str, typer.Option(help="Clock model to use in the analysis.")] = "strict",
        relaxed_gamma_shape: Annotated[float, typer.Option(help="Shape parameter of the gamma distribution for the relaxed clock model.")] = 0.3,
        relaxed_gamma_scale: Annotated[float, typer.Option(help="Scale parameter of the gamma distribution for the relaxed clock model.")] = 0.001,
        chain_length: Annotated[int, typer.Option(help="Length of the MCMC chain.")] = 100000000,
        samples: Annotated[int, typer.Option(help="Number of samples to draw from the MCMC chain.")] = 10000,
        date_delimiter: Annotated[str, typer.Option(help="Delimiter for the date in the fasta header.")] = "|",
        date_index: Annotated[int, typer.Option(help="Index of the date in the fasta header.")] = -1,
        constant_sites: Annotated[str, typer.Option(help="Constant sites in format 'As Ts Gs Cs'.")] = None,
        trace: Annotated[bool, typer.Option(help="Whether to enable the trace log.")] = True,
        trees: Annotated[bool, typer.Option(help="Whether to enable the trees log.")] = True,
        sample_from_prior: Annotated[bool, typer.Option(help="Whether to sample from the prior.")] = False,
        fixed_clock_rate: Annotated[float, typer.Option(help="Fixed clock rate to use in the analysis.")] = None,
    ):
    """
    Populates a BEAST template with the given parameters.
    """
    # Load the template
    template = Template(template_path.read_text(), undefined=StrictUndefined)

    # Parse the alignment file into Taxon objects
    taxa = taxa_from_fasta(alignment_path, date_delimiter=date_delimiter, date_index=date_index)

    log_every = max(1, chain_length // samples)

    trace_log_every = log_every
    trace_log_name = "skygrid.log"

    tree_log_every = log_every
    tree_log_name = "skygrid.trees"

    # Render the template
    rendered_template = template.render(
        taxa=taxa,
        clockModel=clock,
        relaxedGammaShape=relaxed_gamma_shape,
        relaxedGammaScale=relaxed_gamma_scale,
        chainLength=chain_length,
        screenLogEvery=log_every,
        traceLogEvery=trace_log_every,
        traceLogName=trace_log_name,
        treeLogEvery=tree_log_every,
        treeLogName=tree_log_name,
        dimensions=dimensions,
        cutoff=cutoff,
        constantSites=constant_sites,
        sampleFromPrior=sample_from_prior,
        fixedClockRate=fixed_clock_rate,
    )
    if output:
        # Write the rendered template to a file
        output.write_text(rendered_template)
    else:
        # Print the rendered template to the console
        print(rendered_template)


if __name__ == "__main__":
    typer.run(populate_template)