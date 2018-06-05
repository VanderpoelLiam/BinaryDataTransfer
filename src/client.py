import grpc
import os
import binary_data_pb2
import binary_data_pb2_grpc
import math
import device
from google.protobuf.json_format import MessageToJson


def run():
    # Set up the client to communicate with the device
    channel = grpc.insecure_channel('localhost:50051')
    upload_stub = binary_data_pb2_grpc.UploadStub(channel)
    download_stub = binary_data_pb2_grpc.DownloadStub(channel)

    # Get info on the data we are going to work with
    image_filename = '../images/cat.png'
    blob_size = os.stat(image_filename).st_size # File size in bytes
    chunk_count = 10
    chunk_size = math.ceil(blob_size/chunk_count) # Overestimate chunk_size

    # Create the Blob to store the cat image
    blob_spec = binary_data_pb2.BlobSpec(size=blob_size, chunk_count=chunk_count)
    create_blob_response = upload_stub.CreateBlob(blob_spec)

    # Get the BlobInfo and the BlobId
    blob_info = create_blob_response.blob_info
    blob_id = blob_info.id

    # Check there were no issues
    assert(create_blob_response.error.has_occured == False)
    print("\nNo issues creating the blob")

    # Check the blob info from creating the blob matches the info returned by
    # GetBlobInfo
    assert(blob_info == download_stub.GetBlobInfo(blob_id))
    print("\nNo issues retrieving the blob info from the device")

    # Break up the image into chunks
    print("\nBreaking up the image into chunks")
    chunks = []
    with open(image_filename, "rb") as binary_file:
        for i in range(0, chunk_count):
            # Seek the ith chunk location and read chunk_size bytes
            binary_file.seek(i*chunk_size)
            payload = binary_file.read(chunk_size)

            # Create the corresponding chunk
            chunk = binary_data_pb2.Chunk(blob_id=blob_id, index=i,
                                            payload=payload)

            # Add it to the chunk array
            chunks.append(chunk)

    # Upload the chunks to the server
    print("\nUploading chunks:\n")
    for i in range(0, chunk_count):
        chunk = chunks[i]
        upload_response = upload_stub.UploadChunk(chunk)

        # Check there were no issues
        assert(upload_response.error.has_occured == False)
        print("    Uploading chunk number %i" % i)

    print("\nUploaded all chunks")

    # Download all the chunks and ensure they match
    # print("\nDownloading chunks:\n")
    # for i in range(0, chunk_count):
    #     chunk_spec = binary_data_pb2.ChunkSpec(blob_id=blob_id, index=i)
    #     download_response = download_stub.GetChunk(chunk_spec)
    #
    #     # Check there were no issues
    #     assert(download_response.error.has_occured == False)
    #     print("    Downloaded chunk number %i" % i)
    #
    #     # Check the chunks match
    #     chunk = chunks[i]
    #     assert(download_response.payload == chunk.payload)
    #     print("    The data matches!")

    # Get the average image brightness
    print("GetAverageBrightness of the image")
    command_response = upload_stub.GetAverageBrightness(blob_id)
    avg_brightness = device.bytes_to_int(command_response.payload)
    print("    Result: %i" % avg_brightness)




if __name__ == '__main__':
  run()
