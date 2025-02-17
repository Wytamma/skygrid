rule iqtree:
    input:
        alignment = config["alignment"],
    output:
        tree_file = OUTDIR / "iqtree" /  "iqtree.treefile",
    conda:
        ENVS_DIR / "rttr.yaml",
    params:
        fconst = f'-fconst {config.get("constant_sites")}' if config.get("constant_sites") else "",
        prefix = OUTDIR / "iqtree" / "iqtree",
    shell:
        """
        iqtree -redo -s {input.alignment} -m GTR+G -nt AUTO -pre {params.prefix} {params.fconst}
        """

rule prepare_treetime_metadata:
    input:
        alignment = config["alignment"],
    output:
        metadata = OUTDIR / "dates.tsv",
    shell:
       """
       python {SCRIPT_DIR}/prepare_treetime_metadata.py \
       {input.alignment} \
       {output.metadata}
       """

def calculate_sequence_lengths(alignment, constant_sites=None):
    # read first sequence from alignment accounting for multi-line fasta
    with open(alignment) as f:
        first_line = f.readline()
        sequence = ""
        for line in f:
            if line.startswith(">"):
                break
            sequence += line.strip()
    sequence_length = len(sequence)
    # add constant sites if provided
    if constant_sites:
        sequence_length += sum(int(c) for c in constant_sites.split(","))
    return sequence_length

rule treetime:
    input:
        tree = rules.iqtree.output.tree_file,
        metadata = rules.prepare_treetime_metadata.output.metadata,
        alignment = config["alignment"],
    output:
        regression = OUTDIR / "treetime" / "root_to_tip_regression.pdf",
        outliers = OUTDIR / "treetime" / "outliers.tsv",
        dates = OUTDIR / "treetime" / "dates.tsv",
    conda:
        ENVS_DIR / "rttr.yaml",
    params:
        sequence_length = calculate_sequence_lengths(config["alignment"], config.get("constant_sites")),
        outdir = OUTDIR / "treetime",
    shell:
        """
        treetime \
        --tree {input.tree} \
        --dates {input.metadata} \
        --aln {input.alignment} \
        --sequence-length {params.sequence_length} \
        --coalescent skyline \
        --outdir {params.outdir}
        
        # Create outliers.tsv file if it does not exist
        touch {output.outliers}
        """