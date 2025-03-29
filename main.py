import config
from config import *

from Properties.BoolProperty import BoolProperty
from Properties.ByteProperty import ByteProperty
from Properties.DoubleProperty import DoubleProperty
from Properties.FloatProperty import FloatProperty
from Properties.IntProperty import IntProperty
from Properties.Int64Property import Int64Property

from Properties.EnumProperty import EnumProperty
from Properties.NameProperty import NameProperty
from Properties.StrProperty import StrProperty
from Properties.TextProperty import TextProperty

from Properties.ArrayProperty import ArrayProperty
from Properties.MapProperty import MapProperty
from Properties.ObjectProperty import ObjectProperty
from Properties.SetProperty import SetProperty
from Properties.SoftObjectProperty import SoftObjectProperty
from Properties.StructProperty import StructProperty

from Properties.FileEndProperty import FileEndProperty
from Properties.NoneProperty import NoneProperty


# from Properties.DateTimeProperty import DateTimeProperty
# from Properties.GuidProperty import GuidProperty
# from Properties.LinearColorProperty import LinearColorProperty
# from Properties.QuatProperty import QuatProperty
# from Properties.RotatorProperty import RotatorProperty
# from Properties.VectorProperty import VectorProperty


import lz4.block
import os
import sqlite3
import uuid
import inspect
from struct import pack, unpack
from datetime import datetime
import time
import json


def where_was_i_called():
    stack = inspect.stack()
    caller_frame = stack[2]  # Get the frame of the caller
    filename = os.path.basename(caller_frame.filename)
    line_number = caller_frame.lineno
    return f"Called from {filename}, line {line_number}"


class db_read:
    def __init__(self, save_file):
        self.sqlite_db = save_file
        self.connection = sqlite3.connect(self.sqlite_db)
        logger.info(f"Opened connection to db file {self.sqlite_db}")

    def get_entries(self, table):
        logger.debug(f'Working on table "{table}" in "{self.sqlite_db}"')
        with self.connection as conn:
            # Get row and column info
            cursor = conn.execute(f"SELECT COUNT(*), * FROM {table} LIMIT 1")
            row_count = cursor.fetchone()[0]
            column_names = [col[0] for col in cursor.description[1:]]  # Skip COUNT(*)
            logger.debug(
                f"Table has {row_count} rows and {len(column_names)} columns {column_names}"
            )
            cursor = conn.execute(f"SELECT * FROM {table}")
            game_objects = {}
            try:
                for row in cursor:
                    actor_serial = row[column_names.index("actor_serial")]
                    # Log the actor_serial before processing
                    logger.debug(f"Processing entry ID: {actor_serial}")
                    game_objectdata = {
                        name: row[column_names.index(name)] for name in column_names
                    }
                    # Log the game object data after it is created
                    # logger.debug(f"Processed game object data for {actor_serial}: {game_objectdata}")
                    game_objects[actor_serial] = game_objectdata
                logger.info(f"Total game objects processed: {len(game_objects)}")
            except Exception as e:
                logger.error(f"Error processing rows: {e}")
        return game_objects

    def decompress(self, compressed_data):
        try:
            decompressed_data = lz4.block.decompress(compressed_data)
            # logger.debug(f'compressed size:{len(compressed_data)}, decompressed size:{len(decompressed_data)}')
            return decompressed_data
        except Exception as e:
            logger.error(f"Decompression failed : {e}")
            raise Exception(f"Decompression failed : {e}")

    def decompress_all(self, object, label):
        binary_header = b"\x02\x00\x00\x00"
        compressed_size = 0
        decompressed_size = 0
        for entry in object:
            if object[entry][label][:4] == binary_header:
                # Add compressed size to the list
                compressed_size += len(object[entry][label])
                # logger.debug(f'Decompressing : {object[entry][label][4:]}')
                decompressed_data = self.decompress(object[entry][label][4:])
                object[entry][label] = decompressed_data
                # Add decompressed size to the list
                decompressed_size += len(object[entry][label])
            else:
                logger.debug(f"Skipping : {object[entry][label][4:]}")
        logger.info(
            f"inflated database info from {compressed_size/(1024 * 1024)} MB to {decompressed_size/(1024 * 1024)} MB"
        )
        # return the same object with inflated data
        return object


class binary_read:
    def __init__(self, file_array_buffer=None):
        self.offset = 0
        self.file_array_buffer = file_array_buffer
        self.file_size = len(file_array_buffer)
        self.indents = 0
        logger.debug(f"Created a new binary reader with {self.file_size} bytes")
        if DATA_DUMP:
            self.dump_to_disk(file_array_buffer)

    def expect_NoneType(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        try:
            position = self.offset
            result = self.read_string()
            if result == "None":
                return True
            else:
                self.offset = position
                logger.warning(
                    f'Unexpected data found: {self.read_bytes(20).hex(" ",1)}'
                )
                return False
        except Exception as e:
            logger.error(f"{e}")

    def expect(self, expected_data):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        try:
            position = self.offset
            result = self.read_bytes(len(expected_data))
            if result == expected_data:
                return True
            else:
                self.offset = position
                logger.warning(
                    f'Unexpected data found. Looking for {expected_data}, found: {self.read_bytes(20).hex(" ",1)}'
                )
                return False
        except Exception as e:
            logger.error(f"{e}")

    def find_next_property(self):
        found = False
        prop = "EOF"
        while not found and self.offset < self.file_size:
            current_byte = self.offset
            if self.read_bytes(8) == b"Property":
                self.offset = current_byte - 1
                while self.read_bytes(1) != b"\x00":
                    self.offset -= 2
                found = True
                self.offset -= 4
                prop = self.read_string()
            else:
                self.offset = current_byte + 1
        return prop

    def peek(self, count_forward, count_back=False):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        reset = self.offset
        back = b""
        if count_back:
            self.offset -= count_back
            back = self.file_array_buffer[self.offset : self.offset + count_back]
            self.offset = reset
        current = self.file_array_buffer[self.offset : self.offset + 1]
        self.offset = reset + 1
        forward = self.file_array_buffer[self.offset : self.offset + count_forward - 1]
        self.offset = reset
        if count_back:
            return f"{self.offset}:{back.hex(' ', 1)} \x1b[18;32m{current.hex()}\x1b[0m {forward.hex(' ', 1)}"
        else:
            return f"\x1b[18;32m{current.hex()}\x1b[0m {forward.hex(' ', 1)}"

    def has_finished(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        if self.offset > self.file_size:
            logger.error(
                f"Overread the buffer, size:{self.file_size}, offset:{self.offset}"
            )
            return self.offset == self.file_size
        else:
            return self.offset == self.file_size

    def read_bytes(self, count, quiet=False):
        if not quiet:
            logger.debug(
                f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
            )
        result = self.file_array_buffer[self.offset : self.offset + count]
        self.offset += count
        # where_was_i_called()
        # logger.debug(f'{result}')
        return result

    def read_int16(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        value = unpack("<h", self.file_array_buffer[self.offset : self.offset + 2])[0]
        self.offset += 2
        logger.debug(f"{value}")
        return value

    def read_int32(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        value = unpack("<i", self.file_array_buffer[self.offset : self.offset + 4])[0]
        self.offset += 4
        logger.debug(f"{value}")
        return value

    def read_int64(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        value = unpack("<q", self.file_array_buffer[self.offset : self.offset + 8])[0]
        self.offset += 8
        logger.debug(f"{value}")
        return value

    def read_uint32(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        value = unpack("<I", self.file_array_buffer[self.offset : self.offset + 4])[0]
        self.offset += 4
        logger.debug(f"{value}")
        return value

    def read_float32(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        value = unpack("<f", self.file_array_buffer[self.offset : self.offset + 4])[0]
        self.offset += 4
        logger.debug(f"{value}")
        return value

    def read_double(self) -> float:
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        value = unpack("<d", self.file_array_buffer[self.offset : self.offset + 8])[0]
        self.offset += 8
        logger.debug(f"{value}")
        return value

    def read_string(self):
        start_pos = self.offset
        try:
            length = self.read_int32()
            raw_bytes = self.file_array_buffer[
                self.offset : self.offset + length - 1
            ]  # Exclude the null terminator
            result = raw_bytes.decode("utf-8")
            logger.debug(
                f"position:{self.offset} - {inspect.currentframe().f_code.co_name}"
            )
            self.offset += length
            logger.debug(f"{result}")
            return result
        except:
            self.offset = start_pos
            peek = self.read_bytes(30)
            raise Exception(f"Unknown data: {start_pos}:{peek.hex(' ',1)} : {peek}")

    def read_uuid_as_string(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        result = self.read_uuid().hex
        logger.debug(f"{result}")
        return result

    def read_uuid(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        result = uuid.UUID(bytes=self.read_bytes(16))
        logger.debug(f"{result}")
        return result

    def read_string_special(self):
        return self.read_string()
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        length = self.read_int32()
        wide = False
        encoding = "utf-8"
        null = 1
        logger.warning(f"length:{length}")
        if length < 0:
            length = abs(length) * 2
            wide = True
            encoding = "utf-16-le"
            null = 2
        raw_bytes = self.file_array_buffer[
            self.offset : self.offset + length - null
        ]  # Exclude the null terminator
        result = raw_bytes.decode(encoding)
        self.offset += length
        logger.debug(f"{result}, {wide}")
        return result, wide

    def read_boolean(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        result = bool(self.file_array_buffer[self.offset])
        self.offset += 1
        logger.debug(f"{result}")
        return result

    def read_date_time(self):
        logger.debug(
            f"{self.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}:{where_was_i_called()}"
        )
        ticks = int.from_bytes(
            self.file_array_buffer[self.offset : self.offset + 8], "little"
        )
        self.offset += 8
        try:
            calculated_time = datetime.utcfromtimestamp(
                (ticks // 10000 - 62135596800000) / 1000.0
            )
            calculated_time = calculated_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        except:
            calculated_time = ticks
        logger.debug(f"{calculated_time}")

        return calculated_time

    def read_property(self):

        if self.offset + len(FileEndProperty.bytes) == len(self.file_array_buffer):
            assumed_file_end = self.file_array_buffer[
                self.offset : self.offset + len(FileEndProperty.bytes)
            ]

            if assumed_file_end == FileEndProperty.bytes:
                self.offset += len(FileEndProperty.bytes)
                return FileEndProperty()
        property_name = self.read_string()
        logger.debug(f"New Property name:{property_name}")
        if property_name == "None":
            return NoneProperty()

        # Read property type
        property_type = self.read_string()
        logger.debug(f"New Property type:{property_type}")

        if property_type == "BoolProperty":
            value = BoolProperty(property_name, self)
        elif property_type == "IntProperty":
            value = IntProperty(property_name, self)
        elif property_type == "Int64Property":
            value = Int64Property(property_name, self)
        elif property_type == "DoubleProperty":
            value = DoubleProperty(property_name, self)
        elif property_type == "FloatProperty":
            value = FloatProperty(property_name, self)
        elif property_type == "EnumProperty":
            value = EnumProperty(property_name, self)
        elif property_type == "StructProperty":
            value = StructProperty(property_name, self)
        elif property_type == "ByteProperty":
            value = ByteProperty(property_name, self)
        elif property_type == "StrProperty":
            value = StrProperty(property_name, self)
        elif property_type == "TextProperty":
            value = TextProperty(property_name, self)
        elif property_type == "NameProperty":
            value = NameProperty(property_name, self)
        elif property_type == "SetProperty":
            value = SetProperty(property_name, self)
        elif property_type == "ArrayProperty":
            self.indents += 1
            value = ArrayProperty(property_name, self)
            self.indents -= 1
        elif property_type == "ObjectProperty":
            value = ObjectProperty(property_name, self)
        elif property_type == "SoftObjectProperty":
            value = SoftObjectProperty(property_name, self)
        elif property_type == "MapProperty":
            value = MapProperty(property_name, self)
        else:
            logger.critical(self.peek(50))
            raise Exception(
                f"Unknown property type: {property_type} at position:{self.offset-len(property_type)-4}"
            )
        logger.debug(f"Inside {self.indents} arrays")
        return value

    def deserialize(self):
        logger.debug(
            f"position:{self.offset} - {inspect.currentframe().f_code.co_name}"
        )
        num_entries = self.read_int32()
        logger.debug(f"New deserialization. ecapsulated properties: {num_entries}")

        deserialized_data = []
        for _ in range(num_entries):
            deserialized_data.append(self.read_property())
            self.read_bytes(4)  # padding
        return deserialized_data

    def dump_to_disk(self, data, file_path="."):
        filename = f"{file_path}/current_object.bin"
        if os.path.exists(f"{file_path}/previous_object.bin"):
            os.replace(
                f"{file_path}/previous_object.bin", f"{file_path}/back2_object.bin"
            )  # Overwrites new_filename if it exists
        if os.path.exists(filename):
            os.replace(
                filename, f"{file_path}/previous_object.bin"
            )  # Overwrites new_filename if it exists
        with open(filename, "wb") as f:
            logger.debug(f"Creating binary file {file_path}current_object.bin")
            f.write(data)

    def __repr__(self):
        return "{}, {}".format(self.offset, self.file_size)


def clean_directory(directory, extension=False):
    logger.info(f"Cleaning path {directory}")
    for filename in os.listdir(directory):
        # Iterate through the files in the specified path and delete the ones with the specified extension
        if extension:
            if filename.endswith(extension):  # Check if file ends with the extension
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    logger.debug(f"Deleting file : {file_path}")
                    os.remove(file_path)
        # Iterate through the files in the specified path and delete
        else:
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                logger.debug(f"Deleting file : {file_path}")
                os.remove(file_path)


def create_as_files(directory, data):
    clean_directory(directory)
    for entry in data:
        file_path = data[entry]["actor_serial"]
        with open(f"{directory}{file_path}.json", "w") as f:
            logger.debug(f"Creating json file {directory}{file_path}.json")
            for key in data[entry]:
                if key != "actor_data":
                    f.write(f"'{key}':'{data[entry][key]}'\n")
        with open(f"{directory}{file_path}.bin", "wb") as f:
            logger.debug(f"Creating binary file {directory}{file_path}.bin")
            f.write(data[entry]["actor_data"])


def pp(object, indent=0):
    if type(object) == dict:
        for key, value in object.items():
            print("\t" * indent + str(key))
            if isinstance(value, dict):
                pp(value, indent + 1)
            else:
                print("\t" * (indent + 1) + str(value))
    elif type(object) == list:
        for value in object:
            print("\t" * indent + str(value))
            if isinstance(object[value], dict):
                pp(object[value], indent + 1)
            else:
                print("\t" * (indent + 1) + str(object[value]))
    else:
        print("\t" * (indent + 1) + str(object))


if __name__ == "__main__":

    DATA_DUMP = False
    # DATA_DUMP = True

    # Test Files
    dbfile = "./dbfiles/MyServer.db"
    dbfile = "./dbfiles/JimsServer.db"

    # Load the database
    logger.info(f"Begining database read")
    database = db_read(dbfile)

    # Extract all info from the databse
    logger.info(f"Begining database extraction")
    db_objects = database.get_entries("actor_table")

    # Decompress the data
    logger.info(f"Begining data decompression")
    db_objects = database.decompress_all(db_objects, "actor_data")

    # create files in output directory
    if DATA_DUMP:
        logger.info(f"Begining output of all found data")
        create_as_files("./output/", db_objects)

    logger.info(f"Begining insertion of serialized data")
    serialized_data = {}
    deserialized_data = {}

    start_time = time.time()
    for i in db_objects:
        if i < 4:  #  38060:
            if db_objects[i]["actor_name"] != "GAME_SETTINGS":
                logger.info(f'Deserializing entry ID {i}:{db_objects[i]["actor_name"]}')
                serialized_data.update({i: binary_read(db_objects[i]["actor_data"])})
                logger.error(f"Current DB Record : {i}.bin")
                deserialized_data.update({i: serialized_data[i].deserialize()})

            logger.info(
                f"Running for {time.time() - start_time} seconds, STRUCT_INDENT_COUNTER:{STRUCT_INDENT_COUNTER}"
            )
            time.sleep(0.1)
