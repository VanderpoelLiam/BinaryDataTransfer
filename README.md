# BinaryDataTransfer
Communicating binary data with gRPC as the base technology

The following assumes you are in the BinaryDataTransfer directory:

Run all tests in "./tests" with just "nosetests". Run only "test_device.py" with "nosetests tests/test_device.py"

To generate the classes associated with the .proto files, run
"python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=. ./proto/binary_data.proto"
