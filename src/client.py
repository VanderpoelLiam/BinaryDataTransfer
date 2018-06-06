import math
import os

import binary_data_pb2
import binary_data_pb2_grpc
import device
import grpc
import time


def run():
    # Set up the client to communicate with the device
    channel = grpc.insecure_channel('localhost:50051')
    try:
        # Wait 10 seconds for the server to start
        grpc.channel_ready_future(channel).result(timeout=10)
    except grpc.FutureTimeoutError:
        sys.exit('Error connecting to server')
    else:
        upload_stub = binary_data_pb2_grpc.UploadStub(channel)
        download_stub = binary_data_pb2_grpc.DownloadStub(channel)

    image_filename = "../images/cat.png"

    # Create the Blob to store the cat image
    blob_spec = device.create_blob_spec(image_filename)
    create_blob_response = upload_stub.CreateBlob(blob_spec)

    # Get the BlobInfo and the BlobId
    blob_info = create_blob_response.blob_info
    blob_id = blob_info.id

    # Check there were no issues
    assert(create_blob_response.error.has_occured == False)
    print("\nNo issues creating the blob")

    # Check the blob info from creating the blob matches the info returned by
    # GetBlobInfo
    info_response = download_stub.GetBlobInfo(blob_id)
    assert(blob_info == info_response.blob_info)
    assert(info_response.error.has_occured == False)
    print("\nCreated blob info matches that stored on the device")

    # Break up the image into chunks
    print("\nBreaking up the image into chunks")
    chunk_count = blob_spec.chunk_count
    chunk_size = device.get_chunk_size(blob_spec)
    chunks = device.create_chunks(image_filename, chunk_count, chunk_size, blob_id)

    # Upload the chunks to the server
    print("\nUploading chunks:\n")
    for i in range(0, chunk_count):
        chunk = chunks[i]
        upload_response = upload_stub.UploadChunk(chunk)

        # Check there were no issues
        assert(upload_response.error.has_occured == False)
        print("    Uploading chunk number %i" % i)
        time.sleep(1)

    print("\nUploaded all chunks")

    # Download all the chunks and ensure they match
    print("\nDownloading chunks:\n")
    for i in range(0, chunk_count):
        chunk_spec = binary_data_pb2.ChunkSpec(blob_id=blob_id, index=i)
        download_response = download_stub.GetChunk(chunk_spec)

        # Check there were no issues
        assert(download_response.error.has_occured == False)
        print("    Downloaded chunk number %i" % i)
        time.sleep(1)

        # Check the chunks match
        chunk = chunks[i]
        assert(download_response.payload == chunk.payload)
        print("    The data matches!")

    # Get the average image brightness
    print("\nGetAverageBrightness of the image")
    command_response = upload_stub.GetAverageBrightness(blob_id)
    avg_brightness = device.bytes_to_int(command_response.payload)
    print("    Result: %i" % avg_brightness)

    # Delete the blob
    print("\nDeleting the blob")
    delete_response = upload_stub.DeleteBlob(blob_id)
    assert(delete_response.error.has_occured == False)
    print("\nBlob deleted")

    # Check we get an error if we try and download a chunk
    chunk_spec = binary_data_pb2.ChunkSpec(blob_id=blob_id, index=0)
    download_response = download_stub.GetChunk(chunk_spec)
    assert(download_response.error.has_occured == True)
    print("\nWe get an error if we try and download a chunk from this deleted blob")

    # Check we get an error if we try and get the average image brightness
    print("\nAttempting to GetAverageBrightness of the image")
    command_response = upload_stub.GetAverageBrightness(blob_id)
    assert(command_response.error.has_occured == True)
    print("\nWe get an error if we try and get the average image brightness of this deleted blob")

    # Check we do not get an error if we try delete the blob again
    delete_response = upload_stub.DeleteBlob(blob_id)
    assert(delete_response.error.has_occured == False)
    print("\nWe do not get an error if we try and delete the blob again")

    # Now we perform a measurement which generates a blob
    print("\nPerforming measurement")
    measurement_response = download_stub.GetMeasurementData(binary_data_pb2.Empty())
    assert(measurement_response.error.has_occured == False)
    print("\nNo issues performing the measurement")

    # Get the BlobInfo and the BlobId
    blob_info = measurement_response.blob_info
    blob_id = blob_info.id

    # Check the blob info from creating the blob matches the info returned by
    # GetBlobInfo
    info_response = download_stub.GetBlobInfo(blob_id)
    assert(blob_info == info_response.blob_info)
    assert(info_response.error.has_occured == False)
    print("\nMeasurement blob info matches that stored on the device")

    # Get the average image brightness for our measurement image
    print("\nGetAverageBrightness of the measurement image")
    command_response = upload_stub.GetAverageBrightness(blob_id)
    avg_brightness = device.bytes_to_int(command_response.payload)
    print("    Result: %i" % avg_brightness)

    # Finally we can delete the blob
    print("\nDeleting the measurement blob")
    delete_response = upload_stub.DeleteBlob(blob_id)
    assert(delete_response.error.has_occured == False)
    print("\nBlob deleted")

if __name__ == '__main__':
  run()
