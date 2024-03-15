#!/usr/bin/env bash

pushd ..

python \
  -m grpc_tools.protoc \
  -I=protobufs/ \
  --python_out=plugin_runner/ \
  --pyi_out=plugin_runner/ \
  --grpc_python_out=plugin_runner/ \
  protobufs/generated/**/*.proto

popd
