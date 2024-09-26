#!/usr/bin/env bash

outdir="examples/ref/gtpro"

mkdir -p $outdir && cd $outdir
curl -O http://jason.shi-bucket.s3.amazonaws.com/public/20190723_881species_optimized_db_kmer_index.bin
curl -O http://jason.shi-bucket.s3.amazonaws.com/public/20190723_881species_optimized_db_snps.bin
curl -O http://jason.shi-bucket.s3.amazonaws.com/public/variants_main.covered.hq.snp_dict.tsv
curl -O http://jason.shi-bucket.s3.amazonaws.com/public/species_taxonomy_ext.tsv
