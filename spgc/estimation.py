import pandas as pd
from scipy.spatial.distance import cdist


def partition_gene_content(
    depth_table,
    core_genes,
    strain_mapping,
    species_free_thresh,
    depth_ratio_thresh,
    correlation_thresh,
):
    # Construct a dataset
    data = depth_table.stack().to_xarray().to_dataset(name="gene_depth")
    data["is_core_gene"] = data.gene.isin(core_genes)
    data["strain_pure"] = (
        strain_mapping.set_index(["sample", "strain"])
        .assign(flag=True)
        .flag.unstack()
        .reindex(data.sample.values)
        .fillna(False)
    )

    # Calculate statistics
    data["species_depth"] = data.sel(gene=data.is_core_gene).gene_depth.mean(
        "gene"
    )  # FIXME: Trimmed mean?
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
            1 - cdist(x.values.reshape((1, -1)), y.values, metric="cosine")[0],
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

    # Return result
    return data
