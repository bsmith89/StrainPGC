#!/usr/bin/env bash

outdir="$1"

mkdir -p $outdir && cd $outdir
wget --no-check-certificate --content-disposition https://fileshare.czbiohub.org/s/daK4Wj3N7EwSSrd/download
wget --no-check-certificate --content-disposition https://fileshare.czbiohub.org/s/XNCzWziB4JydWFH/download
wget --no-check-certificate --content-disposition https://fileshare.czbiohub.org/s/cYDwCAB539kE5yt/download
wget --no-check-certificate --content-disposition https://fileshare.czbiohub.org/s/XBzwFpfJpmJpBSQ/download
