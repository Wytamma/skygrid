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
        chain_length: Annotated[int, typer.Option(help="Length of the MCMC chain.")] = 100000000,
        samples: Annotated[int, typer.Option(help="Number of samples to draw from the MCMC chain.")] = 10000,
        date_delimiter: Annotated[str, typer.Option(help="Delimiter for the date in the fasta header.")] = "|",
        date_index: Annotated[int, typer.Option(help="Index of the date in the fasta header.")] = -1,
        constant_sites: Annotated[str, typer.Option(help="Constant sites in format 'As Ts Gs Cs'.")] = None,
        trace: Annotated[bool, typer.Option(help="Whether to enable the trace log.")] = True,
        trees: Annotated[bool, typer.Option(help="Whether to enable the trees log.")] = True,
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
    if trace and output:
        trace_log_name = output.parent / "skygrid.log"

    tree_log_every = log_every
    tree_log_name = "skygrid.trees"
    if trees and output:
        tree_log_name = output.parent / "skygrid.trees"


    # Render the template
    rendered_template = template.render(
        taxa=taxa,
        clockModel=clock,
        chainLength=chain_length,
        screenLogEvery=log_every,
        traceLogEvery=trace_log_every,
        traceLogName=trace_log_name,
        treeLogEvery=tree_log_every,
        treeLogName=tree_log_name,
        dimensions=dimensions,
        cutoff=cutoff,
        constantSites=constant_sites,
    )
    if output:
        # Write the rendered template to a file
        output.write_text(rendered_template)
    else:
        # Print the rendered template to the console
        print(rendered_template)


if __name__ == "__main__":
    typer.run(populate_template)