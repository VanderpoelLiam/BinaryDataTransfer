import binary_data_pb2
import binary_data_pb2_grpc
import grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = binary_data_pb2_grpc.UploadStub(channel)
    print("-------------- CreateBlob --------------")
    blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
    stub.CreateBlob(blob_spec)


if __name__ == '__main__':
    run()
