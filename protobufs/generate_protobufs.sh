#! /bin/sh

# poetry run python -m grpc_tools.protoc -I=protobufs/ --python_out=plugin_runner/ --pyi_out=plugin_runner/ --grpc_python_out=plugin_runner/ protobufs/**/*.proto
python -m grpc_tools.protoc -I=protobufs/ --python_out=plugin_runner/ --pyi_out=plugin_runner/ --grpc_python_out=plugin_runner/ protobufs/**/*.proto
