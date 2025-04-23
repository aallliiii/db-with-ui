

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
    # @staticmethod
    # def _parse_select(query: str) -> Dict:
    #     """Parse SELECT query with INNER, LEFT, RIGHT, FULL JOIN support and advanced features"""
    #     pattern = (
    #         r"select\s+(.+?)\s+from\s+(\w+)"
    #         r"(?:\s+(?:as\s+)?(\w+))?"  # main table alias
    #         r"(?:\s+(inner|left|right|full)\s+join\s+(\w+)(?:\s+(?:as\s+)?(\w+))?\s+on\s+([^\s]+?\s*=\s*[^\s]+?))?"  # JOIN
    #         r"(?:\s+where\s+(.+?))?"
    #         r"(?:\s+group\s+by\s+(.+?))?"
    #         r"(?:\s+having\s+(.+?))?"
    #         r"(?:\s+order\s+by\s+(.+?))?"
    #         r"(?:\s+limit\s+(\d+))?"
    #         r"(?:\s+offset\s+(\d+))?"
    #         r"\s*$"
    #     )

    #     match = re.match(pattern, query.strip(), re.IGNORECASE)
    #     if not match:
    #         raise ValueError("Invalid SELECT syntax")

    #     (columns_part, table_name, table_alias,
    #     join_type, join_table, join_alias, join_condition,
    #     where_clause, group_by_clause, having_clause,
    #     order_by_clause, limit, offset) = match.groups()

    #     columns = []
    #     for col in columns_part.split(","):
    #         col = col.strip()
    #         if " as " in col.lower():
    #             parts = re.split(r"\s+as\s+", col, flags=re.IGNORECASE)
    #             columns.append({
    #                 "expression": parts[0].strip(),
    #                 "alias": parts[1].strip()
    #             })
    #         else:
    #             columns.append(col)

    #     return {
    #         "type": "select",
    #         "table_name": table_name,
    #         "table_alias": table_alias,
    #         "columns": columns,
    #         "join": {
    #             "type": join_type.lower() if join_type else None,
    #             "table": join_table,
    #             "alias": join_alias,
    #             "condition": join_condition
    #         } if join_table else None,
    #         "conditions": QueryParser.parse_conditions(where_clause) if where_clause else [],
    #         "group_by": [g.strip() for g in group_by_clause.split(",")] if group_by_clause else [],
    #         "having": QueryParser.parse_conditions(having_clause) if having_clause else [],
    #         "order_by": [(x.strip().rsplit(" ", 1)[0], x.strip().rsplit(" ", 1)[1].lower()) if " " in x else (x.strip(), "asc")
    #                     for x in order_by_clause.split(",")] if order_by_clause else [],
    #         "limit": int(limit) if limit else None,
    #         "offset": int(offset) if offset else None
    #     }


    @staticmethod
    def _parse_select(query: str) -> Dict:
        """Parse SELECT query with JOIN support including CROSS JOIN and advanced clauses"""
        pattern = (
            r"select\s+(.+?)\s+from\s+(\w+)"
            r"(?:\s+(?:as\s+)?(\w+))?"  # main table alias
            r"(?:\s+(inner|left|right|full|cross)\s+join\s+(\w+)(?:\s+(?:as\s+)?(\w+))?(?:\s+on\s+([^\s]+?\s*=\s*[^\s]+?))?)?"  # JOIN
            r"(?:\s+where\s+(.+?))?"
            r"(?:\s+group\s+by\s+(.+?))?"
            r"(?:\s+having\s+(.+?))?"
            r"(?:\s+order\s+by\s+(.+?))?"
            r"(?:\s+limit\s+(\d+))?"
            r"(?:\s+offset\s+(\d+))?"
            r"\s*$"
        )

        match = re.match(pattern, query.strip(), re.IGNORECASE)
        if not match:
            raise ValueError("Invalid SELECT syntax")

        (columns_part, table_name, table_alias,
        join_type, join_table, join_alias, join_condition,
        where_clause, group_by_clause, having_clause,
        order_by_clause, limit, offset) = match.groups()

        columns = []
        for col in columns_part.split(","):
            col = col.strip()
            if " as " in col.lower():
                parts = re.split(r"\s+as\s+", col, flags=re.IGNORECASE)
                columns.append({
                    "expression": parts[0].strip(),
                    "alias": parts[1].strip()
                })
            else:
                columns.append(col)

        return {
            "type": "select",
            "table_name": table_name,
            "table_alias": table_alias,
            "columns": columns,
            "join": {
                "type": join_type.lower() if join_type else None,
                "table": join_table,
                "alias": join_alias,
                "condition": join_condition if join_type != "cross" else None
            } if join_type else None,
            "conditions": QueryParser.parse_conditions(where_clause) if where_clause else [],
            "group_by": [g.strip() for g in group_by_clause.split(",")] if group_by_clause else [],
            "having": QueryParser.parse_conditions(having_clause) if having_clause else [],
            "order_by": [(x.strip().rsplit(" ", 1)[0], x.strip().rsplit(" ", 1)[1].lower()) if " " in x else (x.strip(), "asc")
                        for x in order_by_clause.split(",")] if order_by_clause else [],
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
    def parse_conditions(condition_str: str) -> List[List[Dict[str, Union[str, Tuple, List[str], bool]]]]:
        """Parses a WHERE or HAVING condition string into nested AND/OR condition groups"""
        if not condition_str:
            return []

        condition_str = condition_str.strip()
        conditions = []

        # Split by OR (top-level)
        or_blocks = [block.strip() for block in re.split(r"\s+or\s+", condition_str, flags=re.IGNORECASE)]

        for block in or_blocks:
            and_group = []

            # Match special clauses first: BETWEEN, IN, LIKE, IS
            protected = {
                "between": list(re.finditer(r"(\w+)\s+between\s+([^ ]+)\s+and\s+([^ ]+)", block, re.IGNORECASE)),
                "in": list(re.finditer(r"(\w+)\s+not\s+in\s*\(([^)]+)\)", block, re.IGNORECASE)) +
                    list(re.finditer(r"(\w+)\s+in\s*\(([^)]+)\)", block, re.IGNORECASE)),
                "like": list(re.finditer(r"(\w+)\s+(not\s+)?like\s+['\"](.+?)['\"]", block, re.IGNORECASE)),
                "is": list(re.finditer(r"(\w+)\s+is\s+(not\s+)?(null|true|false)", block, re.IGNORECASE)),
            }

            # Replace protected patterns with placeholders
            temp_block = block
            placeholders = {}
            for clause_type, matches in protected.items():
                for i, match in enumerate(matches):
                    placeholder = f"__{clause_type.upper()}_{i}__"
                    placeholders[placeholder] = (clause_type, match)
                    temp_block = re.sub(re.escape(match.group(0)), placeholder, temp_block, count=1)

            # Now split by AND
            and_conditions = [cond.strip() for cond in re.split(r"\s+and\s+", temp_block, flags=re.IGNORECASE)]

            for cond in and_conditions:
                matched = False
                for placeholder, (clause_type, match) in placeholders.items():
                    if placeholder in cond:
                        matched = True
                        if clause_type == "between":
                            col, val1, val2 = match.groups()
                            and_group.append({
                                "column": col,
                                "operator": "between",
                                "value": (val1.strip("'\""), val2.strip("'\""))
                            })
                        elif clause_type == "in":
                            col, values = match.groups()
                            is_not = "not in" in match.group(0).lower()
                            value_list = [v.strip().strip("'\"") for v in values.split(",")]
                            and_group.append({
                                "column": col,
                                "operator": "not in" if is_not else "in",
                                "value": value_list
                            })
                        elif clause_type == "like":
                            col, not_kw, pattern = match.groups()
                            and_group.append({
                                "column": col,
                                "operator": "not like" if not_kw else "like",
                                "value": pattern
                            })
                        elif clause_type == "is":
                            col, not_kw, value = match.groups()
                            and_group.append({
                                "column": col,
                                "operator": "is",
                                "value": value.lower(),
                                "not": bool(not_kw)
                            })
                        break
                if matched:
                    continue

                # Try generic comparison
                comp_match = re.match(
                    r"(\w+)\s*(=|!=|<>|>=|<=|>|<)\s*"
                    r"((?:\w+\([^)]*\))|(?:'[^']*')|(?:\"[^\"]*\")|(?:\d+\.?\d*)|(?:null|true|false))",
                    cond,
                    re.IGNORECASE
                )
                if comp_match:
                    col, op, val = comp_match.groups()
                    val = val.strip("'\"")
                    if val.lower() in ("null", "true", "false"):
                        val = val.lower()
                    elif val.replace(".", "", 1).isdigit():
                        val = float(val) if "." in val else int(val)
                    and_group.append({
                        "column": col,
                        "operator": op.replace("<>", "!="),
                        "value": val
                    })
                    continue

                raise ValueError(f"Could not parse condition: {cond}")

            conditions.append(and_group)

        return conditions
