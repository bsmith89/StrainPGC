#!/usr/bin/env bash

outdir="examples/ref"

mkdir -p $outdir && cd $outdir
curl -O https://raw.githubusercontent.com/vsbuffalo/scythe/master/illumina_adapters.fa
