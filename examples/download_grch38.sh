#!/usr/bin/env bash

outdir="$1"
stem="GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.bowtie_index"

mkdir -p $outdir && cd $outdir
curl -O "ftp://ftp.ncbi.nlm.nih.gov/genomes/archive/old_genbank/Eukaryotes/vertebrates_mammals/Homo_sapiens/GRCh38/seqs_for_alignment_pipelines/$stem.tar.gz"
tar -xzf $stem.tar.gz
rm $stem.tar.gz
for file in $stem.*
do
    mv $file ${file/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.bowtie_index./GRCh38.}
done
