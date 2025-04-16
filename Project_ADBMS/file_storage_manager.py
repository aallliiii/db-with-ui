# import pandas as pd
# import os
# from metadata_man import MetadataManager

# class FileStorageManager:
#     def __init__(self, table_name, columns=None, primary_key=None, foreign_keys=None):
#         self.table_name = table_name
#         self.file_path = f"{table_name}.csv"
#         self.metadata_manager = MetadataManager()

#         table_schema = self.metadata_manager.get_table_schema(table_name)

#         if table_schema:
#             self.columns = table_schema["columns"]
#             self.primary_key = table_schema["primary_key"]
#             self.foreign_keys = table_schema.get("foreign_keys", {})
#         else:
#             if not columns or not primary_key:
#                 raise Exception("New tables require columns and a primary key.")
#             self.columns = columns
#             self.primary_key = primary_key
#             self.foreign_keys = foreign_keys or {}
#             self.metadata_manager.create_table(table_name, columns, primary_key, foreign_keys)

#         if not os.path.exists(self.file_path):
#             self.create_table_file()

#     def create_table_file(self):
#         df = pd.DataFrame(columns=self.columns)
#         df.to_csv(self.file_path, index=False)

#     def get_next_primary_key(self, df):
#         """ Auto-generates the next primary key value. """
#         if df.empty:
#             return 1  # Start primary key from 1
#         return df[self.primary_key].max() + 1

#     def insert_record(self, record):
#         df = pd.read_csv(self.file_path)

#         # If the primary key is missing, auto-generate it
#         if len(record) == len(self.columns) - 1:  # If user_id is missing
#             new_id = self.get_next_primary_key(df)
#             record.insert(0, new_id)  # Insert new primary key at index 0

#         # Ensure record has the correct number of values
#         if len(record) != len(self.columns):
#             raise Exception(f"Incorrect number of values. Expected {len(self.columns)}, got {len(record)}.")

#         # Convert record into dictionary format
#         new_entry = dict(zip(self.columns, record))

#         # Ensure primary key uniqueness
#         if str(new_entry[self.primary_key]) in df[self.primary_key].astype(str).values:
#             raise Exception(f"Primary key '{new_entry[self.primary_key]}' must be unique.")

#         # Validate foreign key constraints
#         for column, (ref_table, ref_column) in self.foreign_keys.items():
#             ref_df = pd.read_csv(f"{ref_table}.csv")
#             if str(new_entry[column]) not in ref_df[ref_column].astype(str).values:
#                 raise Exception(f"Foreign key constraint failed: {column} references {ref_table}({ref_column})")

#         # Append new entry using pd.concat()
#         df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
#         df.to_csv(self.file_path, index=False)




#     def select_records(self, search_column=None, search_value=None):
#         df = pd.read_csv(self.file_path)
#         if search_column:
#             if search_column not in df.columns:
#                 raise Exception(f"Column '{search_column}' does not exist in {self.table_name}.")
#             return df[df[search_column] == search_value]
#         return df

#     def update_record(self, search_column, search_value, update_column, update_value):
#         df = pd.read_csv(self.file_path)

#         if update_column in self.foreign_keys:
#             ref_table, ref_column = self.foreign_keys[update_column]
#             ref_df = pd.read_csv(f"{ref_table}.csv")
#             if str(update_value) not in ref_df[ref_column].astype(str).values:
#                 raise Exception(f"Foreign key constraint failed: {update_column} references {ref_table}({ref_column})")

#         if search_column not in df.columns:
#             raise Exception(f"Column '{search_column}' does not exist in {self.table_name}.")

#         df.loc[df[search_column] == search_value, update_column] = update_value
#         df.to_csv(self.file_path, index=False)

#     def delete_record(self, search_column, search_value):
#         df = pd.read_csv(self.file_path)

#         if search_column not in df.columns:
#             raise KeyError(f"Column '{search_column}' does not exist in {self.file_path}")

#         # Check if this record is referenced in another table
#         for table, schema in self.metadata_manager.metadata.items():
#             for column, (ref_table, ref_column) in schema.get("foreign_keys", {}).items():
#                 if ref_table == self.table_name:  # If this table is referenced as a foreign key
#                     ref_df = pd.read_csv(f"{table}.csv")

#                     # Ensure ref_column exists
#                     if ref_column not in ref_df.columns:
#                         raise KeyError(f"Column '{ref_column}' does not exist in {table}.csv")

#                     # If there are references, delete those records as well (CASCADE DELETE)
#                     ref_df = ref_df[ref_df[ref_column] != search_value]
#                     ref_df.to_csv(f"{table}.csv", index=False)  # Save the updated referenced table

#         # Delete the main record
#         df = df[df[search_column] != search_value]
#         df.to_csv(self.file_path, index=False)  # Save the updated table


import csv
import pandas as pd
import os
from .metadata_man import MetadataManager


# class FileStorageManager:
#     def __init__(self, db_name, table_name,Index_manger, columns=None, primary_key=None, foreign_keys=None):
#         self.db_name = db_name
#         self.table_name = table_name
#         self.index_manager=Index_manger
#         self.db_path = f"databases/{db_name}"  
#         self.file_path = f"{self.db_path}/{table_name}.csv"
        
        
       
#         os.makedirs(self.db_path, exist_ok=True)

#         self.metadata_manager = MetadataManager(db_name)  
#         table_schema = self.metadata_manager.get_table_schema(table_name)

#         if table_schema:
#             self.columns = table_schema["columns"]
#             self.primary_key = table_schema["primary_key"]
#             self.foreign_keys = table_schema.get("foreign_keys", {})
#         else:
#             if not columns or not primary_key:
#                 raise Exception("New tables require columns and a primary key.")
            
#             self.columns = columns
#             self.primary_key = primary_key
#             self.foreign_keys = foreign_keys or {}

           
#             for fk_column, (ref_table, ref_column) in self.foreign_keys.items():
#                 ref_table_schema = self.metadata_manager.get_table_schema(ref_table)
#                 if not ref_table_schema:
#                     raise Exception(f"Error: Referenced table '{ref_table}' does not exist.")
#                 if ref_column not in ref_table_schema["columns"]:
#                     raise Exception(f"Error: Foreign key column '{ref_column}' does not exist in table '{ref_table}'.")

#             self.metadata_manager.create_table(table_name, columns, primary_key, foreign_keys)

#         if not os.path.exists(self.file_path):
#             self.create_table_file()

class FileStorageManager:
    # def __init__(self, db_name, table_name, index_manager, columns=None, primary_key=None, foreign_keys=None):
    #     self.db_name = db_name
    #     self.table_name = table_name
    #     self.index_manager = index_manager
    #     self.db_path = f"databases/{db_name}"
    #     self.file_path = f"{self.db_path}/{table_name}.csv"
        
    #     os.makedirs(self.db_path, exist_ok=True)

    #     self.metadata_manager = MetadataManager(db_name)  
    #     table_schema = self.metadata_manager.get_table_schema(table_name)

    #     if table_schema:
    #         self.columns = table_schema["columns"]
    #         self.primary_key = table_schema["primary_key"]
    #         self.foreign_keys = table_schema.get("foreign_keys", {})
    #     else:
    #         if not columns or not primary_key:
    #             raise Exception("New tables require columns and a primary key.")
            
    #         self.columns = columns
    #         self.primary_key = primary_key
    #         self.foreign_keys = foreign_keys or {}

    #         for fk_column, (ref_table, ref_column) in self.foreign_keys.items():
    #             ref_table_schema = self.metadata_manager.get_table_schema(ref_table)
    #             if not ref_table_schema:
    #                 raise Exception(f"Error: Referenced table '{ref_table}' does not exist.")
    #             if ref_column not in ref_table_schema["columns"]:
    #                 raise Exception(f"Error: Foreign key column '{ref_column}' does not exist in table '{ref_table}'.")

    #         self.metadata_manager.create_table(table_name, columns, primary_key, foreign_keys)

    #     if not os.path.exists(self.file_path):
    #         self.create_table_file()
    #     else:
    #         # NEW CODE: Validate index on initialization
    #         if not self.validate_index():
    #             print("⚠️ Index out of sync. Rebuilding...")
    #             self.rebuild_index()

    # def __init__(self, db_name, table_name, index_manager, columns=None, primary_key=None, foreign_keys=None):
    #     self.db_name = db_name
    #     self.table_name = table_name
    #     self.index_manager = index_manager
    #     self.db_path = f"databases/{db_name}"
    #     self.file_path = f"{self.db_path}/{table_name}.csv"
        
    #     os.makedirs(self.db_path, exist_ok=True)

    #     self.metadata_manager = MetadataManager(db_name)
    #     table_schema = self.metadata_manager.get_table_schema(table_name)

    #     if table_schema:
    #         self.columns = table_schema["columns"]  # dict: col_name -> type
    #         self.primary_key = table_schema["primary_key"]
    #         self.foreign_keys = table_schema.get("foreign_keys", {})
    #     else:
    #         if not columns or not primary_key:
    #             raise Exception("New tables require columns and a primary key.")
            
    #         self.columns = columns  # dict: col_name -> type
    #         self.primary_key = primary_key
    #         self.foreign_keys = foreign_keys or {}

    #         # Foreign key validation
    #         for fk_column, (ref_table, ref_column) in self.foreign_keys.items():
    #             ref_table_schema = self.metadata_manager.get_table_schema(ref_table)
    #             if not ref_table_schema:
    #                 raise Exception(f"Error: Referenced table '{ref_table}' does not exist.")
    #             if ref_column not in ref_table_schema["columns"]:
    #                 raise Exception(f"Error: Foreign key column '{ref_column}' does not exist in table '{ref_table}'.")

    #         # Create table metadata with typed columns
    #         self.metadata_manager.create_table(
    #             table_name=table_name,
    #             columns=columns,  # dict: col_name -> type
    #             primary_key=primary_key,
    #             foreign_keys=foreign_keys
    #         )

    #     # Create table CSV file if it doesn't exist
    #     if not os.path.exists(self.file_path):
    #         self.create_table_file()
    #     else:
    #         # Validate index on file load
    #         if not self.validate_index():
    #             print("⚠️ Index out of sync. Rebuilding...")
    #             self.rebuild_index()

    def __init__(self, db_name, table_name, index_manager, columns=None, primary_key=None, foreign_keys=None):
        self.db_name = db_name
        self.table_name = table_name
        self.index_manager = index_manager
        self.db_path = f"Project_ADBMS/databases/{db_name}"
        self.file_path = f"{self.db_path}/{table_name}.csv"

        os.makedirs(self.db_path, exist_ok=True)

        self.metadata_manager = MetadataManager(db_name)
        table_schema = self.metadata_manager.get_table_schema(table_name)

        if table_schema:
            self.column_types = table_schema["columns"]                  # dict: column -> type
            self.columns = list(self.column_types.keys())               # ordered column names
            self.primary_key = table_schema["primary_key"]
            self.foreign_keys = table_schema.get("foreign_keys", {})
        else:
            if not columns or not primary_key:
                raise Exception("New tables require columns and a primary key.")

            self.column_types = columns
            self.columns = list(columns.keys())
            self.primary_key = primary_key
            self.foreign_keys = foreign_keys or {}

            # Foreign key validation
            for fk_column, (ref_table, ref_column) in self.foreign_keys.items():
                ref_table_schema = self.metadata_manager.get_table_schema(ref_table)
                if not ref_table_schema:
                    raise Exception(f"Error: Referenced table '{ref_table}' does not exist.")
                if ref_column not in ref_table_schema["columns"]:
                    raise Exception(f"Error: Foreign key column '{ref_column}' does not exist in table '{ref_table}'.")

            self.metadata_manager.create_table(
                table_name=table_name,
                columns=columns,
                primary_key=primary_key,
                foreign_keys=foreign_keys
            )

        if not os.path.exists(self.file_path):
            self.create_table_file()
        else:
            if not self.validate_index():
                print("⚠️ Index out of sync. Rebuilding...")
                self.rebuild_index()



    def validate_index(self):
        """Check if all PKs in file exist in index"""
        if not os.path.exists(self.file_path):
            return True
            
        df = pd.read_csv(self.file_path)
        if df.empty:
            return True
            
        for pk in df[self.primary_key].astype(str):
            if self.index_manager.get_primary_index(self.table_name, pk) is None:
                return False
        return True

    # def rebuild_index(self):
    #     """Force rebuild of the entire primary key index"""
    #     df = pd.read_csv(self.file_path)
    #     self.index_manager.rebuild_primary_index(self.table_name, df, self.primary_key)
    #     print("✅ Primary key index rebuilt successfully")

    def create_table_file(self):
      
        df = pd.DataFrame(columns=self.columns)
        df.to_csv(self.file_path, index=False)


    # def insert_record(self, record):
       
    #     df = pd.read_csv(self.file_path)

        
    #     existing_primary_keys = set(df[self.primary_key].astype(str))

        

    #     if len(record) < len(self.columns):
    #         if self.primary_key in self.columns:
    #             primary_key_idx = self.columns.index(self.primary_key)
    #             new_primary_key = max(df[self.primary_key].dropna().astype(int), default=0) + 1 
    #             record.insert(primary_key_idx, new_primary_key)

    
        
    #     while len(record) < len(self.columns):
    #         record.append(None)  

    #     new_entry = dict(zip(self.columns, record))
    #     primary_key_value = str(new_entry[self.primary_key]) 

        
    #     if primary_key_value in existing_primary_keys:
    #         raise Exception(f"Error: Primary key '{primary_key_value}' already exists!")

    
    #     for column, (ref_table, ref_column) in self.foreign_keys.items():
    #         if new_entry[column] is not None:  
    #             ref_path = f"databases/{self.db_name}/{ref_table}.csv"
    #             if not os.path.exists(ref_path):
    #                 raise Exception(f"Error: Referenced table '{ref_table}' does not exist.")

    #             ref_df = pd.read_csv(ref_path)

               
    #             if str(new_entry[column]) not in ref_df[ref_column].astype(str).values:
    #                 raise Exception(f"Error: Foreign key constraint failed. '{new_entry[column]}' not found in '{ref_table}({ref_column})'.")

       
    #     df.loc[len(df)] = record
    #     df.to_csv(self.file_path, index=False)

    #     print(f"✅ Record inserted successfully into {self.table_name}.")

    #def insert_record(self, record):
    #    """Insert a new record into the table and store primary key in the B+ Tree."""
    #    
    #    # ✅ Step 1: Read the existing table data from CSV
    #    df = pd.read_csv(self.file_path)
#
    #    # ✅ Step 2: Get the set of existing primary keys for uniqueness check
    #    existing_primary_keys = set(df[self.primary_key].astype(str))
#
    #    # ✅ Step 3: Generate a primary key if not provided
    #    if len(record) < len(self.columns):
    #        if self.primary_key in self.columns:
    #            primary_key_idx = self.columns.index(self.primary_key)
    #            new_primary_key = max(df[self.primary_key].dropna().astype(int), default=0) + 1  # Ensures uniqueness
    #            record.insert(primary_key_idx, new_primary_key)
#
    #    # ✅ Step 4: Fill missing columns with None (Handles missing values)
    #    while len(record) < len(self.columns):
    #        record.append(None)
#
    #    # ✅ Step 5: Create a dictionary from the record
    #    new_entry = dict(zip(self.columns, record))
    #    primary_key_value = str(new_entry[self.primary_key])  # Convert primary key to string for consistency
#
    #    # ✅ Step 6: Ensure the primary key is UNIQUE (Check in CSV and B+ Tree)
    #    if primary_key_value in existing_primary_keys or self.index_manager.get_primary_index(primary_key_value) is not None:
    #        raise Exception(f"❌ Error: Primary key '{primary_key_value}' already exists!")
#
    #    # ✅ Step 7: Check Foreign Key Constraints
    #    for column, (ref_table, ref_column) in self.foreign_keys.items():
    #        if new_entry[column] is not None:  # If foreign key column is not empty
    #            ref_path = f"databases/{self.db_name}/{ref_table}.csv"
#
    #            # Check if the referenced table exists
    #            if not os.path.exists(ref_path):
    #                raise Exception(f"❌ Error: Referenced table '{ref_table}' does not exist.")
#
    #            ref_df = pd.read_csv(ref_path)
#
    #            # Check if the foreign key exists in the referenced table
    #            if str(new_entry[column]) not in ref_df[ref_column].astype(str).values:
    #                raise Exception(f"❌ Error: Foreign key constraint failed. '{new_entry[column]}' not found in '{ref_table}({ref_column})'.")
#
    #    # ✅ Step 8: Get the offset where the record will be stored
    #    file_offset = len(df)  # Simulated file offset (row number)
#
    #    # ✅ Step 9: Insert Primary Key & Offset into the B+ Tree
    #    print(self.index_manager.add_primary_index(primary_key_value, file_offset))
#
    #    # ✅ Step 10: Verify if the key was successfully inserted in the B+ Tree
    #    if self.index_manager.get_primary_index(primary_key_value) is None:
    #        raise Exception(f"❌ Error: Failed to store primary key '{primary_key_value}' in B+ Tree!")
#
    #    # ✅ Step 11: Insert the record into the CSV file
    #    df.loc[len(df)] = record
    #    df.to_csv(self.file_path, index=False)
#
    #    print(f"✅ Record inserted successfully into {self.table_name}.")
#

    # def insert_record(self, record):
    #     """Insert a new record into the table with proper offset handling in B+ Tree"""

    #     # Step 1: Validate record length matches columns
    #     if len(record) != len(self.columns):
    #         raise ValueError(f"Record length {len(record)} doesn't match columns {len(self.columns)}")

    #     # Step 2: Read existing data to check constraints
    #     try:
    #         df = pd.read_csv(self.file_path)
    #     except (FileNotFoundError, pd.errors.EmptyDataError):
    #         df = pd.DataFrame(columns=self.columns)

    #     # Step 3: Handle primary key
    #     primary_key_value = str(record[self.columns.index(self.primary_key)])

    #     # Check for duplicate primary key (both in CSV and B+ Tree)
    #     if not df.empty and primary_key_value in df[self.primary_key].astype(str).values:
    #         raise ValueError(f"Primary key {primary_key_value} already exists in table")

    #     if self.index_manager.get_primary_index(self.table_name, primary_key_value) is not None:
    #         raise ValueError(f"Primary key {primary_key_value} already exists in index")

    #     # Step 4: Validate foreign keys
    #     for col, (ref_table, ref_col) in self.foreign_keys.items():
    #         ref_value = str(record[self.columns.index(col)])
    #         if ref_value:  # Only check non-empty foreign keys
    #             ref_path = f"databases/{self.db_name}/{ref_table}.csv"
    #             if not os.path.exists(ref_path):
    #                 raise ValueError(f"Referenced table {ref_table} doesn't exist")

    #             ref_df = pd.read_csv(ref_path)
    #             if ref_value not in ref_df[ref_col].astype(str).values:
    #                 raise ValueError(f"Foreign key violation: {ref_value} not found in {ref_table}.{ref_col}")

    #     # Step 5: Calculate correct file offset
    #     offset = len(df)  # New record will be at this offset position

    #     # Step 6: Insert into B+ Tree index first
    #     try:
    #         self.index_manager.add_primary_index(self.table_name, primary_key_value, offset)
    #     except Exception as e:
    #         raise ValueError(f"Failed to add to index: {str(e)}")

    #     # Step 7: Append record to CSV file
    #     try:
    #         write_header = not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0

    #         with open(self.file_path, 'a', newline='') as f:
    #             writer = csv.writer(f)
    #             if write_header:
    #                 writer.writerow(self.columns)
    #             writer.writerow(record)
    #     except Exception as e:
    #         # Rollback index insertion if file write fails
    #         self.index_manager.delete_primary_index(self.table_name, primary_key_value)
    #         raise IOError(f"Failed to write record: {str(e)}")

    #     print(f"✅ Record inserted successfully. PK: {primary_key_value}, Offset: {offset}")
    #     return offset

    # def insert_record(self, record):
    #     """Insert a new record into the table with proper offset handling in B+ Tree and data type validation"""

    #     if len(record) != len(self.columns):
    #         raise ValueError(f"Record length {len(record)} doesn't match columns {len(self.columns)}")

    #     # Step 0: Validate types
    #     for i, col in enumerate(self.columns):
    #         expected_type = self.column_types[col]
    #         if not self._validate_type(record[i], expected_type):
    #             raise ValueError(f"Invalid type for column '{col}'. Expected {expected_type}, got '{record[i]}'")

    #     try:
    #         df = pd.read_csv(self.file_path)
    #     except (FileNotFoundError, pd.errors.EmptyDataError):
    #         df = pd.DataFrame(columns=self.columns)

    #     primary_key_value = str(record[self.columns.index(self.primary_key)])

    #     if not df.empty and primary_key_value in df[self.primary_key].astype(str).values:
    #         raise ValueError(f"Primary key {primary_key_value} already exists in table")

    #     if self.index_manager.get_primary_index(self.table_name, primary_key_value) is not None:
    #         raise ValueError(f"Primary key {primary_key_value} already exists in index")

    #     for col, (ref_table, ref_col) in self.foreign_keys.items():
    #         ref_value = str(record[self.columns.index(col)])
    #         if ref_value:
    #             ref_path = f"databases/{self.db_name}/{ref_table}.csv"
    #             if not os.path.exists(ref_path):
    #                 raise ValueError(f"Referenced table {ref_table} doesn't exist")

    #             ref_df = pd.read_csv(ref_path)
    #             if ref_value not in ref_df[ref_col].astype(str).values:
    #                 raise ValueError(f"Foreign key violation: {ref_value} not found in {ref_table}.{ref_col}")

    #     offset = len(df)

    #     try:
    #         self.index_manager.add_primary_index(self.table_name, primary_key_value, offset)
    #     except Exception as e:
    #         raise ValueError(f"Failed to add to index: {str(e)}")

    #     try:
    #         write_header = not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0

    #         with open(self.file_path, 'a', newline='') as f:
    #             writer = csv.writer(f)
    #             if write_header:
    #                 writer.writerow(self.columns)
    #             writer.writerow(record)
    #     except Exception as e:
    #         self.index_manager.delete_primary_index(self.table_name, primary_key_value)
    #         raise IOError(f"Failed to write record: {str(e)}")

    #     print(f"✅ Record inserted successfully. PK: {primary_key_value}, Offset: {offset}")
    #     return offset


    def insert_record(self, record):
        if len(record) != len(self.columns):
            raise ValueError(f"Record length {len(record)} doesn't match columns {len(self.columns)}")

        for i, col in enumerate(self.columns):
            expected_type = self.column_types[col]
            print(f"Validating {col} with expected type {expected_type} for value {record[i]}")
            if not self._validate_type(record[i], expected_type):
                raise ValueError(f"Invalid type for column '{col}'. Expected {expected_type}, got '{record[i]}'")

        try:
            df = pd.read_csv(self.file_path)
            
        except (FileNotFoundError, pd.errors.EmptyDataError):
            df = pd.DataFrame(columns=self.columns)

        primary_key_value = str(record[self.columns.index(self.primary_key)])

        if not df.empty and primary_key_value in df[self.primary_key].astype(str).values:
            raise ValueError(f"Primary key {primary_key_value} already exists in table")

        if self.index_manager.get_primary_index(self.table_name, primary_key_value) is not None:
            raise ValueError(f"Primary key {primary_key_value} already exists in index")

        for col, (ref_table, ref_col) in self.foreign_keys.items():
            ref_value = str(record[self.columns.index(col)])
            if ref_value:
                ref_path = f"Project_ADBMS/databases/{self.db_name}/{ref_table}.csv"
                if not os.path.exists(ref_path):
                    raise ValueError(f"Referenced table {ref_table} doesn't exist")
                ref_df = pd.read_csv(ref_path)
                if ref_value not in ref_df[ref_col].astype(str).values:
                    raise ValueError(f"Foreign key violation: {ref_value} not found in {ref_table}.{ref_col}")

        offset = len(df)

        try:
            self.index_manager.add_primary_index(self.table_name, primary_key_value, offset)
        except Exception as e:
            raise ValueError(f"Failed to add to index: {str(e)}")

        try:
            write_header = not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0

            with open(self.file_path, 'a', newline='') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(self.columns)
                writer.writerow(record)
        except Exception as e:
            self.index_manager.delete_primary_index(self.table_name, primary_key_value)
            raise IOError(f"Failed to write record: {str(e)}")

        print(f"✅ Record inserted successfully. PK: {primary_key_value}, Offset: {offset}")
        return offset


    # def delete_record(self, search_column, search_value):
    #     """Delete a record and handle cascading deletes properly"""

    #     if not os.path.exists(self.file_path):
    #         print(f"Table '{self.table_name}' does not exist!")
    #         return

    #     df = pd.read_csv(self.file_path)

    #     if search_column not in df.columns:
    #         raise KeyError(f"Column '{search_column}' does not exist in {self.table_name}")

    #     deleted_rows = df[df[search_column].astype(str) == str(search_value)]

    #     if deleted_rows.empty:
    #         print(f"No matching records found in {self.table_name} for {search_column} = {search_value}")
    #         return

    #     print(f"Deleting {len(deleted_rows)} record(s) from {self.table_name} where {search_column} = {search_value}")

    #     # ✅ Perform cascading deletes ONLY if the search column is a primary key
    #     if search_column == self.primary_key:
    #         for table, schema in self.metadata_manager.metadata.items():
    #             foreign_keys = schema.get("foreign_keys", {})

    #             for fk_col, (ref_table, ref_col) in foreign_keys.items():
    #                 # If another table references this table's primary key
    #                 if ref_table == self.table_name and ref_col == self.primary_key:
    #                     ref_file_path = f"databases/{self.db_name}/{table}.csv"

    #                     if not os.path.exists(ref_file_path):
    #                         continue

    #                     ref_df = pd.read_csv(ref_file_path)

    #                     # 🚫 CORRECTED: Only delete rows where the FOREIGN KEY matches the deleted PRIMARY KEY value
    #                     matching_rows = ref_df[ref_df[fk_col].astype(str) == str(search_value)]

    #                     if not matching_rows.empty:
    #                         print(f"CASCADE DELETE: Removing {len(matching_rows)} record(s) from {table} where {fk_col} = {search_value}")
    #                         ref_df = ref_df[ref_df[fk_col].astype(str) != str(search_value)]
    #                         ref_df.to_csv(ref_file_path, index=False)

        # ✅ Delete the record from the main table
        df = df[df[search_column].astype(str) != str(search_value)]
        df.to_csv(self.file_path, index=False)

        print(f"Record(s) successfully deleted from {self.table_name}")

    def delete_record(self, search_column, search_value):
        """Delete records with comprehensive index handling"""
        try:
            # 1. Read the entire file
            df = pd.read_csv(self.file_path)
            if df.empty:
                raise ValueError("Table is empty")
    
            # 2. Validate search column exists
            if search_column not in df.columns:
                raise ValueError(f"Column '{search_column}' doesn't exist")
    
            # 3. Find matching records
            mask = df[search_column].astype(str) == str(search_value)
            if not mask.any():
                raise ValueError(f"No records found with {search_column}={search_value}")
    
            # 4. Get indices of records to delete
            delete_indices = df[mask].index.tolist()
    
            # 5. Special handling for primary key deletes
            if search_column == self.primary_key:
                # First verify all PKs exist in index
                missing_in_index = [
                    str(df.at[idx, self.primary_key])
                    for idx in delete_indices
                    if self.index_manager.get_primary_index(self.table_name, str(df.at[idx, self.primary_key])) is None
                ]
                
                if missing_in_index:
                    print(f"⚠️ Missing PKs in index: {missing_in_index}. Forcing full reindex...")
                    self._force_reindex_with_repair()
                    
                # Now perform deletions
                for idx in delete_indices:
                    pk_value = str(df.at[idx, self.primary_key])
                    try:
                        if not self.index_manager.delete_primary_index(self.table_name, pk_value):
                            print(f"⚠️ PK {pk_value} not in index but exists in file. Continuing deletion...")
                    except Exception as e:
                        print(f"⚠️ Error deleting PK {pk_value} from index: {str(e)}. Continuing deletion...")
    
            # 6. Handle foreign key cascading
            if search_column == self.primary_key and self.foreign_keys:
                self._handle_cascading_deletes(str(search_value))
    
            # 7. Delete records from DataFrame
            df = df[~mask].reset_index(drop=True)
    
            # 8. Rebuild index if we had any index inconsistencies
            if search_column == self.primary_key and missing_in_index:
                self._rebuild_index_after_delete(df)
    
            # 9. Write back to file
            df.to_csv(self.file_path, index=False)
            print(f"✅ Deleted {len(delete_indices)} record(s) where {search_column}={search_value}")
    
        except Exception as e:
            raise IOError(f"Delete failed: {str(e)}")
    
    def _force_reindex_with_repair(self):
        """Force a complete reindex with repair capabilities"""
        df = pd.read_csv(self.file_path)

        # Create temporary index
        temp_index = {}
        for offset, row in df.iterrows():
            pk_value = str(row[self.primary_key])
            temp_index[pk_value] = offset

        # Clear and rebuild the actual index
        self.index_manager.rebuild_primary_index(self.table_name, df, self.primary_key)

        # Verify all keys made it to the index
        for pk_value, offset in temp_index.items():
            if self.index_manager.get_primary_index(self.table_name, pk_value) is None:
                print(f"⚠️ Critical: Failed to index PK {pk_value}. Adding manually...")
                self.index_manager.add_primary_index(self.table_name, pk_value, offset)

    def _rebuild_index_after_delete(self, df):
        """Rebuild index after deletion with missing keys"""
        print("⏳ Rebuilding index after deletion...")
        self.index_manager.rebuild_primary_index(self.table_name, df, self.primary_key)
        print("✅ Index rebuilt successfully after deletion")

    def _handle_cascading_deletes(self, pk_value):
        """Handle cascading deletes for foreign key relationships"""
        for table, schema in self.metadata_manager.metadata.items():
            for col, (ref_table, ref_col) in schema.get("foreign_keys", {}).items():
                if ref_table == self.table_name:
                    ref_path = f"Project_ADBMS/databases/{self.db_name}/{table}.csv"
                    if os.path.exists(ref_path):
                        ref_df = pd.read_csv(ref_path)
                        affected = ref_df[ref_df[col].astype(str) == str(pk_value)]
                        if not affected.empty:
                            print(f"🔄 Cascading delete: Removing {len(affected)} records from {table}")
                            ref_df = ref_df[ref_df[col].astype(str) != str(pk_value)]
                            ref_df.to_csv(ref_path, index=False)

    def rebuild_index(self):
        """Force rebuild of the entire primary key index"""
        df = pd.read_csv(self.file_path)
        self.index_manager.rebuild_primary_index(self.table_name, df, self.primary_key)
        print("✅ Primary key index rebuilt successfully")


    #def update_record(self, search_column, search_value, update_column, update_value):
    #    
    #    df = pd.read_csv(self.file_path)
#
    #    if search_column not in df.columns or update_column not in df.columns:
    #        raise Exception(f"Error: Column does not exist in table '{self.table_name}'.")
#
    #   
    #    if update_column in self.foreign_keys:
    #        ref_table, ref_column = self.foreign_keys[update_column]
    #        ref_df = pd.read_csv(f"databases/{self.db_name}/{ref_table}.csv")
    #        
    #        if str(update_value) not in ref_df[ref_column].astype(str).values:
    #            raise Exception(f"Foreign key constraint failed: '{update_value}' does not exist in '{ref_table}({ref_column})'.")
#
    #    mask = df[search_column].astype(str) == str(search_value)
    #    print(f"Received arguments: {search_column}, {search_value}, {update_column}, {update_value}")
#
    #    if not mask.any():
    #        raise Exception(f"Error: No record found where '{search_column}' = '{search_value}'.")
#
    #    df.loc[mask, update_column] = update_value
    #    df.to_csv(self.file_path, index=False)
#
    #    print(f"✅ Record updated successfully in '{self.table_name}'.")
#
    def delete_table(self):
     
       if os.path.exists(self.file_path):
           os.remove(self.file_path)
           self.metadata_manager.delete_table(self.table_name)
           print(f"Table '{self.table_name}' deleted successfully.")

    # def update_record(self, search_column, search_value, update_column, update_value):
    #     """Update records with proper B+ Tree index maintenance"""
    #     try:
    #         # 1. Read the entire file
    #         df = pd.read_csv(self.file_path)
    #         if df.empty:
    #             raise ValueError("Table is empty")

    #         # 2. Validate columns
    #         if search_column not in df.columns:
    #             raise ValueError(f"Search column '{search_column}' doesn't exist")
    #         if update_column not in df.columns:
    #             raise ValueError(f"Update column '{update_column}' doesn't exist")

    #         # 3. Find matching records
    #         mask = df[search_column].astype(str) == str(search_value)
    #         if not mask.any():
    #             raise ValueError(f"No records found with {search_column}={search_value}")

    #         # 4. Handle foreign key constraints
    #         if update_column in self.foreign_keys:
    #             ref_table, ref_col = self.foreign_keys[update_column]
    #             ref_path = f"databases/{self.db_name}/{ref_table}.csv"
    #             if not os.path.exists(ref_path):
    #                 raise ValueError(f"Referenced table '{ref_table}' not found")

    #             ref_df = pd.read_csv(ref_path)
    #             if str(update_value) not in ref_df[ref_col].astype(str).values:
    #                 raise ValueError(f"Foreign key violation: '{update_value}' not in {ref_table}.{ref_col}")

    #         # 5. Special handling for primary key updates
    #         if update_column == self.primary_key:
    #             new_pk = str(update_value)
    #             old_pks = df.loc[mask, self.primary_key].astype(str).tolist()

    #             # Check for duplicate PKs
    #             if new_pk in df[self.primary_key].astype(str).values:
    #                 raise ValueError(f"Primary key '{new_pk}' already exists")
    #             if self.index_manager.get_primary_index(self.table_name, new_pk) is not None:
    #                 raise ValueError(f"Primary key '{new_pk}' already indexed")

    #             # Update index for each affected record
    #             for idx, old_pk in zip(df[mask].index, old_pks):
    #                 # Get current offset
    #                 current_offset = self.index_manager.get_primary_index(self.table_name, old_pk)
    #                 if current_offset is None:
    #                     raise ValueError(f"Primary key '{old_pk}' not found in index")

    #                 # Update index
    #                 self.index_manager.delete_primary_index(self.table_name, old_pk)
    #                 self.index_manager.add_primary_index(self.table_name, new_pk, current_offset)

    #         # 6. Update the data
    #         df.loc[mask, update_column] = update_value

    #         # 7. If updating non-PK column that's indexed, update offsets
    #         table_schema = self.metadata_manager.get_table_schema(self.table_name)
    #         if (update_column != self.primary_key and 
    #             update_column in table_schema.get("indexes", [])):
    #             for idx in df[mask].index:
    #                 pk_value = str(df.at[idx, self.primary_key])
    #                 self.index_manager.update_primary_index(self.table_name, pk_value, idx)

    #         # 8. Write back to file
    #         df.to_csv(self.file_path, index=False)
    #         print(f"✅ Updated {mask.sum()} record(s) where {search_column}={search_value}")

    #     except Exception as e:
    #         raise IOError(f"Update failed: {str(e)}")

    # def update_record(self, search_column, search_value, update_column, update_value):
    #     """Update records with proper B+ Tree index maintenance and data type validation"""
    #     try:
    #         df = pd.read_csv(self.file_path)
    #         if df.empty:
    #             raise ValueError("Table is empty")

    #         if search_column not in df.columns:
    #             raise ValueError(f"Search column '{search_column}' doesn't exist")
    #         if update_column not in df.columns:
    #             raise ValueError(f"Update column '{update_column}' doesn't exist")

    #         # Validate new value's type
    #         expected_type = self.column_types[update_column]
    #         if not self._validate_type(update_value, expected_type):
    #             raise ValueError(f"Invalid type for column '{update_column}'. Expected {expected_type}, got '{update_value}'")

    #         mask = df[search_column].astype(str) == str(search_value)
    #         if not mask.any():
    #             raise ValueError(f"No records found with {search_column}={search_value}")

    #         if update_column in self.foreign_keys:
    #             ref_table, ref_col = self.foreign_keys[update_column]
    #             ref_path = f"databases/{self.db_name}/{ref_table}.csv"
    #             if not os.path.exists(ref_path):
    #                 raise ValueError(f"Referenced table '{ref_table}' not found")

    #             ref_df = pd.read_csv(ref_path)
    #             if str(update_value) not in ref_df[ref_col].astype(str).values:
    #                 raise ValueError(f"Foreign key violation: '{update_value}' not in {ref_table}.{ref_col}")

    #         if update_column == self.primary_key:
    #             new_pk = str(update_value)
    #             old_pks = df.loc[mask, self.primary_key].astype(str).tolist()

    #             if new_pk in df[self.primary_key].astype(str).values:
    #                 raise ValueError(f"Primary key '{new_pk}' already exists")
    #             if self.index_manager.get_primary_index(self.table_name, new_pk) is not None:
    #                 raise ValueError(f"Primary key '{new_pk}' already indexed")

    #             for idx, old_pk in zip(df[mask].index, old_pks):
    #                 current_offset = self.index_manager.get_primary_index(self.table_name, old_pk)
    #                 if current_offset is None:
    #                     raise ValueError(f"Primary key '{old_pk}' not found in index")

    #                 self.index_manager.delete_primary_index(self.table_name, old_pk)
    #                 self.index_manager.add_primary_index(self.table_name, new_pk, current_offset)

    #         df.loc[mask, update_column] = update_value

    #         table_schema = self.metadata_manager.get_table_schema(self.table_name)
    #         if (update_column != self.primary_key and 
    #             update_column in table_schema.get("indexes", [])):
    #             for idx in df[mask].index:
    #                 pk_value = str(df.at[idx, self.primary_key])
    #                 self.index_manager.update_primary_index(self.table_name, pk_value, idx)

    #         df.to_csv(self.file_path, index=False)
    #         print(f"✅ Updated {mask.sum()} record(s) where {search_column}={search_value}")

    #     except Exception as e:
    #         raise IOError(f"Update failed: {str(e)}")

    def update_record(self, search_column, search_value, update_column, update_value):
        try:
            df = pd.read_csv(self.file_path)
            if df.empty:
                raise ValueError("Table is empty")

            if search_column not in df.columns:
                raise ValueError(f"Search column '{search_column}' doesn't exist")
            if update_column not in df.columns:
                raise ValueError(f"Update column '{update_column}' doesn't exist")

            expected_type = self.column_types[update_column]
            if not self._validate_type(update_value, expected_type):
                raise ValueError(f"Invalid type for column '{update_column}'. Expected {expected_type}, got '{update_value}'")

            mask = df[search_column].astype(str) == str(search_value)
            if not mask.any():
                raise ValueError(f"No records found with {search_column}={search_value}")

            if update_column in self.foreign_keys:
                ref_table, ref_col = self.foreign_keys[update_column]
                ref_path = f"Project_ADBMS/databases/{self.db_name}/{ref_table}.csv"
                if not os.path.exists(ref_path):
                    raise ValueError(f"Referenced table '{ref_table}' not found")
                ref_df = pd.read_csv(ref_path)
                if str(update_value) not in ref_df[ref_col].astype(str).values:
                    raise ValueError(f"Foreign key violation: '{update_value}' not in {ref_table}.{ref_col}")

            if update_column == self.primary_key:
                new_pk = str(update_value)
                old_pks = df.loc[mask, self.primary_key].astype(str).tolist()

                if new_pk in df[self.primary_key].astype(str).values:
                    raise ValueError(f"Primary key '{new_pk}' already exists")
                if self.index_manager.get_primary_index(self.table_name, new_pk) is not None:
                    raise ValueError(f"Primary key '{new_pk}' already indexed")

                for idx, old_pk in zip(df[mask].index, old_pks):
                    current_offset = self.index_manager.get_primary_index(self.table_name, old_pk)
                    if current_offset is None:
                        raise ValueError(f"Primary key '{old_pk}' not found in index")

                    self.index_manager.delete_primary_index(self.table_name, old_pk)
                    self.index_manager.add_primary_index(self.table_name, new_pk, current_offset)

            df.loc[mask, update_column] = update_value

            table_schema = self.metadata_manager.get_table_schema(self.table_name)
            if update_column != self.primary_key and update_column in table_schema.get("indexes", []):
                for idx in df[mask].index:
                    pk_value = str(df.at[idx, self.primary_key])
                    self.index_manager.update_primary_index(self.table_name, pk_value, idx)

            df.to_csv(self.file_path, index=False)
            print(f"✅ Updated {mask.sum()} record(s) where {search_column}={search_value}")

        except Exception as e:
            raise IOError(f"Update failed: {str(e)}")

    
    # def select_records(self, search_column=None, search_value=None):
    #     if not os.path.exists(self.file_path):
    #         print(f"Table '{self.table_name}' does not exist!")
    #         return None  

    #     df = pd.read_csv(self.file_path)

    #     if df.empty:
    #         print("No records found.")
    #         return None  

    #     if search_column:
    #         if search_column not in df.columns:
    #             print(f"Column '{search_column}' does not exist in {self.table_name}.")
    #             return None  
            
    #         filtered_df = df[df[search_column].astype(str) == str(search_value)]
    #         if filtered_df.empty:
    #             print("No matching records found.")
    #             return None  
    #         return filtered_df  

    #     return df  
    def select_records(self, search_column=None, search_value=None):
        if not os.path.exists(self.file_path):
            print(f"Table '{self.table_name}' does not exist!")
            return None

        # If searching by primary key, use the B+ Tree index
        if search_column == self.primary_key:
            offset = self.index_manager.get_primary_index(self.table_name, search_value)
            print(offset)
              # Pass table name
            if offset is not None:
                # Read just that specific record using the offset
                with open(self.file_path, 'r') as f:
                    reader = csv.reader(f)
                    for i, row in enumerate(reader):
                        if i == 0:  # Skip header
                            continue
                        if i == offset + 1:  # +1 because offset 0 = first data row
                            return pd.DataFrame([row], columns=self.columns)
                return None

        # Fall back to full scan for non-primary key searches
        df = pd.read_csv(self.file_path)

        if search_column:
            if search_column not in df.columns:
                print(f"Column '{search_column}' does not exist in {self.table_name}.")
                return None

            filtered_df = df[df[search_column].astype(str) == str(search_value)]
            if filtered_df.empty:
                print("No matching records found.")
                return None
            return filtered_df

        return df


    def _validate_type(self, value, expected_type):
        """Validate the type of a value based on expected SQL type."""
        try:
            expected_type = expected_type.upper()

            if expected_type in ['INT', 'BIGINT', 'SMALLINT']:
                int(value)
            elif expected_type in ['FLOAT', 'DOUBLE']:
                float(value)
            elif expected_type == 'TEXT':
                str(value)
            elif expected_type == 'BOOL':
                if str(value).lower() not in ['true', 'false', '0', '1']:
                    return False
            elif expected_type == 'DATE':
                pd.to_datetime(value, format='%Y-%m-%d', errors='raise')
            elif expected_type == 'TIME':
                pd.to_datetime(value, format='%H:%M:%S', errors='raise')
            else:
                # Unknown or unsupported type
                return False

            return True
        except (ValueError, TypeError):
            return False


