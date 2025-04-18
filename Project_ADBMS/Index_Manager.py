from .b_plus_tree import BPlusTree

class IndexManager:
    def __init__(self, order=4):
        # Dictionary to store B+ Trees per table
        self.primary_indexes = {}  # { table_name: BPlusTree }
        self.order = order

    def _get_tree(self, table_name):
        """Get or create B+ Tree for a table."""
        if table_name not in self.primary_indexes:
            self.primary_indexes[table_name] = BPlusTree(self.order)
        return self.primary_indexes[table_name]

    def add_primary_index(self, table_name, key, file_offset):
        """Add primary key index using B+ Tree."""
        tree = self._get_tree(table_name)
        if tree.search(key) is not None:
            raise ValueError(f"Primary key {key} already exists in table '{table_name}'.")
        tree.insert(key, file_offset)

    def get_primary_index(self, table_name, key):
        """Retrieve file offset for primary key lookup using B+ Tree."""
        tree = self._get_tree(table_name)
        return tree.search(key)

    def delete_primary_index(self, table_name, key):
        """Remove a primary key from the B+ Tree."""
        tree = self._get_tree(table_name)
        tree.delete(key)

    def update_primary_index(self, table_name, key, new_offset):
        """Update the offset for a primary key after an update."""
        tree = self._get_tree(table_name)
        if not tree.update(key, new_offset):
            raise KeyError(f"Primary key {key} not found in table '{table_name}'.")

   

    def rebuild_primary_index(self, table_name, df, primary_key_column):
        """Rebuilds primary index from scratch"""
        # Clear existing index
        if table_name in self.primary_indexes:
            del self.primary_indexes[table_name]
        
        # Create new tree
        tree = BPlusTree(self.order)
        self.primary_indexes[table_name] = tree
        
        # Add all records
        for offset, row in df.iterrows():
            pk_value = str(row[primary_key_column])
            tree.insert(pk_value, offset)
    