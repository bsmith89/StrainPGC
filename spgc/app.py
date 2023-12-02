from spgc.estimation import partition_gene_content
from spgc.pandas_util import idxwhere
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
        "outpath",
        metavar="OUTPATH",
        help="Where to write strain-by-gene assignments table",
    )

    # Parameters
    parser.add_argument(
        "--species-free-thresh",
        "-f",
        type=float,
        help="Species-free depth threshold.",
        default=spgc.DEFAULT_SPECIES_FREE_THRESHOLD,
    )
    parser.add_argument(
        "--depth-ratio-thresh",
        "-d",
        type=float,
        help="Depth ratio selection threshold.",
        default=spgc.DEFAULT_DEPTH_RATIO_THRESHOLD,
    )
    parser.add_argument(
        "--correlation-thresh",
        "-c",
        type=float,
        help="Correlation selection threshold.",
        default=spgc.DEFAULT_CORRELATION_THRESHOLD,
    )

    # Output args
    parser.add_argument(
        "--full-output",
        action="store_true",
        help="Write full analysis details to NetCDF.",
    )

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
    assert args.species_free_thresh >= 0, "Species-free depth threshold must be >=0"
    assert (
        0 <= args.correlation_thresh <= 1.0
    ), "Gene depth ratio selection threshold must be >=0 and <= 1.0"
    assert (
        0 <= args.depth_ratio_thresh
    ), "Gene correlation selection threshold must be >=0"
    # TODO: Other parameters

    # (2) Load input data.
    logging.info(f"Reading gene depths from {args.depth_table_inpath}.")
    depth_table = pd.read_table(args.depth_table_inpath, index_col=0).rename_axis(
        index="gene", columns="sample"
    )

    logging.info(f"Reading core genes from {args.core_genes_inpath}.")
    with open(args.core_genes_inpath) as f:
        core_genes = [line.strip() for line in f]

    logging.info(f"Reading strain partitioning from {args.strain_mapping_inpath}.")
    strain_mapping = pd.read_table(
        args.strain_mapping_inpath, names=["sample", "strain"]
    )

    # (3) Run SPGC on data
    logging.info("Running SPGC.")
    result = partition_gene_content(
        depth_table,
        core_genes,
        strain_mapping,
        args.species_free_thresh,
        args.depth_ratio_thresh,
        args.correlation_thresh,
    )

    # (4) Write outputs
    if args.full_output:
        logging.info(f"Writing NetCDF with all results to {args.outpath}.")
        result.to_netcdf(args.outpath)
    else:
        result["gene_selected"].to_pandas().to_csv(args.outpath, sep="\t")

    # (5) Write strain metadata
    # TODO


def main():
    args = parse_cli_args()
    setup_cli_logging(args)
    run_cli_app(args)
