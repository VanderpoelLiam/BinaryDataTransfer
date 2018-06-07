# BinaryDataTransfer
This project demonstrates moving around binary data with gRPC as the base technology. 

## Demonstration 
To run the demonstration open two terminals to the src/ directory. In one enter `python device.py`, in the other enter `python client.py`. The demonstration will showcase all the methods implemented by the device in device.py. As these methods are robust to connection losses, you may disconnect the device by pressing "Ctrl-C". At this point the client will attempt to reconnect for some time during which you can simply restart the device by again entering "python device.py" into the appropriate terminal. If the device is not restarted during this interval, the client will stop running.

## Testing
Navigate to the "BinaryDataTransfer/" directory. To run all tests the "tests/" directory, enter `nosetests` into the terminal. To run only the tests in the "test_device.py" module, enter `nosetests tests/test_device.py`.

## Generating classes from the Protocol Buffers
To generate the classes associated with the .proto files in the "protos/" directory, navigate to the "BinaryDataTransfer/" directory and enter the following in the terminal:

`python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/binary_data.proto`
