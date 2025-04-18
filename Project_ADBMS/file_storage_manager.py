


import csv
import pandas as pd
import os
from .metadata_man import MetadataManager



class FileStorageManager:
    

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

    

    def create_table_file(self):
      
        df = pd.DataFrame(columns=self.columns)
        df.to_csv(self.file_path, index=False)


    


    def insert_record(self, record):
        """Insert a record after validating types, primary keys, and foreign keys."""
        if len(record) != len(self.columns):
            raise ValueError(f"Record length {len(record)} doesn't match expected columns {len(self.columns)}")

        # Type validation
        for i, col in enumerate(self.columns):
            expected_type = self.column_types[col]
            value = record[i]
            print(f"Validating {col}: expected {expected_type}, got value '{value}'")
            if not self._validate_type(value, expected_type):
                raise ValueError(f"Invalid type for column '{col}'. Expected {expected_type}, got '{value}'")

        # Try loading existing data
        try:
            df = pd.read_csv(self.file_path)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            df = pd.DataFrame(columns=self.columns)

        primary_key_value = str(record[self.columns.index(self.primary_key)])

        # Primary key check using B+ Tree index only
        if self.index_manager.get_primary_index(self.table_name, primary_key_value) is not None:
            raise ValueError(f"Primary key {primary_key_value} already exists in index")

        # Foreign key validation
        for col, (ref_table, ref_col) in self.foreign_keys.items():
            ref_value = str(record[self.columns.index(col)])
            if ref_value:  # Only check if value is non-empty
                ref_path = f"Project_ADBMS/databases/{self.db_name}/{ref_table}.csv"
                if not os.path.exists(ref_path):
                    raise ValueError(f"Referenced table '{ref_table}' does not exist")
                ref_df = pd.read_csv(ref_path)
                if not ref_df.empty and ref_value not in ref_df[ref_col].astype(str).values:
                    raise ValueError(f"Foreign key violation: Value '{ref_value}' not found in {ref_table}.{ref_col}")

        # Calculate file offset (row number)
        offset = len(df)

        # First, add to index (in-memory B+Tree)
        try:
            self.index_manager.add_primary_index(self.table_name, primary_key_value, offset)
        except Exception as e:
            raise ValueError(f"Failed to add primary key to index: {str(e)}")

        # Now write to file
        try:
            write_header = not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0

            with open(self.file_path, 'a', newline='') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(self.columns)
                writer.writerow(record)

        except Exception as e:
            # Rollback in-memory index if file write fails
            self.index_manager.delete_primary_index(self.table_name, primary_key_value)
            raise IOError(f"Failed to write record to file: {str(e)}")

        print(f"✅ Record inserted successfully. PK={primary_key_value}, Offset={offset}")
        return offset





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


    
    def delete_table(self):
     
       if os.path.exists(self.file_path):
           os.remove(self.file_path)
           self.metadata_manager.delete_table(self.table_name)
           print(f"Table '{self.table_name}' deleted successfully.")

   

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


