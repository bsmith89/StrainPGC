from spgc.estimation import (
    partition_gene_content,
    estimate_depth,
    load_depth_and_core_genes_list_to_xarray,
)
import spgc
import logging
import sys
import pandas as pd
import xarray as xr


class App:
    """Base-class for subcommand "applications".

    Custom subcommands must subclass App (or a subclass of App) and override
    the following methods:

    - add_custom_cli_args
    - validate_and_transform_args
    - execute

    Subcommands can then be registered in spgc.__main__ by adding them to the
    *APPLICATIONS* dict.

    """

    def __init__(self, subparsers, incantation):
        self.parser = subparsers.add_parser(incantation, help=self._help)
        self._add_cli_args()
        self.parser.set_defaults(subcommand_main=self._run)

    @property
    def _help(self):
        return self.__doc__

    def _add_cli_args(self):
        # Default arguments
        self.parser.add_argument(
            "--version",
            action="version",
            version=spgc.__version__,
        )
        self.parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Print info messages to stderr.",
        )
        self.parser.add_argument(
            "--debug",
            action="store_true",
            help="Print debug messages to stderr.",
        )

        # App-specific setup.
        self.add_custom_cli_args()

    def _process_args(self, raw_args):
        # App specific parsing/validation/transformation
        try:
            final_args = self.validate_and_transform_args(raw_args)
        except AssertionError as err:
            logging.error(f"Argument validation failed: {err}")
            sys.exit(1)

        return final_args

    def _run(self, raw_args):
        args = self._process_args(raw_args)

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

        logging.debug(f"Arguments: {args}")

        # Run the app specific work.
        self.execute(args)

    def add_custom_cli_args(self):
        """Add app-specific CLI args to parser.

        Subclasses of App must override this method.
        Arguments may be added to self.parser, an
        instance of argparse.Parser.  # TODO: Check this.

        """
        raise NotImplementedError

    def validate_and_transform_args(self, args):
        """Add custom argument validation/transformation/parsing.

        Subclasses of App must override this method.

        This method is used by subclasses to
        implement any validation/transformation/parsing of
        the "raw" argparse.Namespace object
        that cannot be implemented easily within the argparse.Parser API.

        Subclass methods must operate only on the *args* input
        and must return an argparse.Namespace for usage during execution.

        """
        raise NotImplementedError

    def execute(self, args):
        """Implement all remaining work for the specific application.

        Subclasses of App must override this method.

        Execution should rely only on the properties of *args*.

        """
        raise NotImplementedError


class Example(App):
    """Example application to test the API."""

    def add_custom_cli_args(self):
        self.parser.add_argument("--foo", action="store_true", help="Should I foo?")
        self.parser.add_argument("--num", type=int, default=1, help="How many times?")

    def validate_and_transform_args(self, args):
        assert args.num < 5, "NUM must be less than 5"
        return args

    def execute(self, args):
        if args.foo:
            for i in range(args.num):
                print("Foo!")
        else:
            print("Nope, that's a bar.")


class EstimateSpeciesDepth(App):
    """Run species depth estimation only."""

    def add_custom_cli_args(self):
        # Required arguments
        self.parser.add_argument(
            "depth_table_inpath",
            metavar="GENE_DEPTH_TABLE",
            help="TSV of gene depths",
        )
        self.parser.add_argument(
            "core_genes_inpath",
            metavar="CORE_GENE_LIST",
            help="List of core genes",
        )
        self.parser.add_argument(
            "outpath",
            metavar="OUTPATH",
            help="Where to write estimated sample-by-depth table",
        )

        # Parameters
        self.parser.add_argument(
            "--trim-frac-species-genes",
            "-s",
            type=float,
            help="Species genes proportion to cut for trimmed mean.",
            default=spgc.DEFAULT_TRIM_FRAC_SPECIES_GENES,
        )

    def validate_and_transform_args(self, args):
        # (1) Validate parameters
        assert (
            0 <= args.trim_frac_species_genes < 0.5
        ), "Species gene trimming fraction must be >= 0 and <= 1.0"
        return args

    def execute(self, args):
        # (2) Load input data.
        logging.info(f"Reading gene depths from {args.depth_table_inpath}.")
        depth_table = pd.read_table(args.depth_table_inpath, index_col=0).rename_axis(
            index="gene", columns="sample"
        )

        logging.info(f"Reading core genes from {args.core_genes_inpath}.")
        with open(args.core_genes_inpath) as f:
            core_genes = [line.strip() for line in f]

        # (3) Run estimation
        logging.info("Running Depth Estimation.")
        data = load_depth_and_core_genes_list_to_xarray(depth_table, core_genes)
        result = estimate_depth(data, args.trim_frac_species_genes)

        # (4) Write outputs
        logging.info(f"Writing results table to {args.outpath}.")
        result.to_pandas().to_csv(args.outpath, sep="\t", header=False)


class Run(App):
    """Run the core StrainPGC algorithm."""

    def add_custom_cli_args(self):
        # Required arguments
        self.parser.add_argument(
            "depth_table_inpath",
            metavar="GENE_DEPTH_TABLE",
            help="TSV of gene depths",
        )
        self.parser.add_argument(
            "core_genes_inpath",
            metavar="CORE_GENE_LIST",
            help="List of core genes",
        )
        self.parser.add_argument(
            "strain_mapping_inpath",
            metavar="STRAIN_MAPPING",
            help="TSV mapping samples to strains",
        )
        self.parser.add_argument(
            "outpath",
            metavar="OUTPATH",
            help="Where to write strain-by-gene assignments table",
        )

        # Parameters
        self.parser.add_argument(
            "--trim-frac-species-genes",
            "-s",
            type=float,
            help="Species genes proportion to cut for trimmed mean.",
            default=spgc.DEFAULT_TRIM_FRAC_SPECIES_GENES,
        )
        self.parser.add_argument(
            "--species-free-thresh",
            "-f",
            type=float,
            help="Species-free depth threshold.",
            default=spgc.DEFAULT_SPECIES_FREE_THRESHOLD,
        )
        self.parser.add_argument(
            "--depth-ratio-thresh",
            "-d",
            type=float,
            help="Depth ratio selection threshold.",
            default=spgc.DEFAULT_DEPTH_RATIO_THRESHOLD,
        )
        self.parser.add_argument(
            "--correlation-thresh",
            "-c",
            type=float,
            help="Correlation selection threshold.",
            default=spgc.DEFAULT_CORRELATION_THRESHOLD,
        )

        # Output args
        self.parser.add_argument(
            "--full-output",
            action="store_true",
            help="Write full analysis details to NetCDF.",
        )

    def validate_and_transform_args(self, args):
        # (1) Validate parameters
        assert (
            0 <= args.trim_frac_species_genes < 0.5
        ), "Species gene trimming fraction must be >= 0 and <= 1.0"
        assert (
            args.species_free_thresh >= 0
        ), "Species-free depth threshold must be >= 0"
        assert (
            0 <= args.correlation_thresh <= 1.0
        ), "Gene depth ratio selection threshold must be >= 0 and <= 1.0"
        assert (
            0 <= args.depth_ratio_thresh
        ), "Gene correlation selection threshold must be >= 0"
        return args

    def execute(self, args):
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
            args.strain_mapping_inpath,
            names=["sample", "strain"],
            dtype=str,
        )

        # (3) Run SPGC on data
        logging.info("Running SPGC.")
        result = partition_gene_content(
            depth_table,
            core_genes,
            strain_mapping,
            args.trim_frac_species_genes,
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

class DumpGeneResults(App):
    """Extract gene content results and write to TSV."""

    def add_custom_cli_args(self):
        # Required arguments
        self.parser.add_argument(
            "inpath",
            help="NetCDF file produced by `spgc run`.",
        )
        self.parser.add_argument(
            "outpath",
            help="TSV outpath.",
        )

    def execute(self, args):
        # (1) Load input data.
        logging.info(f"Reading StrainPGC formatted data.")
        result = xr.open_dataset(args.inpath)
        # (2) Write outputs
        logging.info(f"Writing estimated gene content table to {args.outpath}.")
        result["gene_selected"].to_pandas().rename_axis(index="gene").astype(int).to_csv(args.outpath, sep="\t")

class DumpStrainStats(App):
    """Extract strain statistics and write to TSV."""

    def add_custom_cli_args(self):
        # Required arguments
        self.parser.add_argument(
            "inpath",
            help="NetCDF file produced by `spgc run`.",
        )
        self.parser.add_argument(
            "outpath",
            help="TSV outpath.",
        )

    def execute(self, args):
        # (1) Load input data.
        logging.info(f"Reading StrainPGC formatted data.")
        result = xr.open_dataset(args.inpath)
        # (2) Collect outputs
        strain_sample_meta = (
            spgc[
                [
                    "num_gene",
                    "num_strain_sample",
                    "sum_strain_depth",
                    "max_strain_depth",
                    "species_gene_frac",
                    "log_selected_gene_depth_ratio_std",
                ]
            ]
            .to_dataframe()
            )
        # (2) Write outputs
        logging.info(f"Writing strain statistics table to {args.outpath}.")
        strain_sample_meta.rename_axis(index="strain").to_csv(args.outpath, sep="\t")
