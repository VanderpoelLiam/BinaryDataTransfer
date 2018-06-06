import time
from datetime import datetime, timedelta

import binary_data_pb2
import binary_data_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from resources_files import read_db, write_db, remove_by_key_db


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def can_create_blob(blob_spec, available_server_space):
    if have_space(blob_spec.size, available_server_space):
        expiration_time = get_expiration_time()
        return binary_data_pb2.Response(valid_until=expiration_time)
    else:
        return binary_data_pb2.Response(error=get_not_enough_space_error())


def have_space(blob_size, available_server_space):
    return blob_size <= available_server_space


def get_not_enough_space_error():
    return binary_data_pb2.Error(has_occured=True,
                                 description="Not enough space to store blob")


def get_expiration_time():
    # Assume the expiration time is fixed
    expiration_time = Timestamp()
    expiration_time.FromDatetime(datetime(day=1, month=2, year=2019) +
                                 timedelta(days=365))
    return binary_data_pb2.ExpirationTime(time=expiration_time)


def update_expiration_time(time):
    expiration_time_dt = Timestamp.ToDatetime(time.time)
    expiration_time_dt = expiration_time_dt + timedelta(minutes=10)
    expiration_time = Timestamp()
    expiration_time.FromDatetime(expiration_time_dt)
    return binary_data_pb2.ExpirationTime(time=expiration_time)


def download_chunk(filename, chunk_spec):
    try:
        payload = read_chunk_payload(filename, chunk_spec.blob_id,
                                     chunk_spec.index)
        response = binary_data_pb2.Response(payload=payload,
                                            valid_until=get_expiration_time())
    except Exception as e:
        error = binary_data_pb2.Error(has_occured=True,
                                      description="Issue downloading chunk")
        response = binary_data_pb2.Response(error=error)

    return response


def delete_blob(filename, blob_id):
    try:
        remove_blob(filename, blob_id)
        error = binary_data_pb2.Error(has_occured=False, description="")
    except BlobNotFoundException as e:
        error = binary_data_pb2.Error(has_occured=False, description=str(e))
    except Exception as e:
        error = binary_data_pb2.Error(has_occured=True, description=str(e))

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
    payload = chunk.payload
    payload_as_string = payload.decode("latin1")
    blob_id = str(chunk.blob_id.id)
    try:
        data[blob_id]
    except KeyError:
        data[blob_id] = {}
    data[blob_id][index] = payload_as_string
    write_db(filename, data)


def read_chunk_payload(filename, blob_id, index):
    data = read_db(filename)
    blob = data[str(blob_id.id)]
    payload_as_string = blob[str(index)]
    payload_as_bytes = payload_as_string.encode("latin1")
    return payload_as_bytes


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
        """Downloads the Chunk specified by ChunkSpec from the server and returns
        the associated Payload and ExpirationTime in the response. Returns an
        Error if it fails for any reason.
        """
        chunk_spec = request
        response = download_chunk(self._DATABASE_FILENAME, chunk_spec)
        return response

    def Delete(self, request, context):
        """Deletes the Blob associated with BlobId and returns an Error object
        containing a description of the error that occured, or an empty
        description if the deletion was a success.
        """
        blob_id = request
        error = delete_blob(self._DATABASE_FILENAME, blob_id)
        return error
