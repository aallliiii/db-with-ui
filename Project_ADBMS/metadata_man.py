# import json
# import os

# class MetadataManager:
#     def __init__(self, db_name):
#         self.db_name = db_name
#         self.db_path = f"databases/{db_name}"
#         self.metadata_file = f"{self.db_path}/metadata.json"
        
#         # Create database directory if it doesn't exist
#         os.makedirs(self.db_path, exist_ok=True)

#         if os.path.exists(self.metadata_file):
#             with open(self.metadata_file, "r") as f:
#                 self.metadata = json.load(f)
#         else:
#             self.metadata = {}

#     def save_metadata(self):
#         """Save metadata to the database-specific metadata file."""
#         with open(self.metadata_file, "w") as f:
#             json.dump(self.metadata, f, indent=4)

#     def create_table(self, table_name, columns, primary_key, foreign_keys=None):
#         if table_name in self.metadata:
#             raise Exception(f"Table {table_name} already exists!")

#         self.metadata[table_name] = {
#             "columns": columns,
#             "primary_key": primary_key,
#             "indexes": [primary_key],
#             "foreign_keys": foreign_keys or {}
#         }
#         self.save_metadata()
#         return True

#     def get_table_schema(self, table_name):
#         return self.metadata.get(table_name, None)

#     def delete_table(self, table_name):
#         if table_name not in self.metadata:
#             raise Exception(f"Table {table_name} does not exist!")
#         del self.metadata[table_name]
#         self.save_metadata()
#         return True

import json
import os

class MetadataManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db_path = f"databases/{db_name}"
        
        self.metadata_file = f"{self.db_path}/metadata.json"
        
        # Create database directory if it doesn't exist
        os.makedirs(self.db_path, exist_ok=True)

        # Load existing metadata or initialize empty
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def save_metadata(self):
        """Save metadata to the database-specific metadata file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=4)

    def create_table(self, table_name, columns, primary_key, foreign_keys=None):
        """
        columns: dict[column_name] = type
        primary_key: str
        foreign_keys: dict[column_name] = (referenced_table, referenced_column)
        """
        if table_name in self.metadata:
            raise Exception(f"Table '{table_name}' already exists!")

        self.metadata[table_name] = {
            "columns": columns,  # dict with types
            "primary_key": primary_key,
            "indexes": [primary_key],
            "foreign_keys": foreign_keys or {}
        }
        self.save_metadata()
        return True

    def get_table_schema(self, table_name):
        """Retrieve the schema (columns, primary key, foreign keys) of a table."""
        return self.metadata.get(table_name, None)

    def delete_table(self, table_name):
        """Delete a table from metadata."""
        if table_name not in self.metadata:
            raise Exception(f"Table '{table_name}' does not exist!")
        del self.metadata[table_name]
        self.save_metadata()
        return True
