#!/usr/bin/env python3
# USAGE::
# workflow/scripts/merge_gtpro_counts.py \
#     102506 \
#     results/species/102506/gtpro/snv_counts.tsv.bz2 \
#     HSM67VDP=results/reads/HSM67VDP/gtpro/r1.snv_counts.tsv.bz2:results/reads/HSM67VDP/gtpro/r2.snv_counts.tsv.bz2 \
#     HSM6XRSI=results/reads/HSM6XRSI/gtpro/r1.snv_counts.tsv.bz2:results/reads/HSM6XRSI/gtpro/r2.snv_counts.tsv.bz2 \
#     MSM79HCG=results/reads/MSM79HCG/gtpro/r1.snv_counts.tsv.bz2:results/reads/MSM79HCG/gtpro/r2.snv_counts.tsv.bz2 \
#     PSM6XBW3=results/reads/PSM6XBW3/gtpro/r1.snv_counts.tsv.bz2:results/reads/PSM6XBW3/gtpro/r2.snv_counts.tsv.bz2 \
#     PSM7J1A2=results/reads/PSM7J1A2/gtpro/r1.snv_counts.tsv.bz2:results/reads/PSM7J1A2/gtpro/r2.snv_counts.tsv.bz2 \
#     MSM79HCI=results/reads/MSM79HCI/gtpro/r1.snv_counts.tsv.bz2:results/reads/MSM79HCI/gtpro/r2.snv_counts.tsv.bz2 \

import pandas as pd
import sys
from tqdm import tqdm


if __name__ == "__main__":
    species = sys.argv[1]
    outpath = sys.argv[2]
    input_args = sys.argv[3:]

    sample_to_paths = dict()
    for sample_arg in input_args:
        sample, paths_arg = sample_arg.split("=")
        paths = paths_arg.split(":")
        sample_to_paths[sample] = paths

    all_data = []
    for sample, inpaths in tqdm(sample_to_paths.items()):
        sample_data = []
        for path in inpaths:
            read_data = pd.read_table(path, dtype={"species": str})[
                lambda x: x.species == species
            ]
            sample_data.append(read_data)
        sample_data = (
            pd.concat(sample_data)
            .groupby(
                [
                    "species",
                    "global_pos",
                    "contig",
                    "local_pos",
                    "ref_allele",
                    "alt_allele",
                ]
            )
            .sum()
            .reset_index()
            .assign(sample=sample)
        )
        all_data.append(sample_data)
    all_data = pd.concat(all_data)
    all_data[
        [
            "sample",
            "species",
            "global_pos",
            "contig",
            "local_pos",
            "ref_allele",
            "alt_allele",
            "ref_count",
            "alt_count",
        ]
    ].to_csv(outpath, sep="\t", index=False, header=False)
