#!/usr/bin/env bash
set -e

# Run this script from inside the /protobufs directory

pushd ..

python \
  -m grpc_tools.protoc \
  -I=protobufs/ \
  --python_out=./ \
  --pyi_out=./ \
  --grpc_python_out=./ \
  protobufs/canvas_generated/**/*.proto

popd
