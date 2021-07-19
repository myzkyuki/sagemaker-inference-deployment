#!/bin/bash

TF_VERSION="v2.3.1"
CODE_DIR="code"

outdir=$(pwd)/$CODE_DIR
rm -rf ${outdir}/tensorflow

tmpdir=$(mktemp -d)
echo "tmpdir: ${tmpdir}"
cd $tmpdir

python3 -m venv buildenv
source buildenv/bin/activate
pip3 --no-cache-dir install grpcio==1.29.0 grpcio-tools==1.29.0
git clone --depth 1 -b $TF_VERSION https://github.com/tensorflow/tensorflow.git
cd tensorflow
python3 -m grpc_tools.protoc \
    -I. \
    --python_out=$outdir \
    --grpc_python_out=$outdir \
    tensorflow/core/{framework,example,protobuf}/*.proto
