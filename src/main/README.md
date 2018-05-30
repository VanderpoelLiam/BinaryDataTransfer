To generate the classes associated with the .proto files, navigate to
".\python" then enter: "python -m grpc_tools.protoc -I../proto --python_out=. --grpc_python_out=. ../proto/binary_data.proto"
