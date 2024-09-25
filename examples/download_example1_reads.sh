#!/usr/bin/env bash

sample_list="HSM67VDP HSM6XRSI PSM6XBW3 PSM7J1A2 MSM79HCG MSM79HCI"
dir="examples/input/reads"

mkdir -p $dir && cd $dir
for sample in $sample_list
do
    echo $sample
    curl -O "https://ibdmdb.org/downloads/raw/HMP2/MGX/2018-05-04/$sample.tar" \
    && tar -xf "$sample.tar" \
    && rm "$sample.tar"
done
