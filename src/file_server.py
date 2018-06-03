from datetime import datetime, timedelta
from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.any_pb2 import Any

import grpc
import json
import time
import binary_data_pb2
import binary_data_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def can_create_blob(blob_spec, availible_server_space):
    if have_space(blob_spec.size, availible_server_space):
        expiration_time = get_expiration_time()
        return binary_data_pb2.Response(valid_until=expiration_time)
    else:
        return binary_data_pb2.Response(error=get_error())

def have_space(blob_size, availible_server_space):
    return blob_size <= availible_server_space

def get_error():
    return binary_data_pb2.Error(has_occured=True, description="Not enough space to store blob")

def get_expiration_time():
    # Assume the expiration time is fixed
    expiration_time = Timestamp()
    expiration_time.FromDatetime(datetime(day=1,month=2,year=2019) + timedelta(days=365))
    return binary_data_pb2.ExpirationTime(time=expiration_time)

def update_expiration_time(time):
    expiration_time_dt = Timestamp.ToDatetime(time.time)
    expiration_time_dt = expiration_time_dt + timedelta(minutes=10)
    expiration_time = Timestamp()
    expiration_time.FromDatetime(expiration_time_dt)
    return binary_data_pb2.ExpirationTime(time=expiration_time)

def download_blob(filename, blob_id):
    """
    Returns None if no blob with the given id is found.
    """
    try:
        payload = read_blob_payload(filename, blob_id)
    except Exception:
        return None

    if payload is None:
        return None
    else:
        return binary_data_pb2.Blob(id=blob_id, payload=payload)

def delete_blob(filename, blob_id):
    try:
        remove_blob(filename, blob_id)
        error = binary_data_pb2.Error(has_occured=False, description="")
    except BlobNotFoundException as e:
        error = binary_data_pb2.Error(has_occured=False, description=str(e))
    except Exception as e:
        error = error = binary_data_pb2.Error(has_occured=True, description=str(e))

    return error

def remove_blob(filename, blob_id):
    try:
        remove_by_key_db(filename, str(blob_id.id))
    except KeyError:
        raise BlobNotFoundException("No blob with this id is saved")

def save_chunk(filename, chunk):
    write_chunk(filename, chunk)
    expiration_time = update_expiration_time(get_expiration_time())
    return binary_data_pb2.Response(valid_until=expiration_time)

def write_chunk(filename, chunk):
    data = read_db(filename)
    index = chunk.index
    payload_as_string = chunk.payload.decode("utf-8")
    blob_id = str(chunk.blob_id.id)
    try:
        data[blob_id]
    except KeyError:
        data[blob_id] = {}
    data[blob_id][index] = payload_as_string
    write_db(filename, data)

def read_chunk_payload(filename, blob_id, index):
    """
    Returns None if no blob with the given id and index is found.
    """
    try:
        data = read_db(filename)
        blob = data[str(blob_id.id)]
        payload_as_string = blob[str(index)]
        payload_as_bytes = payload_as_string.encode("utf-8")
        return payload_as_bytes
    except KeyError:
        return None

def read_db(filename):
    with open(filename) as fp:
        data = json.load(fp)
    return data

def write_db(filename, data):
    with open(filename, 'w') as fp:
        json.dump(data, fp)

def remove_by_key_db(filename, key):
    data = read_db(filename)
    del data[key]
    write_db(filename, data)

class BlobNotFoundException(Exception):
    pass

class FileServerServicer(binary_data_pb2_grpc.FileServerServicer):
    """Interfaces exported by the server.
    """
    def __init__(self, availible_server_space, database_filename):
        # self._DATABASE_FILENAME = 'binary_data_db.json'
        self._DATABASE_FILENAME = database_filename
        self._AVAILIBLE_SERVER_SPACE = availible_server_space

    def ValidateFileServer(self, request, context):
        """Checks if we can create a Blob specified by BlobSpec on the FileServer
        and returns the ExpirationTime until which the Blob is valid. Returns an
        Error if there is not enough space.
        """
        blob_spec = request
        response = can_create_blob(blob_spec, self._AVAILIBLE_SERVER_SPACE)
        return response

    def Save(self, request, context):
        """Saves a Chunk to the server and returns the updated ExpirationTime
        Returns an Error if there if it fails for any reason.
        """
        chunk = request
        response = save_chunk(self._DATABASE_FILENAME, chunk)
        return response

    def Download(self, request, context):
        """Downloads a Chunk from the server specified by the ChunkSpec returns
        the Payload and the updated ExpirationTime
        """
        # TODO
        return


    def Delete(self, request, context):
        """Deletes the Blob associated with BlobId and returns an Error object
        containing a description of the error that occured, or an empty
        description if the deletion was a success.
        """
        blob_id = request
        error = delete_blob(self._DATABASE_FILENAME, blob_id)
        return error


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    binary_data_pb2_grpc.add_FileServerServicer_to_server(
        FileServerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            print("\nServer is ready...")
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
