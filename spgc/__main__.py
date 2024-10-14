import spgc.app
import argparse
import sys

APPLICATIONS = {
    "run": spgc.app.Run,
    "estimate_species_depth": spgc.app.EstimateSpeciesDepth,
    "foobar": spgc.app.Example,
    "dump_genes": spgc.app.DumpGeneResults,
    "dump_strains": spgc.app.DumpStrainStats,
}


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        fromfile_prefix_chars="@",
    )
    subparsers = parser.add_subparsers(dest="cmd", metavar="CMD", required=True)
    for invocation, app_class in APPLICATIONS.items():
        app_class(subparsers, invocation)

    # Default parsing
    raw_args = parser.parse_args(sys.argv[1:])
    raw_args.subcommand_main(raw_args)


if __name__ == "__main__":
    main()
