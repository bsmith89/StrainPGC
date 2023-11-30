import spgc
import logging
import argparse
import sys
import pandas as pd


def parse_cli_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        fromfile_prefix_chars="@",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=spgc.__version__,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print info messages to stderr.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug messages to stderr.",
    )

    # Required arguments
    parser.add_argument(
        "depth_table_inpath",
        metavar="GENE_DEPTH_TABLE",
        help="TSV of gene depths",
    )
    parser.add_argument(
        "core_genes_inpath",
        metavar="CORE_GENE_LIST",
        help="List of core genes",
    )
    parser.add_argument(
        "strain_mapping_inpath",
        metavar="STRAIN_MAPPING",
        help="TSV mapping samples to strains",
    )
    parser.add_argument(
        "assignments_outpath",
        metavar="OUTPATH",
        help="Where to write strain-by-gene assignments table",
    )

    # Additional outputs
    parser.add_argument(
        "--species-depth-out",
        dest="species_depth_outpath",
        nargs=1,
        help="Write estimated species depths to file.",
    )
    parser.add_argument(
        "--species-free-samples-out",
        dest="species_free_samples_outpath",
        nargs=1,
        help="Write list of samples with very low species depth to file.",
    )
    parser.add_argument(
        "--depth-ratio-out",
        dest="depth_ratio_outpath",
        nargs=1,
        help="Write table of gene depth ratios to file.",
    )
    parser.add_argument(
        "--depth-corr-out",
        dest="depth_correlation_outpath",
        nargs=1,
        help="Write table of gene depth correlations to file.",
    )

    # TODO: Add all parameters

    args = parser.parse_args()

    # If no arguments passed to app, print usage and error out.
    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)

    return args


def setup_cli_logging(args):
    # Setup logging
    logging.basicConfig(format="%(asctime)s %(message)s")
    if args.debug:
        logging_level = logging.DEBUG
    elif args.verbose:
        logging_level = logging.INFO
    else:
        logging_level = logging.WARNING
    logging.getLogger().setLevel(logging_level)
    logging.debug(f"Logging level set to {logging_level}.")


def run_cli_app(args):
    logging.debug(f"Arguments: {args}")

    # (1) Validate parameters
    # TODO

    # (2) Load input data.
    logging.info(f"Reading gene depths from {args.depth_table_inpath}.")
    depth_table = pd.read_table(args.depth_table_inpath)

    logging.info(f"Reading core genes from {args.core_genes_inpath}.")
    with open(args.core_genes_inpath) as f:
        core_genes = [line.strip() for line in f]

    logging.info(f"Reading strain partitioning from {args.strain_mapping_inpath}.")
    strain_mapping = pd.read_table(args.strain_mapping_inpath, index_col=0)

    # (3) Run SPGC on data
    logging.info("Running SPGC.")
    (
        assignments,
        species_depth,
        species_free_sample_list,
        depth_ratio,
        depth_correlation,
    ) = spgc.partition_gene_content(depth_table, core_genes, strain_mapping)

    # (4) Write outputs
    if args.species_depth_outpath:
        logging.info(f"Writing estimated species depth to {args.species_depth_outpath}.")
        species_depth.to_csv(args.species_depth_outpath, sep="\t")

    if args.species_free_samples_outpath:
        logging.info(
            f"Writing list of low-species-depth samples to {args.species_free_samples_outpath}."
        )
        with open(args.species_free_samples_outpath) as f:
            for sample in species_free_sample_list:
                print(sample, file=f)

    if args.depth_ratio_outpath:
        logging.info(f"Writing gene depth ratios to {args.depth_ratio_outpath}.")
        depth_ratio.to_csv(args.depth_ratio_outpath, sep="\t")

    if args.depth_correlation_outpath:
        logging.info(f"Writing gene depth correlation to {args.depth_correlation_outpath}.")
        depth_correlation.to_csv(args.depth_correlation_outpath, sep="\t")

    logging.info(f"Writing gene assignments to {args.assignments_outpath}.")
    assignments.to_csv(args.assignments_outpath, sep="\t")


def main():
    args = parse_cli_args()
    setup_cli_logging(args)
    run_cli_app(args)
