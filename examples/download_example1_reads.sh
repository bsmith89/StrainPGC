#!/usr/bin/env bash

outdir="$1"
sample_list="HSM67VDP HSM6XRSI PSM6XBW3 PSM7J1A2 MSM79HCG MSM79HCI"

mkdir -p $outdir && cd $outdir
for sample in $sample_list
do
    echo $sample
    curl -O "https://ibdmdb.org/downloads/raw/HMP2/MGX/2018-05-04/$sample.tar" \
    && tar -xf "$sample.tar" \
    && rm "$sample.tar"
done
