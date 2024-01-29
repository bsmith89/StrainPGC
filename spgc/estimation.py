import pandas as pd
import scipy as sp
import numpy as np
from scipy.spatial.distance import cdist
import xarray as xr


def partition_gene_content(
    depth_table,
    core_genes,
    strain_mapping,
    trim_frac_species_mean_depth,
    species_free_thresh,
    depth_ratio_thresh,
    correlation_thresh,
):
    # Construct a dataset
    data = depth_table.stack().to_xarray().to_dataset(name="gene_depth")
    data["is_core_gene"] = data.gene.isin(core_genes)
    # Strain info is currently stored redundantly as both a series of labels,
    data["pure_strain"] = strain_mapping.set_index("sample").strain
    # and a binary matrix.
    data["strain_pure"] = (
        strain_mapping.set_index(["sample", "strain"])
        .assign(flag=True)
        .flag.unstack()
        .reindex(data.sample.values)
        .fillna(False)
    )

    # Calculate statistics
    data["species_depth"] = xr.apply_ufunc(
        sp.stats.trim_mean,
        data.gene_depth.sel(gene=data.is_core_gene),
        input_core_dims=[["gene"]],
        kwargs=dict(axis=-1, proportiontocut=trim_frac_species_mean_depth),
    )
    data["species_free"] = data.species_depth < species_free_thresh

    gene_depth_ratio = {}
    gene_correlation = {}
    for strain in data.strain.values:
        strain_pure_samples = data.strain_pure.sel(strain=strain, drop=True)
        total_species_depth = data.species_depth.sel(sample=strain_pure_samples).sum(
            "sample"
        )
        total_gene_depth = data.gene_depth.sel(sample=strain_pure_samples).sum("sample")
        gene_depth_ratio[strain] = (total_gene_depth / total_species_depth).to_series()

        strain_pure_and_species_free_samples = strain_pure_samples | data.species_free
        x = data.species_depth.sel(sample=strain_pure_and_species_free_samples)
        y = data.gene_depth.sel(sample=strain_pure_and_species_free_samples)
        gene_correlation[strain] = pd.Series(
            1 - cdist(x.values.reshape((1, -1)), y.values, metric="correlation")[0],
            index=y.gene,
        )
    data["gene_depth_ratio"] = pd.DataFrame(gene_depth_ratio).rename_axis(
        columns="strain"
    )
    data["gene_correlation"] = pd.DataFrame(gene_correlation).rename_axis(
        index="gene", columns="strain"
    )

    # Select genes
    data["gene_selected"] = (data.gene_depth_ratio >= depth_ratio_thresh) & (
        data.gene_correlation >= correlation_thresh
    )

    # Strain metadata
    strain_sample_metadata = (
        data["species_depth"]
        .to_series()
        .groupby(data["pure_strain"].to_series())
        .agg(["count", "sum", "max"])
        .rename_axis("strain")
        .rename(
            columns={
                "count": "num_strain_sample",
                "sum": "sum_strain_depth",
                "max": "max_strain_depth",
            }
        )
        .to_xarray()
    )
    data = xr.merge([data, strain_sample_metadata])
    data["num_gene"] = data.gene_selected.sum("gene")
    # QC Stats
    data["log_species_gene_depth_ratio_std"] = np.log10(
        data["gene_depth_ratio"].sel(gene=data.is_core_gene) + depth_ratio_thresh
    ).std("gene")
    data["log_selected_gene_depth_ratio_std"] = (
        np.log10(
            data[["gene_depth_ratio", "gene_selected"]]
            .to_dataframe()[lambda x: x.gene_selected]
            .gene_depth_ratio
            + depth_ratio_thresh
        )
        .groupby("strain")
        .std()
        .to_xarray()
    )
    data["species_gene_frac"] = (
        data["gene_selected"].sel(gene=data.is_core_gene).mean("gene")
    )

    # Return result
    return data
