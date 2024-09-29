# Requirements for all of my compbio containers.
#
FROM condaforge/mambaforge:24.7.1-0 AS compbio
RUN \
    apt-get update \
    && apt-get install -y \
        less \
        make \
        g++ \
        libz-dev \
        libtbb2 \
    && rm -rf /var/lib/apt/lists/*
RUN \
    mkdir -p src && cd src \
    && git clone https://github.com/zjshi/gt-pro gt-pro && cd gt-pro \
    && make && ln -s $PWD/GT_Pro /usr/bin/
RUN \
    mkdir -p src && cd src \
    && git clone https://github.com/najoshi/sickle sickle && cd sickle \
    && make && ln -s $PWD/sickle /usr/bin/
RUN \
    mkdir -p src && cd src \
    && git clone https://github.com/vsbuffalo/scythe scythe && cd scythe \
    && make all && ln -s $PWD/scythe /usr/bin/
RUN \
    mamba install -y -c conda-forge -c bioconda \
        cython \
        ipython \
        jupyterlab \
        lz4 \
        matplotlib \
        numpy \
        pandas \
        patsy \
        pigz \
        pip \
        scikit-learn \
        scipy \
        seaborn \
        snakemake \
        statsmodels \
        tqdm \
        xarray \
        netCDF4 \
        xlrd \
        openpyxl \
        biopython \
        bowtie2 \
        fastuniq \
        pysam \
        samtools \
        seqtk \
    && conda clean -afy
RUN \
    mamba install -y -c pytorch -c nvidia \
        pytorch-cuda=12.4 \
        pytorch \
        torchvision \
        torchaudio \
    && conda clean -afy
RUN \
    git clone https://github.com/bsmith89/StrainFacts src/StrainFacts && cd src/StrainFacts \
    && git reset --hard bd6f3ff3bc7b2b655c4a6843a1edbc6c3c0c28c3 \
    && pip install --no-cache-dir --upgrade pip \
    && pip install -e .
RUN \
    git clone https://github.com/CZBiohub-sf/MIDAS src/MIDAS && cd src/MIDAS \
    && git reset --hard 8e321ed29080e1ee3138f69e56b033d17d140798 \
    && pip install -e .

# THIS version of StrainPGC
ADD . src/StrainPGC/
RUN \
    pip install -e src/StrainPGC/
