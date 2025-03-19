import lz4.block
import sqlite3

class db_read:
    def __init__(self, save_file):
        self.sqlite_db = save_file
        self.connection = sqlite3.connect(save_file)

    def get_entries(self, table):
        with self.connection as conn:
            cursor = conn.execute(f"SELECT * FROM {table}")
            game_objects = {}
            row_count = len(cursor.fetchall())

            # Get column names
            cursor = conn.execute(f"SELECT * FROM {table}")
            cursor.row_factory = sqlite3.Row
            row = cursor.fetchone()
            names = row.keys()
            cols={}
            i = 0
            for name in names:
                cols[name]=i
                i += 1

            cursor = conn.execute(f"SELECT * FROM {table}")
            i = 0
            for row in cursor:
                i += 1
                try:
                    self.progress = (100 / row_count) * i
                except:
                    self.progress = 0

                game_objectdata = {}
                for name in cols:
                    game_objectdata.update({name:row[cols[name]]})

                game_objects[row[cols['actor_serial']]] = game_objectdata
        return game_objects
    def output_to_bin(self, file, data):
        with open(file, "wb") as f:
            f.write(data)

    def output_to_json(self, file, object):
        #binary_data = json.dumps(object, indent=4).encode("utf-8")
        with open(file, "w") as f:
            for i in object:
                f.write(f"'{i}':'{object[i]}'\n")

def clean_directory(directory, extension=False):
    import os

    # Iterate through the files and delete the ones with the specified extension
    for filename in os.listdir(directory):
        if extension:
            if filename.endswith(extension):  # Check if file ends with the extension
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    print(f'Removing {file_path}')
                    os.remove(file_path)
        else:
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                print(f'Removing {file_path}')
                os.remove(file_path)

#db = 'C:/Users/Games/Downloads/soulmask - world.db_20250213_222248/world.db'
db = 'Z:/SMServer/WS/Saved/Worlds/Dedicated/Level01_Main/world.db'

filepath = './output/'
clean_directory(filepath)

test = db_read(db)
data = test.get_entries('actor_table')

for i in data:
    file = data[i]['actor_serial']
    binary = data[i].pop("actor_data", None)
    compression_header = b'\x02\x00\x00\x00'
    if binary[:4] == compression_header:
        decompressed_binary = lz4.block.decompress(binary[4:])
    else:
        print(f'{file} is not compressed')
        decompressed_binary=binary
    data[i]['compressed'] = len(binary)
    data[i]['decompressed'] = len(decompressed_binary)
    test.output_to_bin(f'{filepath}/{file}.bin',decompressed_binary)
    test.output_to_json(f'{filepath}/{file}.json',data[i])
