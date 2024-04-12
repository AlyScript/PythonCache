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


class LFUCache(Cache):
    def name(self):
        return "LFU"

    def __init__(self, data, size=5):
        super().__init__(data, size)
        self.size = size
        self.cache = {}
        self.freqs = defaultdict(int)
        self.freq_to_keys = defaultdict(OrderedDict)
        self.min_freq = 0

    def _update_freq(self, key):
        freq = self.freqs[key]
        self.freqs[key] += 1
        new_freq = self.freqs[key]

        # Safely remove key from current freq list
        self.freq_to_keys[freq].pop(key, None)
        if not self.freq_to_keys[freq]:
            del self.freq_to_keys[freq]
            if freq == self.min_freq:
                # Adjust min_freq to next available frequency
                self.min_freq = min(
                    self.freq_to_keys.keys(), default=self.min_freq + 1
                    )

        # Add key to new frequency list
        self.freq_to_keys[new_freq][key] = None

    def lookup(self, key):
        if key in self.cache:
            self._update_freq(key)
            self.cache_hit_count += 1
            self.cache_hit_flag = True
            return self.cache[key]
        else:
            data = super().lookup(key)
            if len(self.cache) >= self.size:
                # Evict least frequently used item
                lfu_key, _ = next(
                    iter(self.freq_to_keys[self.min_freq].items())
                )
                del self.cache[lfu_key]
                del self.freqs[lfu_key]
                self.freq_to_keys[self.min_freq].popitem(last=False)
                if not self.freq_to_keys[self.min_freq]:
                    self.min_freq = min(self.freq_to_keys.keys(), default=0)

            # Add new key to cache
            self.cache[key] = data
            self.freqs[key] = 1
            self.freq_to_keys[1][key] = None
            if self.min_freq == 0 or self.min_freq > 1:
                self.min_freq = 1
            self.cache_hit_flag = False
            return data
        