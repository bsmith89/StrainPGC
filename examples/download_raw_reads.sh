#!/usr/bin/env bash

# SAMPLES="HSM67VDP HSM6XRSI PSM6XBW3 PSM7J1A2 MSM79HCG MSM79HCI"
SAMPLES="MSM79HCI"

mkdir -p raw
cd raw
for sample in $SAMPLES
do
    echo $sample
    curl -O https://ibdmdb.org/downloads/raw/HMP2/MGX/2018-05-04/$sample.tar \
    && tar -xf $sample.tar \
    && rm $sample.tar
done
cd ..