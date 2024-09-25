#!/usr/bin/env bash

mkdir -p examples/ref/gtpro
cd examples/ref/gtpro

curl -O http://jason.shi-bucket.s3.amazonaws.com/public/20190723_881species_optimized_db_kmer_index.bin
curl -O http://jason.shi-bucket.s3.amazonaws.com/public/20190723_881species_optimized_db_snps.bin
curl -O http://jason.shi-bucket.s3.amazonaws.com/public/variants_main.covered.hq.snp_dict.tsv
curl -O http://jason.shi-bucket.s3.amazonaws.com/public/species_taxonomy_ext.tsv
