from .file_storage_manager import FileStorageManager
import os
import shutil
from typing import List, Dict
from .Index_Manager import IndexManager
from .Query_Parser import QueryParser
import pandas as pd
import time
import json
from pandas import DataFrame
import re
from .transaction_manager import TransactionManager, TransactionError

class DatabaseManager:  
    def __init__(self):
        self.db_name = None
        self.index_manager = None
        self.transaction_manager = None

    def use_database(self):
        self.db_name = input("Enter the name of the database you want to use: ")
        if not os.path.exists(f"Project_ADBMS/databases/{self.db_name}"):
            print(f"Database '{self.db_name}' does not exist!")
            self.db_name = None
            return False
        
        if self.index_manager is None:
            self.index_manager = IndexManager()
            
        # Initialize TransactionManager for this database
        self.transaction_manager = TransactionManager(self.db_name)
        
        print(f"Using database '{self.db_name}'.")
        return True
        
    def create_database(self):
        
        self.db_name = input("Enter the name of the new database: ")
        if os.path.exists(f"Project_ADBMS/databases/{self.db_name}"):
            print(f"Database '{self.db_name}' already exists!")
            return
        os.makedirs(f"Project_ADBMS/databases/{self.db_name}", exist_ok=True)
        self.index_manager = IndexManager()
        print(f"Database '{self.db_name}' created successfully!")


    def delete_database(self):
       
        
        self.db_name = input("Enter the name of the database you want to delete: ").strip()
        db_path = f"Project_ADBMS/databases/{self.db_name}"

        if not os.path.exists(db_path):
            print(f"Database '{self.db_name}' does not exist!")
            return

        confirm = input(f"⚠️ Are you sure you want to delete database '{self.db_name}'? (yes/no): ").strip().lower()
        if confirm == "yes":
            shutil.rmtree(db_path)  
            print(f"Database '{self.db_name}' deleted successfully!")
            self.db_name = None 
            self.index_manager = None
        else:
            print("Database deletion canceled.")


    


    def table_menu(self):
        while True:
            print("\nTable Operations:")
            print("1. Create a new table")
            print("2. Insert a record")
            print("3. Select records")
            print("4. Update a record")
            print("5. Delete a record")
            print("6. Delete a table")
            print("7. Enter SQL-command Interface")
            print("8. Transaction Controls")
            print("9. Back to main menu")
            
            choice = input("Enter your choice: ")

            if choice == "1":
                table_name = input("Enter the name of the new table: ")
                columns = input("Enter column names (comma-separated): ").split(",")
                primary_key = input("Enter the primary key column: ")
                foreign_keys = {}
                foreign_key = input("Enter foreign keys in format 'column_name:referenced_table(referenced_column)' (comma-separated), or press ENTER if none: ")
                if foreign_key.strip():
                    foreign_key_pairs = foreign_key.split(",")
                    for fk in foreign_key_pairs:
                        try:
                            column_name, ref = fk.strip().split(":")
                            ref_table, ref_column = ref.strip("()").split("(")
                            foreign_keys[column_name] = (ref_table, ref_column)
                        except ValueError:
                            print("Invalid foreign key format!")
                            break

                print("Creating table...")
                try:
                    table = FileStorageManager(self.db_name, table_name, self.index_manager, columns, primary_key, foreign_keys)
                    print(f"Table '{table_name}' created successfully!")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == "2":
                if not self.db_name:
                    print("No database selected!")
                    continue

                table_name = input("Enter the name of the table: ")
                if not os.path.exists(f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"):
                    print(f"Table '{table_name}' does not exist!")
                    continue

                record = input("Enter record values (comma-separated): ").split(",")
                try:
                    if not self.transaction_manager or not self.transaction_manager.in_transaction:
                        print("⚠️ Starting automatic transaction for this operation")
                        with TransactionManager(self.db_name) as tm:
                            table = FileStorageManager(self.db_name, table_name, self.index_manager)
                            table.insert_record(record)
                    else:
                        table = FileStorageManager(self.db_name, table_name, self.index_manager)
                        table.insert_record(record)
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == "3":
                if not self.db_name:
                    print("No database selected!")
                    continue

                table_name = input("Enter the name of the table: ")
                if not os.path.exists(f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"):
                    print(f"Table '{table_name}' does not exist!")
                    continue

                table = FileStorageManager(self.db_name, table_name, self.index_manager)
                search_column = input("Enter the column name to filter by (or press ENTER to select all records): ").strip()

                if search_column:
                    search_value = input(f"Enter the value for '{search_column}': ").strip()
                    start_time = time.time()
                    records = table.select_records(search_column, search_value)
                else:
                    start_time = time.time()
                    records = table.select_records()

                if records is not None and not records.empty:
                    print(records.to_string(index=False))
                    print(f"Total records found: {len(records)}")
                    end_time = time.time()
                    print(f"Query executed in {end_time - start_time:.4f} seconds")

            elif choice == "4":
                if not self.db_name:
                    print("No database selected!")
                    continue

                table_name = input("Enter the name of the table: ")
                if not os.path.exists(f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"):
                    print(f"Table '{table_name}' does not exist!")
                    continue

                search_column = input("Enter column to search for the record: ")
                search_value = input(f"Enter value to search in '{search_column}': ")
                update_column = input("Enter column to update: ")
                update_value = input(f"Enter new value for '{update_column}': ")

                try:
                    if not self.transaction_manager or not self.transaction_manager.in_transaction:
                        print("⚠️ Starting automatic transaction for this operation")
                        with TransactionManager(self.db_name) as tm:
                            table = FileStorageManager(self.db_name, table_name, self.index_manager)
                            table.update_record(search_column, search_value, update_column, update_value)
                    else:
                        table = FileStorageManager(self.db_name, table_name, self.index_manager)
                        table.update_record(search_column, search_value, update_column, update_value)

                    print("Record updated successfully!")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == "5":
                if not self.db_name:
                    print("No database selected!")
                    continue

                table_name = input("Enter the name of the table: ")
                if not os.path.exists(f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"):
                    print(f"Table '{table_name}' does not exist!")
                    continue

                search_column = input("Enter column to search for the record: ")
                search_value = input(f"Enter value to search in '{search_column}': ")

                try:
                    if not self.transaction_manager or not self.transaction_manager.in_transaction:
                        print("⚠️ Starting automatic transaction for this operation")
                        with TransactionManager(self.db_name) as tm:
                            table = FileStorageManager(self.db_name, table_name, self.index_manager)
                            table.delete_record(search_column, search_value)
                    else:
                        table = FileStorageManager(self.db_name, table_name, self.index_manager)
                        table.delete_record(search_column, search_value)

                    print("Record deleted successfully!")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == "6":
                if not self.db_name:
                    print("No database selected!")
                    continue

                table_name = input("Enter the name of the table to delete: ")
                if not os.path.exists(f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"):
                    print(f"Table '{table_name}' does not exist!")
                    continue

                try:
                    if not self.transaction_manager or not self.transaction_manager.in_transaction:
                        print("⚠️ Starting automatic transaction for this operation")
                        with TransactionManager(self.db_name) as tm:
                            table = FileStorageManager(self.db_name, table_name, self.index_manager)
                            table.delete_table()
                    else:
                        table = FileStorageManager(self.db_name, table_name, self.index_manager)
                        table.delete_table()

                    print(f"Table '{table_name}' deleted successfully!")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == "7":
                if not self.db_name:
                    print("No database selected!")
                    continue

                sql_query = input(f"\nEnter SQL query:\n(Type 'help' for SQL command guide)\n{self.db_name}>: ")
                self.execute_sql(sql_query)

            elif choice == "8":
                if not self.db_name:
                    print("No database selected!")
                    continue
                self.transaction_control_menu()

            elif choice == "9":
                break

            else:
                print("Invalid choice! Please enter a number between 1 and 9.")


    def transaction_control_menu(self):
        while True:
            print("\nTransaction Controls:")
            print("1. Begin Transaction")
            print("2. Commit Transaction")
            print("3. Rollback Transaction")
            print("4. Transaction Status")
            print("5. Back to Table Menu")
            
            choice = input("Enter your choice: ")
            
            if choice == "1":
                self.begin_transaction()
            elif choice == "2":
                self.commit_transaction()
            elif choice == "3":
                self.rollback_transaction()
            elif choice == "4":
                if self.transaction_manager:
                    status = self.transaction_manager.status()
                    print(f"Transaction Status: {status}")
                else:
                    print("No active database connection")
            elif choice == "5":
                break
            else:
                print("Invalid choice!")

    


    

    def execute_sql(self, sql_query: str):
        """Execute SQL command using QueryParser with automatic transaction handling."""
        try:
            sql_query = sql_query.strip()

            if sql_query.lower() == "help":
                self.show_help()
                return

            parsed_query = QueryParser.parse(sql_query)
            query_type = parsed_query.get("type")

            print(f"🧠 Parsed query type: {query_type}")

            # Mapping query types to handler methods
            query_handlers = {
                "insert": self.insert_into_table,
                "update": self.update_table,
                "delete": self.delete_from_table,
                "select": self.select_from_table,
                "create_table": self.create_table,
                "drop_table": self.drop_table,
                "begin_transaction": lambda _: self._begin_transaction_sql(),
                "commit": lambda _: self._commit_transaction_sql(),
                "rollback": lambda _: self._rollback_transaction_sql()
            }

            if query_type not in query_handlers:
                print("❌ Unsupported query type.")
                return "Unsupported query type."

            handler = query_handlers[query_type]

            if query_type in ("insert", "update", "delete"):
                try:
                    if self.transaction_manager and self.transaction_manager.in_transaction:
                        try:
                            handler(parsed_query)
                            return f"{query_type.upper()} successful within transaction"
                        except Exception as e:
                            print(f"⚠️ Error during {query_type.upper()} inside transaction: {e}")
                            self.transaction_manager.rollback()
                            return f"{query_type.upper()} failed, rolled back"
                    else:
                        with self.transaction_manager:
                            handler(parsed_query)
                            return f"{query_type.upper()} successful"
                except Exception as e:
                    print(f"⚠️ Error during {query_type.upper()}, rolled back: {e}")
                    return f"Error: {e}"

            elif query_type == "select":
                return handler(parsed_query)  # ✅ Return result of SELECT

            else:
                # Non-transactional operations or explicit transaction commands
                return handler(parsed_query)

        except Exception as e:
            print(f"❌ Error executing query: {e}")
            return f"Error: {str(e)}"



                

    








    def evaluate_conditions(self, record: dict, conditions: List[List[Dict]]) -> bool:
        """Evaluate OR-AND based conditions for a record"""
        for and_group in conditions:  # Each AND group is part of OR logic
            if all(self.evaluate_single_condition(record, cond) for cond in and_group):
                return True  # At least one AND group is True → satisfies the OR
        return False

    def evaluate_single_condition(self, record: dict, cond: Dict) -> bool:
        """Evaluate a single condition dict against a record"""
        col = cond["column"]
        op = cond["operator"]
        val = cond["value"]
        record_val = record.get(col)

        # Try to convert to numbers if applicable
        try:
            if isinstance(record_val, str) and record_val.replace(".", "", 1).isdigit():
                record_val = float(record_val)
            if isinstance(val, str) and val.replace(".", "", 1).isdigit():
                val = float(val)
        except Exception as e:
            print(f"Error converting values for comparison: {e}")
            return False  # If conversion fails, the condition is not met

        try:
            if op == "=":
                return record_val == val
            elif op == "!=":
                return record_val != val
            elif op == ">":
                return float(record_val) > float(val)
            elif op == "<":
                return float(record_val) < float(val)
            elif op == ">=":
                return float(record_val) >= float(val)
            elif op == "<=":
                return float(record_val) <= float(val)
            elif op == "between" and isinstance(val, tuple) and len(val) == 2:
                lower, upper = val
                return lower <= float(record_val) <= upper
            elif op == "in":
                # Check if record_val is in the list of values
                return str(record_val) in map(str, val)
            elif op == "not in":
                # Check if record_val is NOT in the list of values
                return str(record_val) not in map(str, val)
            elif op == "like":
                # SQL LIKE → convert % to .* and _ to . in regex, perform case-insensitive match but keep case intact
                import re
                pattern = "^" + re.escape(val).replace(r"\%", ".*").replace(r"\_", ".") + "$"
                return re.match(pattern, str(record_val), re.IGNORECASE) is not None
        except Exception as e:
            print(f"Condition evaluation error: {e}")

        return False

    

    def create_table(self, parsed_query):
        """Handle CREATE TABLE with data types"""
        table_name = parsed_query["table_name"]
        columns_with_types = parsed_query["columns"]  # Dict[col_name] = type
        primary_key = parsed_query["primary_key"]
        foreign_keys = parsed_query["foreign_keys"]

        # Ensure table doesn't already exist
        if os.path.exists(f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"):
            print(f"Table '{table_name}' already exists.")
            return

        # Pass both column names and types separately if needed
        column_names = list(columns_with_types.keys())

        # Create table using FileStorageManager
        table = FileStorageManager(
            db_name=self.db_name,
            table_name=table_name,
            index_manager=self.index_manager,
            columns=columns_with_types,  # Keep full schema (with types)
            primary_key=primary_key,
            foreign_keys=foreign_keys
        )

        print(f"Table '{table_name}' created successfully!")

    

    def insert_into_table(self, parsed_query):
        """Handle INSERT INTO with auto PK support and proper NULL handling."""
        if not self.transaction_manager or not self.transaction_manager.in_transaction:
            print("⚠️ Operation must be performed within a transaction")
            return

        try:
            table_name = parsed_query["table_name"]
            columns = parsed_query["columns"]
            values = parsed_query["values"]

            table_path = f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"
            meta_path = f"Project_ADBMS/databases/{self.db_name}/metadata.json"

            # Validate table existence
            if not os.path.exists(table_path):
                raise ValueError(f"Table '{table_name}' does not exist!")

            # Load metadata
            with open(meta_path, "r") as f:
                metadata = json.load(f)
            
            table_metadata = metadata.get(table_name)
            if not table_metadata:
                raise ValueError(f"Metadata for table '{table_name}' not found!")
            
            primary_key = table_metadata["primary_key"]
            all_columns = table_metadata["columns"]
            column_types = table_metadata.get("column_types", {})

            # --- Auto-increment PK if missing ---
            if primary_key not in columns:
                try:
                    df = pd.read_csv(table_path)
                    max_val = df[primary_key].max()
                    new_pk = int(max_val) + 1 if pd.notna(max_val) else 1
                except (FileNotFoundError, pd.errors.EmptyDataError, KeyError):
                    new_pk = 1

                columns = [primary_key] + columns
                values = [new_pk] + values

            # --- Build the final record ---
            final_record = {col: None for col in all_columns}
            
            for col, val in zip(columns, values):
                if col not in all_columns:
                    raise ValueError(f"Column '{col}' does not exist in table!")
                final_record[col] = val

            final_record_list = [final_record[col] for col in all_columns]

            # --- Insert the record ---
            table = FileStorageManager(self.db_name, table_name, self.index_manager)
            table.insert_record(final_record_list)
            
            # Log the operation for potential rollback
            self.transaction_manager.transaction_log.append({
                'operation': 'insert',
                'table': table_name,
                'primary_key': primary_key,
                'pk_value': final_record[primary_key]
            })
            
            print(f"✅ Record inserted into '{table_name}' successfully!")

        except Exception as e:
            raise TransactionError(f"Insert failed: {e}")



    

    def select_from_table(self, parsed_query):
        """Handle SELECT queries with advanced conditions, GROUP BY, HAVING, and ORDER BY"""
        table_name = parsed_query["table_name"]
        columns = parsed_query["columns"]
        conditions = parsed_query["conditions"]
        group_by = parsed_query.get("group_by", [])
        having = parsed_query.get("having", [])
        order_by = parsed_query.get("order_by", [])

        # Ensure the table exists
        table_path = f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"
        if not os.path.exists(table_path):
            raise Exception(f"Table '{table_name}' does not exist!")

        table = FileStorageManager(self.db_name, table_name, self.index_manager)
        records = table.select_records()
        # print(records.head()) 
        # return records # Pandas DataFrame
        

        if records is None or records.empty:
            return pd.DataFrame()  # Return empty DataFrame instead of None

        # Apply WHERE conditions before grouping
        if conditions:
            filtered = []
            for _, row in records.iterrows():
                record_dict = row.to_dict()
                if self.evaluate_conditions(record_dict, conditions):
                    filtered.append(record_dict)
            print(records.head())
            records = pd.DataFrame(filtered)

        # Return empty DataFrame if no records matched
        if records.empty:
            return pd.DataFrame()

        # Ensure columns are correctly set after filtering
        records.columns = table.columns

        # GROUP BY logic
        if group_by:
            agg_ops = {}
            selected_cols = list(group_by)

            for col in columns:
                if "(" in col and ")" in col:
                    func = col.split("(")[0].lower()
                    field = col.split("(")[1].replace(")", "").strip()

                    alias = f"{func}({field})"
                    selected_cols.append(alias)

                    if func == "count":
                        agg_ops[alias] = (field, 'count')
                    elif func == "sum":
                        agg_ops[alias] = (field, 'sum')
                    elif func == "avg":
                        agg_ops[alias] = (field, 'mean')
                    elif func == "min":
                        agg_ops[alias] = (field, 'min')
                    elif func == "max":
                        agg_ops[alias] = (field, 'max')
                elif col not in group_by:
                    selected_cols.append(col)

            # Apply aggregation
            grouped = records.groupby(group_by)
            result_df = grouped.agg(**agg_ops).reset_index()

            # Apply HAVING clause
            if having:
                filtered = []
                for _, row in result_df.iterrows():
                    record_dict = row.to_dict()
                    if self.evaluate_conditions(record_dict, having):
                        filtered.append(record_dict)
                result_df = pd.DataFrame(filtered)

            # Apply ORDER BY
            if order_by:
                for col, direction in order_by:
                    if col not in result_df.columns:
                        raise ValueError(f"Column '{col}' not found in grouped data.")
                    result_df = result_df.sort_values(by=col, ascending=(direction == "asc"))

            return result_df[selected_cols]

        else:
            # No GROUP BY → Normal projection after WHERE
            if columns == ["*"]:
                columns = table.columns
                # print(records.head())
                # return records

            # Apply ORDER BY
            if order_by:
                for col, direction in order_by:
                    if col not in records.columns:
                        raise ValueError(f"Column '{col}' not found in records.")
                    records = records.sort_values(by=col, ascending=(direction == "asc"))
            print(records[columns])
            return records[columns]


    def update_table(self, parsed_query):
        """Update records in a table based on complex conditions"""

        table_name = parsed_query["table_name"]
        updates = parsed_query["updates"]
        conditions = parsed_query["conditions"]

        if not os.path.exists(f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"):
            print(f"Table '{table_name}' does not exist!")
            return

        if not updates:
            print("Error: No updates specified.")
            return

        table = FileStorageManager(self.db_name, table_name, self.index_manager)
        df = pd.read_csv(table.file_path)

        updated_count = 0
        for index, row in df.iterrows():
            if self.evaluate_conditions(row.to_dict(), conditions):
                for column, new_value in updates.items():
                    if column in df.columns:
                        df.at[index, column] = new_value
                updated_count += 1

        df.to_csv(table.file_path, index=False)
        print(f"✅ {updated_count} record(s) updated in '{table_name}'.")


    def delete_from_table(self, parsed_query: Dict):
        """Delete records based on complex conditions and handle cascading deletes"""

        table_name = parsed_query["table_name"]
        conditions = parsed_query.get("conditions", [])

        if not os.path.exists(f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"):
            print(f"Table '{table_name}' does not exist!")
            return

        table = FileStorageManager(self.db_name, table_name, self.index_manager)
        df = pd.read_csv(table.file_path)
        meta_data = table.metadata_manager
        table_metadata = meta_data.metadata.get(table_name, {})
        primary_key = table_metadata.get("primary_key")

        if not conditions:
            confirm = input(f"Are you sure you want to delete ALL records from '{table_name}'? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Delete operation canceled.")
                return
            deleted_count = len(df)
            df = df.iloc[:0]
        else:
            mask = df.apply(lambda row: self.evaluate_conditions(row.to_dict(), conditions), axis=1)
            to_delete = df[mask]
            deleted_count = len(to_delete)

            if deleted_count == 0:
                print("No matching records found. Nothing deleted.")
                return

            # Cascading deletes
            if primary_key and primary_key in df.columns:
                for value in to_delete[primary_key].astype(str):
                    for ref_table, schema in meta_data.metadata.items():
                        for fk_col, (fk_ref_table, fk_ref_col) in schema.get("foreign_keys", {}).items():
                            if fk_ref_table == table_name and fk_ref_col == primary_key:
                                ref_path = f"Project_ADBMS/databases/{self.db_name}/{ref_table}.csv"
                                if os.path.exists(ref_path):
                                    ref_df = pd.read_csv(ref_path)
                                    if fk_col in ref_df.columns:
                                        before = len(ref_df)
                                        ref_df = ref_df[ref_df[fk_col].astype(str) != value]
                                        after = len(ref_df)
                                        if before != after:
                                            print(f"CASCADE DELETE: Removed {before - after} record(s) from '{ref_table}' where {fk_col} = {value}")
                                            ref_df.to_csv(ref_path, index=False)

            df = df[~mask]

        df.to_csv(table.file_path, index=False)
        print(f"🗑️ Deleted {deleted_count} record(s) from '{table_name}'.")

      

    def drop_table(self, parsed_query):
        """Handle DROP TABLE"""
        table_name = parsed_query["table_name"]

        # Ensure table exists
        if not os.path.exists(f"Project_ADBMS/databases/{self.db_name}/{table_name}.csv"):
            print(f"Table '{table_name}' does not exist!")
            return

        # Drop table using FileStorageManager (delete CSV and associated files)
        table = FileStorageManager(self.db_name, table_name, self.index_manager)
        table.delete_table()
        print(f"Table '{table_name}' dropped successfully.")
    
    def show_help(self,):
        """Display help information for supported SQL commands"""
        help_text = """
        SQL Command Help:
        
        1. CREATE TABLE

        Syntax:
        CREATE TABLE table_name (
            column1_name column1_data_type,
            column2_name column2_data_type,
            ...,
            PRIMARY KEY (primary_key_column),
            FOREIGN KEY (column_name) REFERENCES referenced_table (referenced_column)
        );

        2. INSERT INTO
    
        Syntax:
        INSERT INTO table_name (column1, column2, ...)
        VALUES (value1, value2, ...);

        3. SELECT
    
        Syntax:
        SELECT column1, column2, ... FROM table_name
        WHERE column1 = value AND column2 = value;

        4. UPDATE
    
        Syntax:
        UPDATE table_name
        SET column1 = value1, column2 = value2, ...
        WHERE column_name = value;

        5. DELETE

        Syntax:
        DELETE FROM table_name WHERE column_name = value;

        6. DROP TABLE

        Syntax:
        DROP TABLE table_name;


        7. HELP
        --------
        Displays the help information for supported SQL commands.
        """

        print(help_text)
        input("Press any key to continue...")

    def _begin_transaction_sql(self):
        if not self.transaction_manager:
            print("❌ No database selected.")
            return
        self.transaction_manager.begin()
        print("✅ Transaction started.")

    def _commit_transaction_sql(self):
        if not self.transaction_manager:
            print("❌ No database selected.")
            return
        self.transaction_manager.commit()
        print("✅ Transaction committed.")

    def _rollback_transaction_sql(self):
        if not self.transaction_manager:
            print("❌ No database selected.")
            return
        self.transaction_manager.rollback()
        print("🔁 Transaction rolled back.")
