#!/usr/bin/env bash

outdir="$1"

mkdir -p $outdir && cd $outdir
curl -kO https://raw.githubusercontent.com/vsbuffalo/scythe/master/illumina_adapters.fa
