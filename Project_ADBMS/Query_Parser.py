# import re
# from typing import Dict, List, Tuple, Union

# class QueryParser:
#     @staticmethod
#     def parse(query: str) -> Dict[str, Union[str, List, Dict]]:
#         """Parse SQL-like queries into structured dictionary format"""
#         query = query.strip().lower()
        
#         if query.startswith("create table"):
#             return QueryParser._parse_create_table(query)
#         elif query.startswith("insert into"):
#             return QueryParser._parse_insert(query)
#         elif query.startswith("select"):
#             return QueryParser._parse_select(query)
#         elif query.startswith("update"):
#             return QueryParser._parse_update(query)
#         elif query.startswith("delete from"):
#             return QueryParser._parse_delete(query)
#         elif query.startswith("drop table"):
#             return QueryParser._parse_drop_table(query)
#         else:
#             raise ValueError(f"Unsupported query: {query}")

#     @staticmethod
#     # def _parse_create_table(query: str) -> Dict:
#     #     """Parse CREATE TABLE query"""
#     #     pattern = r"create table (\w+)\s*\((.*)\)"
#     #     match = re.match(pattern, query, re.IGNORECASE)
#     #     if not match:
#     #         raise ValueError("Invalid CREATE TABLE syntax")
        
#     #     table_name = match.group(1)
#     #     columns_part = match.group(2)
        
#     #     # Parse columns and constraints
#     #     columns = []
#     #     primary_key = None
#     #     foreign_keys = {}
        
#     #     for col_def in [c.strip() for c in columns_part.split(",")]:
#     #         if col_def.startswith("primary key"):
#     #             pk_match = re.match(r"primary key\s*\((\w+)\)", col_def, re.IGNORECASE)
#     #             if pk_match:
#     #                 primary_key = pk_match.group(1)
#     #         elif "foreign key" in col_def:
#     #             fk_match = re.match(
#     #                 r"foreign key\s*\((\w+)\)\s*references\s*(\w+)\s*\((\w+)\)", 
#     #                 col_def, 
#     #                 re.IGNORECASE
#     #             )
#     #             if fk_match:
#     #                 col, ref_table, ref_col = fk_match.groups()
#     #                 foreign_keys[col] = (ref_table, ref_col)
#     #         else:
#     #             # Regular column definition
#     #             col_parts = col_def.split()
#     #             if col_parts:
#     #                 col_name = col_parts[0]
#     #                 columns.append(col_name)
        
#     #     return {
#     #         "type": "create_table",
#     #         "table_name": table_name,
#     #         "columns": columns,
#     #         "primary_key": primary_key,
#     #         "foreign_keys": foreign_keys
#     #     }


#     # def _parse_create_table(query: str) -> Dict:
#     #     """Parse CREATE TABLE query with column types."""
#     #     pattern = r"create table (\w+)\s*\((.*)\)"
#     #     match = re.match(pattern, query, re.IGNORECASE)
#     #     if not match:
#     #         raise ValueError("Invalid CREATE TABLE syntax")
        
#     #     table_name = match.group(1)
#     #     columns_part = match.group(2)
        
#     #     # Parse columns and constraints
#     #     columns = {}  # Now a dict: column_name -> data_type
#     #     primary_key = None
#     #     foreign_keys = {}
        
#     #     for col_def in [c.strip() for c in columns_part.split(",")]:
#     #         if col_def.lower().startswith("primary key"):
#     #             pk_match = re.match(r"primary key\s*\((\w+)\)", col_def, re.IGNORECASE)
#     #             if pk_match:
#     #                 primary_key = pk_match.group(1)
#     #         elif "foreign key" in col_def.lower():
#     #             fk_match = re.match(
#     #                 r"foreign key\s*\((\w+)\)\s*references\s*(\w+)\s*\((\w+)\)", 
#     #                 col_def, 
#     #                 re.IGNORECASE
#     #             )
#     #             if fk_match:
#     #                 col, ref_table, ref_col = fk_match.groups()
#     #                 foreign_keys[col] = (ref_table, ref_col)
#     #         else:
#     #             # Regular column definition: col_name data_type
#     #             col_parts = col_def.split()
#     #             if len(col_parts) >= 2:
#     #                 col_name = col_parts[0]
#     #                 col_type = col_parts[1]
#     #                 columns[col_name] = col_type
#     #             else:
#     #                 raise ValueError(f"Invalid column definition: '{col_def}'")
        
#     #     return {
#     #         "type": "create_table",
#     #         "table_name": table_name,
#     #         "columns": columns,  # Now includes types
#     #         "primary_key": primary_key,
#     #         "foreign_keys": foreign_keys
#     #     }
#     def _parse_create_table(query: str) -> Dict:
#         """Parse CREATE TABLE query with column types. Accepts only specific SQL types."""
#         pattern = r"create table (\w+)\s*\((.*)\)"
#         match = re.match(pattern, query, re.IGNORECASE)
#         if not match:
#             raise ValueError("Invalid CREATE TABLE syntax")
        
#         table_name = match.group(1)
#         columns_part = match.group(2)

#         # Allowed SQL types
#         allowed_types = {"INT", "BIGINT", "SMALLINT", "FLOAT", "DOUBLE", "TEXT", "DATE", "TIME", "BOOL"}

#         columns = {}  # Dict: column_name -> data_type
#         primary_key = None
#         foreign_keys = {}

#         for col_def in [c.strip() for c in columns_part.split(",")]:
#             if col_def.lower().startswith("primary key"):
#                 pk_match = re.match(r"primary key\s*\((\w+)\)", col_def, re.IGNORECASE)
#                 if pk_match:
#                     primary_key = pk_match.group(1)
#             elif "foreign key" in col_def.lower():
#                 fk_match = re.match(
#                     r"foreign key\s*\((\w+)\)\s*references\s*(\w+)\s*\((\w+)\)", 
#                     col_def, 
#                     re.IGNORECASE
#                 )
#                 if fk_match:
#                     col, ref_table, ref_col = fk_match.groups()
#                     foreign_keys[col] = (ref_table, ref_col)
#             else:
#                 # Regular column definition: col_name data_type
#                 col_parts = col_def.split()
#                 if len(col_parts) >= 2:
#                     col_name = col_parts[0]
#                     col_type = col_parts[1].upper()

#                     if col_type not in allowed_types:
#                         raise ValueError(f"Invalid data type '{col_type}' for column '{col_name}'")

#                     columns[col_name] = col_type
#                 else:
#                     raise ValueError(f"Invalid column definition: '{col_def}'")

#         return {
#             "type": "create_table",
#             "table_name": table_name,
#             "columns": columns,
#             "primary_key": primary_key,
#             "foreign_keys": foreign_keys
#         }

#     @staticmethod
#     def _parse_insert(query: str) -> Dict:
#         """Parse INSERT INTO query"""
#         pattern = r"insert into (\w+)\s*(?:\(([^)]+)\))?\s*values\s*\(([^)]+)\)"
#         match = re.match(pattern, query, re.IGNORECASE)
#         if not match:
#             raise ValueError("Invalid INSERT syntax")
        
#         table_name = match.group(1)
#         columns_part = match.group(2)
#         values_part = match.group(3)
        
#         columns = [c.strip() for c in columns_part.split(",")] if columns_part else None
#         values = [v.strip().strip("'\"") for v in values_part.split(",")]
        
#         return {
#             "type": "insert",
#             "table_name": table_name,
#             "columns": columns,
#             "values": values
#         }

#     @staticmethod
#     def _parse_select(query: str) -> Dict:
#         """Parse SELECT query with optional WHERE, GROUP BY, HAVING, ORDER BY"""
#         pattern = r"select (.+?) from (\w+)(?: where (.+?))?(?: group by (.+?))?(?: having (.+?))?(?: order by (.+))?$"
#         match = re.match(pattern, query, re.IGNORECASE)
#         if not match:
#             raise ValueError("Invalid SELECT syntax")

#         columns_part = match.group(1)
#         table_name = match.group(2)
#         where_clause = match.group(3)
#         group_by_clause = match.group(4)
#         having_clause = match.group(5)
#         order_by_clause = match.group(6)

#         columns = ["*"] if columns_part.strip() == "*" else [c.strip() for c in columns_part.split(",")]
#         conditions = QueryParser.parse_conditions(where_clause) if where_clause else []
#         group_by = [g.strip() for g in group_by_clause.split(",")] if group_by_clause else []
#         having = QueryParser.parse_conditions(having_clause) if having_clause else []
        
#         order_by = []
#         if order_by_clause:
#             for part in order_by_clause.split(","):
#                 tokens = part.strip().split()
#                 column = tokens[0]
#                 direction = tokens[1].lower() if len(tokens) > 1 else "asc"
#                 order_by.append((column, direction))  # [('city', 'asc'), ('salary', 'desc')]

#         return {
#             "type": "select",
#             "table_name": table_name,
#             "columns": columns,
#             "conditions": conditions,
#             "group_by": group_by,
#             "having": having,
#             "order_by": order_by
#         }






#     @staticmethod
#     def _parse_update(query: str) -> Dict:
#         """Parse UPDATE query correctly handling multiple column assignments"""

#         # ✅ Improved regex: More robust handling of SET and WHERE clauses
#         pattern = r"update\s+(\w+)\s+set\s+(.+?)\s*(?:where\s+(.+))?$"
#         match = re.match(pattern, query.strip(), re.IGNORECASE)

#         if not match:
#             raise ValueError("Invalid UPDATE syntax")

#         # ✅ Extract table name, set part, and where clause correctly
#         table_name = match.group(1)
#         set_part = match.group(2)  # This should contain "name=gmd,email=gmd"
#         where_clause = match.group(3)  # This should contain "id = 3" or None

#         print(f"Table Name: {table_name}")
#         print(f"Set Part: {set_part}")
#         print(f"Where Clause: {where_clause}")

#         # ✅ Fix: Correctly parse multiple column-value pairs in SET clause
#         updates = {}
#         assignments = set_part.split(",")

#         for assignment in assignments:
#             parts = assignment.split("=", 1)  # Only split at the first '='
#             if len(parts) == 2:
#                 col, val = parts
#                 updates[col.strip()] = val.strip().strip("'\"")  # Remove spaces & quotes

#         # ✅ Fix: Correctly parse WHERE conditions
#         conditions = QueryParser.parse_conditions(where_clause) if where_clause else []


#         return {
#             "type": "update",
#             "table_name": table_name,
#             "updates": updates,
#             "conditions": conditions
#         }

    
#     @staticmethod
#     def _parse_delete(query: str) -> Dict:
#         """Parse DELETE query"""
#         pattern = r"delete from (\w+)(?: where (.+))?"
#         match = re.match(pattern, query, re.IGNORECASE)
#         if not match:
#             raise ValueError("Invalid DELETE syntax")
        
#         table_name = match.group(1)
#         where_clause = match.group(2)
        
#         conditions = QueryParser.parse_conditions(where_clause) if where_clause else []

        
#         return {
#             "type": "delete",
#             "table_name": table_name,
#             "conditions": conditions
#         }

#     @staticmethod
#     def _parse_drop_table(query: str) -> Dict:
#         """Parse DROP TABLE query"""
#         pattern = r"drop table (\w+)"
#         match = re.match(pattern, query, re.IGNORECASE)
#         if not match:
#             raise ValueError("Invalid DROP TABLE syntax")
        
#         return {
#             "type": "drop_table",
#             "table_name": match.group(1)
#         }
    
#     @staticmethod
#     def parse_conditions(condition_str: str) -> List[List[Dict[str, Union[str, Tuple, List[str]]]]]:
#         """Parses a WHERE or HAVING condition string into nested AND/OR condition groups"""
#         if not condition_str:
#             return []

#         print(f"Parsing condition string: '{condition_str}'")

#         condition_str = condition_str.strip()
#         conditions = []

#         # Split top-level ORs
#         or_blocks = [block.strip() for block in re.split(r"\s+or\s+", condition_str, flags=re.IGNORECASE)]

#         for block in or_blocks:
#             and_group = []

#             # Protect BETWEEN
#             between_matches = list(re.finditer(r"(\w+\(?\w*\)?)\s+between\s+(\S+)\s+and\s+(\S+)", block, re.IGNORECASE))
#             temp_block = block
#             placeholders = {}
#             for i, match in enumerate(between_matches):
#                 placeholder = f"__BETWEEN_{i}__"
#                 placeholders[placeholder] = match.group(0)
#                 temp_block = temp_block.replace(match.group(0), placeholder)

#             # Split on AND
#             and_conditions = [cond.strip() for cond in re.split(r"\s+and\s+", temp_block, flags=re.IGNORECASE)]

#             for cond in and_conditions:
#                 if cond in placeholders:
#                     cond = placeholders[cond]

#                 # BETWEEN
#                 between_match = re.match(r"(\w+\(?\w*\)?)\s+between\s+(\S+)\s+and\s+(\S+)", cond, re.IGNORECASE)
#                 if between_match:
#                     col, val1, val2 = between_match.groups()
#                     and_group.append({
#                         "column": col,
#                         "operator": "between",
#                         "value": (float(val1), float(val2))
#                     })
#                     continue

#                 # IN
#                 in_match = re.match(r"(\w+\(?\w*\)?)\s+in\s*\((.+?)\)", cond, re.IGNORECASE)
#                 if in_match:
#                     col, values = in_match.groups()
#                     value_list = [v.strip().strip("'\"") for v in values.split(",")]
#                     and_group.append({
#                         "column": col,
#                         "operator": "in",
#                         "value": value_list
#                     })
#                     continue

#                 # LIKE
#                 like_match = re.match(r"(\w+\(?\w*\)?)\s+like\s+['\"](.+?)['\"]", cond, re.IGNORECASE)
#                 if like_match:
#                     col, pattern = like_match.groups()
#                     and_group.append({
#                         "column": col,
#                         "operator": "like",
#                         "value": pattern
#                     })
#                     continue

#                 # NOT
#                 not_match = re.match(r"not\s+\(?(.+?)\)?$", cond, re.IGNORECASE)
#                 if not_match:
#                     inner = not_match.group(1).strip()
#                     # Recursively parse NOT conditions and mark as negated
#                     nested = QueryParser.parse_conditions(inner)
#                     for c in nested[0]:
#                         c["not"] = True
#                         and_group.append(c)
#                     continue

#                 # General comparison (=, !=, <>, >, <, >=, <=)
#                 comp_match = re.match(r"(\w+\(?\w*\)?)\s*(=|!=|<>|>=|<=|>|<)\s*(.+)", cond)
#                 if comp_match:
#                     col, op, val = comp_match.groups()
#                     and_group.append({
#                         "column": col.strip(),
#                         "operator": op.replace("<>", "!="),
#                         "value": val.strip().strip("'\"")
#                     })

#             conditions.append(and_group if and_group else [])

#         print(f"Final conditions: {conditions}")
#         return conditions

import re
from typing import Dict, List, Tuple, Union, Optional

class QueryParser:
    @staticmethod
    def parse(query: str) -> Dict[str, Union[str, List, Dict]]:
        """Parse SQL-like queries into structured dictionary format"""
        query = query.strip()
        lower_query = query.lower()
        
        if lower_query.startswith("create table"):
            return QueryParser._parse_create_table(query)
        elif lower_query.startswith("insert into"):
            return QueryParser._parse_insert(query)
        elif lower_query.startswith("select"):
       
            return QueryParser._parse_select(query)
        elif lower_query.startswith("update"):
            return QueryParser._parse_update(query)
        elif lower_query.startswith("delete from"):
            return QueryParser._parse_delete(query)
        elif lower_query.startswith("drop table"):
            return QueryParser._parse_drop_table(query)
        elif lower_query.startswith(("begin transaction", "start transaction")):
            return QueryParser._parse_begin_transaction(query)
        elif lower_query.startswith("commit"):
            return QueryParser._parse_commit(query)
        elif lower_query.startswith("rollback"):
            return QueryParser._parse_rollback(query)
        elif lower_query.startswith("savepoint"):
            return QueryParser._parse_savepoint(query)
        elif lower_query.startswith("release savepoint"):
            return QueryParser._parse_release_savepoint(query)
        elif lower_query.startswith("rollback to"):
            return QueryParser._parse_rollback_to_savepoint(query)
        else:
            # Check for common mistakes
            if "transaction" in lower_query:
                raise ValueError("Invalid transaction command. Use BEGIN/COMMIT/ROLLBACK")
            elif any(cmd in lower_query for cmd in ["create", "insert", "select", "update", "delete"]):
                raise ValueError("Invalid SQL syntax - check your command structure")
            else:
                raise ValueError(f"Unsupported query: {query.split()[0]}")

    @staticmethod
    def _parse_create_table(query: str) -> Dict:
        """Parse CREATE TABLE query with column types. Accepts only specific SQL types."""
        pattern = r"create table (\w+)\s*\((.*)\)"
        match = re.match(pattern, query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1)
        columns_part = match.group(2)

        # Allowed SQL types
        allowed_types = {
            "INT", "INTEGER", "BIGINT", "SMALLINT", "TINYINT",
            "FLOAT", "DOUBLE", "DECIMAL", "NUMERIC",
            "TEXT", "VARCHAR", "CHAR", "STRING",
            "DATE", "TIME", "DATETIME", "TIMESTAMP",
            "BOOL", "BOOLEAN", "BINARY", "JSON"
        }

        columns = {}  # Dict: column_name -> data_type
        primary_key = None
        foreign_keys = {}
        unique_constraints = []

        for col_def in [c.strip() for c in columns_part.split(",")]:
            col_def_lower = col_def.lower()
            
            if col_def_lower.startswith("primary key"):
                pk_match = re.match(r"primary key\s*\((\w+)\)", col_def, re.IGNORECASE)
                if pk_match:
                    primary_key = pk_match.group(1)
            elif "foreign key" in col_def_lower:
                fk_match = re.match(
                    r"foreign key\s*\((\w+)\)\s*references\s*(\w+)\s*\((\w+)\)", 
                    col_def, 
                    re.IGNORECASE
                )
                if fk_match:
                    col, ref_table, ref_col = fk_match.groups()
                    foreign_keys[col] = (ref_table, ref_col)
            elif col_def_lower.startswith("unique"):
                unique_match = re.match(r"unique\s*\((\w+)\)", col_def, re.IGNORECASE)
                if unique_match:
                    unique_constraints.append(unique_match.group(1))
            else:
                # Regular column definition: col_name data_type [constraints]
                col_parts = col_def.split()
                if len(col_parts) >= 2:
                    col_name = col_parts[0]
                    col_type = col_parts[1].upper()

                    if col_type not in allowed_types:
                        raise ValueError(f"Invalid data type '{col_type}' for column '{col_name}'")

                    columns[col_name] = col_type

        return {
            "type": "create_table",
            "table_name": table_name,
            "columns": columns,
            "primary_key": primary_key,
            "foreign_keys": foreign_keys,
            "unique_constraints": unique_constraints
        }

    @staticmethod
    def _parse_insert(query: str) -> Dict:
        """Parse INSERT INTO query with support for multiple value formats"""
        pattern = (
            r"insert into (\w+)\s*"
            r"(?:\(([^)]+)\))?\s*"
            r"(?:values\s*\(([^)]+)\)|select .+)$"
        )
        match = re.match(pattern, query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid INSERT syntax")
        
        table_name = match.group(1)
        columns_part = match.group(2)
        values_part = match.group(3)

        # Handle INSERT...SELECT differently
        if "select" in query.lower():
            select_part = query[query.lower().index("select"):]
            return {
                "type": "insert_select",
                "table_name": table_name,
                "columns": [c.strip() for c in columns_part.split(",")] if columns_part else None,
                "select_query": select_part
            }

        columns = [c.strip() for c in columns_part.split(",")] if columns_part else None
        
        # Handle value parsing with proper quote handling
        values = []
        if values_part:
            current = ""
            in_quotes = False
            quote_char = None
            for char in values_part:
                if char in ("'", '"') and (not in_quotes or char == quote_char):
                    in_quotes = not in_quotes
                    quote_char = char if in_quotes else None
                    current += char
                elif char == "," and not in_quotes:
                    values.append(current.strip())
                    current = ""
                else:
                    current += char
            if current:
                values.append(current.strip())

        return {
            "type": "insert",
            "table_name": table_name,
            "columns": columns,
            "values": [v.strip("'\"") if (v.startswith("'") and v.endswith("'")) or 
                      (v.startswith('"') and v.endswith('"')) else v for v in values]
        }

    @staticmethod
    def _parse_select(query: str) -> Dict:
        """Parse SELECT query with advanced features"""
        # Improved pattern to handle complex SELECTs
        pattern = (
            r"select\s+(.+?)\s+from\s+(\w+)(?:\s+(?:as\s+)?(\w+)?"
            r"(?:\s+where\s+(.+?))?"
            r"(?:\s+group\s+by\s+(.+?))?"
            r"(?:\s+having\s+(.+?))?"
            r"(?:\s+order\s+by\s+(.+?))?"
            r"(?:\s+limit\s+(\d+))?"
            r"(?:\s+offset\s+(\d+))?$"
        )
        
        match = re.match(pattern, query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid SELECT syntax")
        columns_part = match.group(1)
        table_name = match.group(2)
        table_alias = match.group(3)
        where_clause = match.group(4)
        group_by_clause = match.group(5)
        having_clause = match.group(6)
        order_by_clause = match.group(7)
        limit = match.group(8)
        offset = match.group(9)

        # Parse columns with aliases and functions
        columns = []
        for col in columns_part.split(","):
            col = col.strip()
            # Handle column aliases (AS or implicit)
            if " as " in col.lower():
                parts = re.split(r"\s+as\s+", col, flags=re.IGNORECASE)
                columns.append({
                    "expression": parts[0].strip(),
                    "alias": parts[1].strip()
                })
            else:
                columns.append(col)

        # Parse conditions
        conditions = QueryParser.parse_conditions(where_clause) if where_clause else []
        having = QueryParser.parse_conditions(having_clause) if having_clause else []

        # Parse GROUP BY
        group_by = [g.strip() for g in group_by_clause.split(",")] if group_by_clause else []

        # Parse ORDER BY
        order_by = []
        if order_by_clause:
            for part in order_by_clause.split(","):
                part = part.strip()
                if " " in part:
                    col, direction = part.rsplit(" ", 1)
                    order_by.append((col.strip(), direction.lower()))
                else:
                    order_by.append((part, "asc"))

        return {
            "type": "select",
            "table_name": table_name,
            "table_alias": table_alias,
            "columns": columns,
            "conditions": conditions,
            "group_by": group_by,
            "having": having,
            "order_by": order_by,
            "limit": int(limit) if limit else None,
            "offset": int(offset) if offset else None
        }

    @staticmethod
    def _parse_update(query: str) -> Dict:
        """Parse UPDATE query with support for joins and complex conditions"""
        # Basic pattern (can be extended for joins)
        pattern = (
            r"update\s+(\w+)(?:\s+set\s+(.+?))"
            r"(?:\s+where\s+(.+?))?$"
        )
        match = re.match(pattern, query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid UPDATE syntax")

        table_name = match.group(1)
        set_part = match.group(2)
        where_clause = match.group(3)

        # Parse SET clause
        updates = {}
        assignments = [a.strip() for a in set_part.split(",")]
        for assignment in assignments:
            if "=" not in assignment:
                raise ValueError(f"Invalid assignment: {assignment}")
            col, val = assignment.split("=", 1)
            updates[col.strip()] = val.strip().strip("'\"")

        # Parse WHERE conditions
        conditions = QueryParser.parse_conditions(where_clause) if where_clause else []

        return {
            "type": "update",
            "table_name": table_name,
            "updates": updates,
            "conditions": conditions
        }

    @staticmethod
    def _parse_delete(query: str) -> Dict:
        """Parse DELETE query with support for joins"""
        pattern = r"delete from (\w+)(?:\s+where\s+(.+?))?$"
        match = re.match(pattern, query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DELETE syntax")
        
        table_name = match.group(1)
        where_clause = match.group(2)
        
        conditions = QueryParser.parse_conditions(where_clause) if where_clause else []

        return {
            "type": "delete",
            "table_name": table_name,
            "conditions": conditions
        }

    @staticmethod
    def _parse_drop_table(query: str) -> Dict:
        """Parse DROP TABLE query with optional IF EXISTS"""
        pattern = r"drop table (?:(if exists)\s+)?(\w+)"
        match = re.match(pattern, query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DROP TABLE syntax")
        
        if_exists = match.group(1) is not None
        table_name = match.group(2)

        return {
            "type": "drop_table",
            "table_name": table_name,
            "if_exists": if_exists
        }

    @staticmethod
    def _parse_begin_transaction(query: str) -> Dict:
        """Parse BEGIN/START TRANSACTION command"""
        pattern = r"(?:begin|start)\s+transaction(?:\s+(.+))?"
        match = re.match(pattern, query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid BEGIN TRANSACTION syntax")
        
        options = match.group(1)
        read_only = "read only" in (options or "").lower()
        read_write = "read write" in (options or "").lower()

        return {
            "type": "begin_transaction",
            "access_mode": "read_only" if read_only else "read_write" if read_write else None
        }

    @staticmethod
    def _parse_commit(query: str) -> Dict:
        """Parse COMMIT command"""
        return {"type": "commit"}

    @staticmethod
    def _parse_rollback(query: str) -> Dict:
        """Parse ROLLBACK command"""
        return {"type": "rollback"}

    @staticmethod
    def _parse_savepoint(query: str) -> Dict:
        """Parse SAVEPOINT command"""
        pattern = r"savepoint\s+(\w+)"
        match = re.match(pattern, query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid SAVEPOINT syntax")
        return {
            "type": "savepoint",
            "name": match.group(1)
        }

    @staticmethod
    def _parse_release_savepoint(query: str) -> Dict:
        """Parse RELEASE SAVEPOINT command"""
        pattern = r"release\s+savepoint\s+(\w+)"
        match = re.match(pattern, query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid RELEASE SAVEPOINT syntax")
        return {
            "type": "release_savepoint",
            "name": match.group(1)
        }

    @staticmethod
    def _parse_rollback_to_savepoint(query: str) -> Dict:
        """Parse ROLLBACK TO SAVEPOINT command"""
        pattern = r"rollback\s+to\s+savepoint\s+(\w+)"
        match = re.match(pattern, query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid ROLLBACK TO SAVEPOINT syntax")
        return {
            "type": "rollback_to_savepoint",
            "name": match.group(1)
        }

    @staticmethod
    def parse_conditions(condition_str: str) -> List[List[Dict[str, Union[str, Tuple, List[str]]]]]:
        """Parses a WHERE or HAVING condition string into nested AND/OR condition groups"""
        if not condition_str:
            return []

        condition_str = condition_str.strip()
        conditions = []

        # Split top-level ORs
        or_blocks = [block.strip() for block in re.split(r"\s+or\s+", condition_str, flags=re.IGNORECASE)]

        for block in or_blocks:
            and_group = []

            # Protect special clauses (BETWEEN, IN, LIKE, etc.)
            protected = {
                "between": list(re.finditer(r"(\w+)\s+between\s+([^ ]+)\s+and\s+([^ ]+)", block, re.IGNORECASE)),
                "in": list(re.finditer(r"(\w+)\s+in\s*\(([^)]+)\)", block, re.IGNORECASE)),
                "like": list(re.finditer(r"(\w+)\s+like\s+['\"](.+?)['\"]", block, re.IGNORECASE)),
                "is": list(re.finditer(r"(\w+)\s+is\s+(?:not\s+)?(null|true|false)", block, re.IGNORECASE))
            }

            # Replace protected clauses with placeholders
            temp_block = block
            placeholders = {}
            for clause_type, matches in protected.items():
                for i, match in enumerate(matches):
                    placeholder = f"__{clause_type.upper()}_{i}__"
                    placeholders[placeholder] = (clause_type, match)
                    temp_block = temp_block.replace(match.group(0), placeholder)

            # Split remaining AND conditions
            and_conditions = [cond.strip() for cond in re.split(r"\s+and\s+", temp_block, flags=re.IGNORECASE)]

            for cond in and_conditions:
                if cond in placeholders:
                    clause_type, match = placeholders[cond]
                    if clause_type == "between":
                        col, val1, val2 = match.groups()
                        and_group.append({
                            "column": col,
                            "operator": "between",
                            "value": (val1.strip("'\""), val2.strip("'\""))
                        })
                    elif clause_type == "in":
                        col, values = match.groups()
                        value_list = [v.strip().strip("'\"") for v in values.split(",")]
                        and_group.append({
                            "column": col,
                            "operator": "in",
                            "value": value_list
                        })
                    elif clause_type == "like":
                        col, pattern = match.groups()
                        and_group.append({
                            "column": col,
                            "operator": "like",
                            "value": pattern
                        })
                    elif clause_type == "is":
                        col, value = match.groups()
                        and_group.append({
                            "column": col,
                            "operator": "is",
                            "value": value.lower(),
                            "not": "not" in match.group(0).lower()
                        })
                    continue

                # Handle NOT conditions
                not_match = re.match(r"not\s+\(?(.+?)\)?$", cond, re.IGNORECASE)
                if not_match:
                    inner = not_match.group(1).strip()
                    nested = QueryParser.parse_conditions(inner)
                    for c in nested[0]:
                        c["not"] = True
                        and_group.append(c)
                    continue

                # General comparison operators
                comp_match = re.match(
                    r"(\w+)\s*(=|!=|<>|>=|<=|>|<)\s*"
                    r"((?:\w+\([^)]*\))|(?:'[^']*')|(?:\"[^\"]*\")|(?:\d+)|(?:null|true|false))",
                    cond,
                    re.IGNORECASE
                )
                if comp_match:
                    col, op, val = comp_match.groups()
                    # Clean up the value
                    val = val.strip("'\"")
                    if val.lower() in ("null", "true", "false"):
                        val = val.lower()
                    elif val.isdigit():
                        val = int(val)
                    elif val.replace(".", "", 1).isdigit():
                        val = float(val)
                    
                    and_group.append({
                        "column": col,
                        "operator": op.replace("<>", "!="),
                        "value": val
                    })
                    continue

                # If we get here, the condition wasn't parsed
                raise ValueError(f"Could not parse condition: {cond}")

            conditions.append(and_group if and_group else [])

        return conditions