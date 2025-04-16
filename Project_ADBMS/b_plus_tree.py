class BPlusTreeNode:
    def __init__(self, order, is_leaf=True):
        self.order = order
        self.is_leaf = is_leaf
        self.keys = []
        self.children = [] if not is_leaf else None
        self.values = [] if is_leaf else None  # Only leaf nodes store values
        self.next = None  # Pointer to next leaf node (for range queries)

    def is_full(self):
        return len(self.keys) >= self.order

    def __repr__(self):
        return f"BPlusTreeNode(keys={self.keys}, is_leaf={self.is_leaf})"


class BPlusTree:
    def __init__(self, order=4):
        self.root = BPlusTreeNode(order, is_leaf=True)
        self.order = order
        self.min_keys = (order // 2)

    def search(self, key, node=None):
        """Search for a key and return its value (file offset) if found."""
        node = node or self.root
        
        if node.is_leaf:
            for i, k in enumerate(node.keys):
                if k == key:
                    return node.values[i]
            return None

        # Find the appropriate child to traverse
        for i, k in enumerate(node.keys):
            if key < k:
                return self.search(key, node.children[i])
        return self.search(key, node.children[-1])

    def insert(self, key, value):
        """Insert a key-value pair into the tree."""
        root = self.root
        
        if root.is_full():
            new_root = BPlusTreeNode(self.order, is_leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        
        self._insert_non_full(self.root, key, value)

    def _insert_non_full(self, node, key, value):
        """Insert into a node that is not full."""
        if node.is_leaf:
            # Find position to insert
            idx = 0
            while idx < len(node.keys) and node.keys[idx] < key:
                idx += 1
                
            node.keys.insert(idx, key)
            node.values.insert(idx, value)
        else:
            # Find child to insert into
            idx = len(node.keys) - 1
            while idx >= 0 and key < node.keys[idx]:
                idx -= 1
            idx += 1
            
            # Split child if full
            if node.children[idx].is_full():
                self._split_child(node, idx)
                if key > node.keys[idx]:
                    idx += 1
            
            self._insert_non_full(node.children[idx], key, value)

    def _split_child(self, parent, child_idx):
        """Split a full child node."""
        child = parent.children[child_idx]
        new_node = BPlusTreeNode(self.order, child.is_leaf)
        
        split_point = self.order // 2
        mid_key = child.keys[split_point]
        
        # Split keys and values/children
        new_node.keys = child.keys[split_point + (0 if child.is_leaf else 1):]
        child.keys = child.keys[:split_point]
        
        if child.is_leaf:
            new_node.values = child.values[split_point:]
            child.values = child.values[:split_point]
            # Maintain leaf linked list
            new_node.next = child.next
            child.next = new_node
        else:
            new_node.children = child.children[split_point + 1:]
            child.children = child.children[:split_point + 1]
        
        # Insert the middle key into the parent
        parent.keys.insert(child_idx, mid_key)
        parent.children.insert(child_idx + 1, new_node)

    def delete(self, key):
        """Delete a key from the tree."""
        self._delete(self.root, key)
        
        # If root becomes empty and has one child, make that child the new root
        if not self.root.keys and not self.root.is_leaf:
            self.root = self.root.children[0]

    def _delete(self, node, key):
        """Internal delete implementation."""
        if node.is_leaf:
            # Delete from leaf node
            if key in node.keys:
                idx = node.keys.index(key)
                node.keys.pop(idx)
                node.values.pop(idx)
                return True
            return False
        
        # Find the appropriate child
        child_idx = 0
        while child_idx < len(node.keys) and key >= node.keys[child_idx]:
            child_idx += 1
            
        # Recurse into child
        result = self._delete(node.children[child_idx], key)
        
        # Handle underflow if necessary
        if len(node.children[child_idx].keys) < self.min_keys:
            self._handle_underflow(node, child_idx)
            
        return result

    def _handle_underflow(self, parent, child_idx):
        """Handle underflow in a child node."""
        # Try to borrow from left sibling
        if child_idx > 0 and len(parent.children[child_idx - 1].keys) > self.min_keys:
            self._borrow_from_left(parent, child_idx)
        # Try to borrow from right sibling
        elif child_idx < len(parent.children) - 1 and len(parent.children[child_idx + 1].keys) > self.min_keys:
            self._borrow_from_right(parent, child_idx)
        # Merge with sibling if borrowing isn't possible
        else:
            if child_idx > 0:
                self._merge_nodes(parent, child_idx - 1)
            else:
                self._merge_nodes(parent, child_idx)

    def _borrow_from_left(self, parent, child_idx):
        """Borrow a key from left sibling."""
        left = parent.children[child_idx - 1]
        right = parent.children[child_idx]
        
        if right.is_leaf:
            # For leaf nodes, borrow the last element
            borrowed_key = left.keys.pop()
            borrowed_value = left.values.pop()
            right.keys.insert(0, borrowed_key)
            right.values.insert(0, borrowed_value)
            parent.keys[child_idx - 1] = right.keys[0]
        else:
            # For internal nodes, borrow differently
            borrowed_key = parent.keys[child_idx - 1]
            borrowed_child = left.children.pop()
            parent.keys[child_idx - 1] = left.keys.pop()
            right.keys.insert(0, borrowed_key)
            right.children.insert(0, borrowed_child)

    def _borrow_from_right(self, parent, child_idx):
        """Borrow a key from right sibling."""
        left = parent.children[child_idx]
        right = parent.children[child_idx + 1]
        
        if left.is_leaf:
            # For leaf nodes, borrow the first element
            borrowed_key = right.keys.pop(0)
            borrowed_value = right.values.pop(0)
            left.keys.append(borrowed_key)
            left.values.append(borrowed_value)
            parent.keys[child_idx] = right.keys[0]
        else:
            # For internal nodes, borrow differently
            borrowed_key = parent.keys[child_idx]
            borrowed_child = right.children.pop(0)
            parent.keys[child_idx] = right.keys.pop(0)
            left.keys.append(borrowed_key)
            left.children.append(borrowed_child)

    def _merge_nodes(self, parent, left_idx):
        """Merge two nodes."""
        left = parent.children[left_idx]
        right = parent.children[left_idx + 1]
        
        if left.is_leaf:
            # Merge leaf nodes
            left.keys += right.keys
            left.values += right.values
            left.next = right.next
        else:
            # Merge internal nodes
            left.keys.append(parent.keys.pop(left_idx))
            left.keys += right.keys
            left.children += right.children
        
        # Remove the right node from parent
        parent.children.pop(left_idx + 1)
        
        # If parent is root and becomes empty, it will be handled in delete()

    def update(self, key, new_value):
        """Update the value for an existing key."""
        node = self.root
        while not node.is_leaf:
            for i, k in enumerate(node.keys):
                if key < k:
                    node = node.children[i]
                    break
            else:
                node = node.children[-1]
        
        if key in node.keys:
            idx = node.keys.index(key)
            node.values[idx] = new_value
            return True
        return False

    def range_query(self, start_key, end_key):
        """Return all key-value pairs where start_key <= key <= end_key."""
        results = []
        node = self._find_leaf(start_key)
        
        while node:
            for i, key in enumerate(node.keys):
                if start_key <= key <= end_key:
                    results.append((key, node.values[i]))
                elif key > end_key:
                    return results
            node = node.next
        
        return results

    def _find_leaf(self, key):
        """Find the leaf node that would contain the given key."""
        node = self.root
        while not node.is_leaf:
            for i, k in enumerate(node.keys):
                if key < k:
                    node = node.children[i]
                    break
            else:
                node = node.children[-1]
        return node