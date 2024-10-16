def prefix_workdir(path):
    return os.path.join(config["outdir"], path)


def prefix_benchmarkdir(path):
    return os.path.join(config["benchdir"], path)


integer_wc = "[0-9]+"
