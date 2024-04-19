from collections import OrderedDict, defaultdict
from memory import Memory
import utilities


class Cache:
    def name(self):
        return "Cache"

    def __init__(self, data, size=5):
        self.memory = Memory(data)
        self.cache_hit_count = 0
        self.cache_hit_flag = False

    def get_cache_hit_count(self):
        return self.cache_hit_count

    def get_memory_request_count(self):
        return self.memory.get_request_count()

    def get_cache_hit_flag(self):
        return self.cache_hit_flag

    def lookup(self, address):
        return self.memory.lookup(address)


class CyclicCache(Cache):
    def name(self):
        return "Cyclic"

    def __init__(self, data, size=5):
        super().__init__(data)
        self.size = size
        self.cache = [None] * size
        self.index = 0

    def lookup(self, address):
        for item in self.cache:
            if item is not None and item[0] == address:
                self.cache_hit_count += 1
                self.cache_hit_flag = True
                return item[1]

        data = super().lookup(address)
        self.cache[self.index] = (address, data)
        self.index = (self.index + 1) % self.size
        self.cache_hit_flag = False
        return data


class Node:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


class LRUCache(Cache):
    def name(self):
        return "LRU"

    def __init__(self, data, size=5):
        super().__init__(data)
        self.size = size
        self.cache = {}
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        prev = node.prev
        next = node.next
        prev.next = next
        next.prev = prev

    def _add(self, node):
        next = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = next
        next.prev = node

    def lookup(self, address):
        if address in self.cache:
            node = self.cache[address]
            self._remove(node)
            self._add(node)
            self.cache_hit_count += 1
            self.cache_hit_flag = True
            return node.val
        else:
            data = super().lookup(address)
            node = Node(address, data)
            self.cache[address] = node
            self._add(node)
            if len(self.cache) > self.size:
                node_to_remove = self.tail.prev
                self._remove(node_to_remove)
                del self.cache[node_to_remove.key]
            self.cache_hit_flag = False
            return data


class MRUCache(Cache):
    def name(self):
        return "MRU"

    def __init__(self, data, size=5):
        super().__init__(data, size)
        self.size = size
        self.cache = {}
        self.head = Node(None, None)
        self.tail = Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def lookup(self, key):
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add_to_front(node)
            self.cache_hit_count += 1
            self.cache_hit_flag = True
            return node.val
        else:
            data = super().lookup(key)
            if len(self.cache) >= self.size:
                lru_node = self.head.next
                self._remove(lru_node)
                del self.cache[lru_node.key]
            new_node = Node(key, data)
            self._add_to_front(new_node)
            self.cache[key] = new_node
            self.cache_hit_flag = False
            return data

# My LFU cache is now an array of tuples (address, data)
# i.e. cache = [(address1, data1), (address2, data2), (None), (None), (None)]
#                              cache[item] = (item, data1)


class LFUCache(Cache):
    def name(self):
        return "LFU"

    def __init__(self, data, size=5):
        super().__init__(data)
        self.size = size
        self.cache = [None] * size
        self.freq_dict = {}

    def lookup(self, address):
        # If address in Cache, increment frequency and return data
        for item in self.cache:
            if item is not None and item[0] == address:
                self.cache_hit_count += 1
                self.cache_hit_flag = True
                self.freq_dict[address] = self.freq_dict.get(address, 0) + 1
                return item[1]
        
        data = super().lookup(address)
        # If there is space in the cache, add the new item
        # Ensures items are alwaus added to the cache in the correct order
        # Which is important for the case of a tie in frequency as we remove LRU item
        if None in self.cache:
            self.cache.remove(None)
            self.cache.append((address, data))
            self.freq_dict[address] = self.freq_dict.get(address, 0) + 1
        else:
            # Find the LFU item
            lfu_item = min(self.cache, key=lambda x: self.freq_dict[x[0]])
            self.cache.remove(lfu_item)
            del self.freq_dict[lfu_item[0]]
            self.cache.append((address, data))
            self.freq_dict[address] = self.freq_dict.get(address, 0) + 1
        return data
