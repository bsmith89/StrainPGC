# Requirements for all of my compbio containers.
#
FROM condaforge/mambaforge AS compbio
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
    mamba install -y -c conda-forge -c bioconda -c zhaoc1 \
        midas \
    && conda clean -afy
RUN \
    pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir git+https://github.com/bsmith89/StrainFacts

ADD . src/StrainPGC/
RUN \
    pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir  src/StrainPGC/
