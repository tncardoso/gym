#!/bin/bash
python -m grpc.tools.protoc -I ../deepwalk/robot/src/main/proto/  --python_out=. --grpc_python_out=. ../deepwalk/robot/src/main/proto/qwop.proto

