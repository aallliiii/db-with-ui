import pandas as pd
import os
from metadata_man import MetadataManager

class FileStorageManager:
    def __init__(self, table_name, columns=None, primary_key=None, foreign_keys=None):
        self.table_name = table_name
        self.file_path = f"{table_name}.csv"
        self.metadata_manager = MetadataManager()

        table_schema = self.metadata_manager.get_table_schema(table_name)

        if table_schema:
            self.columns = table_schema["columns"]
            self.primary_key = table_schema["primary_key"]
            self.foreign_keys = table_schema.get("foreign_keys", {})
        else:
            if not columns or not primary_key:
                raise Exception("New tables require columns and a primary key.")
            self.columns = columns
            self.primary_key = primary_key
            self.foreign_keys = foreign_keys or {}
            self.metadata_manager.create_table(table_name, columns, primary_key, foreign_keys)

        if not os.path.exists(self.file_path):
            self.create_table_file()

    def create_table_file(self):
        df = pd.DataFrame(columns=self.columns)
        df.to_csv(self.file_path, index=False)

    def insert_record(self, record):
        df = pd.read_csv(self.file_path)
        new_entry = dict(zip(self.columns, record))

        for column, (ref_table, ref_column) in self.foreign_keys.items():
            if str(new_entry[column]) not in pd.read_csv(f"{ref_table}.csv")[ref_column].astype(str).values:
                raise Exception(f"Foreign key constraint failed: {column} references {ref_table}({ref_column})")

        df.loc[len(df)] = record
        df.to_csv(self.file_path, index=False)

    def select_records(self, search_column=None, search_value=None):
        df = pd.read_csv(self.file_path)
        if search_column:
            return df[df[search_column] == search_value]
        return df

    def update_record(self, search_column, search_value, update_column, update_value):
        df = pd.read_csv(self.file_path)
        
        if update_column in self.foreign_keys:
            ref_table, ref_column = self.foreign_keys[update_column]
            if str(update_value) not in pd.read_csv(f"{ref_table}.csv")[ref_column].astype(str).values:
                raise Exception(f"Foreign key constraint failed: {update_column} references {ref_table}({ref_column})")
        
        df.loc[df[search_column] == search_value, update_column] = update_value
        df.to_csv(self.file_path, index=False)

    def delete_record(self, search_column, search_value):
        df = pd.read_csv(self.file_path)

        if search_column not in df.columns:
            raise KeyError(f"Column '{search_column}' does not exist in {self.file_path}")

        # Check if this record is referenced in another table
        for table, schema in self.metadata_manager.metadata.items():
            for column, (ref_table, ref_column) in schema.get("foreign_keys", {}).items():
                if ref_table == self.table_name:
                    ref_df = pd.read_csv(f"{table}.csv")
                    
                    # Ensure ref_column exists
                    if ref_column not in ref_df.columns:
                        raise KeyError(f"Column '{ref_column}' does not exist in {table}.csv")

                    if search_value in ref_df[ref_column].astype(str).values:
                        raise Exception(f"Cannot delete {self.table_name} record: It is referenced in {table}({column})")

        df = df[df[search_column] != search_value]
        df.to_csv(self.file_path, index=False)

    
    def delete_table(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        self.metadata_manager.delete_table(self.table_name)


import json
import os

METADATA_FILE = "metadata.json"

class MetadataManager:
    def __init__(self):
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "r") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def save_metadata(self):
        with open(METADATA_FILE, "w") as f:
            json.dump(self.metadata, f, indent=4)

    def create_table(self, table_name, columns, primary_key, foreign_keys=None):
        if table_name in self.metadata:
            raise Exception(f"Table {table_name} already exists!")

        self.metadata[table_name] = {
            "columns": columns,
            "primary_key": primary_key,
            "indexes": [primary_key],
            "foreign_keys": foreign_keys or {}
        }
        self.save_metadata()
        return True

    def get_table_schema(self, table_name):
        return self.metadata.get(table_name, None)

    def delete_table(self, table_name):
        if table_name not in self.metadata:
            raise Exception(f"Table {table_name} does not exist!")
        del self.metadata[table_name]
        self.save_metadata()
        return True
