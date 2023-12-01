import matplotlib.pyplot as plt


def plot_strain_gene_selection(
    data,
    strain,
    corr_thresh=None,
    depth_ratio_thresh=None,
    indicator="is_core_gene",
    indicator_color_palette={True: "tab:orange", False: "tab:blue"},
    ax=None,
    **scatter_kws
):
    strain_data = (
        data[["gene_depth_ratio", "gene_correlation", "gene_selected", indicator]]
        .sel(strain=1)
        .to_pandas()
        .assign(corr_complement=lambda x: 1 - x.gene_correlation)
        .sort_values("is_core_gene")
    )

    if corr_thresh is None:
        corr_thresh = strain_data[lambda x: x.gene_selected].gene_correlation.min()
    if depth_ratio_thresh is None:
        depth_ratio_thresh = strain_data[
            lambda x: x.gene_selected
        ].gene_depth_ratio.min()

    if ax is None:
        ax = plt.gca()

    default_scatter_kws = dict(s=10, alpha=0.75)

    for indicator_status, d in strain_data.groupby(indicator):
        ax.scatter(
            "corr_complement",
            "gene_depth_ratio",
            color=indicator_color_palette[indicator_status],
            data=d,
            **(scatter_kws | default_scatter_kws)
        )
    ax.axvline(1 - corr_thresh, lw=1, linestyle="--", color="r")
    ax.axhline(depth_ratio_thresh, lw=1, linestyle="--", color="r")
    ax.set_xscale("symlog", linthresh=1e-2, linscale=0.1)
    ax.set_yscale("symlog", linthresh=1e-2, linscale=0.1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 50)
    ax.invert_xaxis()
    return ax
