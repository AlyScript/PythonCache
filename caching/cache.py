from collections import OrderedDict, defaultdict
from memory import Memory
import utilities


# This class does not provide any actual caching and is used as a
# superclass that is extended for the various strategie. It defines
# two variables that should keep track of cache hits and accessors for
# statistics and testing.
#
# cache_hit_count: should be incremented whenever the cache is hit,
# i.e. if the requested element is already in the cache.
#
# cache_hit_flag: should be set to True if the cache was hit on the
# last request and set to False otherwise
#
# Definitions of lookup in subclasses should update these variables as
# appropriate.
class Cache():

    def name(self):
        return "Cache"

    # Takes two parameters. Parameter memory is the "memory". Size is
    # a non-negative integer that indicates the size of the cache.
    def __init__(self, data, size=5):
        self.memory = Memory(data)
        self.cache_hit_count = 0
        self.cache_hit_flag = False

    # Returns information on the number of cache hit counts
    def get_cache_hit_count(self):
        return self.cache_hit_count

    def get_memory_request_count(self):
        return self.memory.get_request_count()

    # Returns the cache hit flag
    def get_cache_hit_flag(self):
        return self.cache_hit_flag

    # Look up an address. Uses caching if appropriate.
    def lookup(self, address):
        return self.memory.lookup(address)


class CyclicCache(Cache):
    def name(self):
        return "Cyclic"

    # TODO: Edit the code below to provide an implementation of a
    # cache that uses a cyclic caching strategy with the given cache
    # size. You can use additional methods and variables as you see
    # fit as long as you provide a suitable overridding of the lookup
    # method.

    def __init__(self, data, size=5):
        super().__init__(data)
        self.size = size
        self.cache = [None] * size  # Initialize cache
        self.index = 0  # Initialize index

    # Look up an address. Uses caching if appropriate.
    def lookup(self, address):
        # If address is in cache, return it
        for item in self.cache:
            if item is not None and item[0] == address:
                self.cache_hit_count += 1
                self.cache_hit_flag = True
                return item[1]

        # If address is not in cache, fetch it, store it in cache, and return it
        data = super().lookup(address)  # Fetch data using superclass's lookup method
        self.cache[self.index] = (address, data)  # Store in cache
        self.index = (self.index + 1) % self.size  # Increment index (wrap around if at end)
        self.cache_hit_flag = False
        return data

# Node class for linked list
class Node:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCache(Cache):
    def name(self):
        return "LRU"

    # TODO: Edit the code below to provide an implementation of a
    # cache that uses a least recently used caching strategy with the
    # given cache size.  You can use additional methods and variables
    # as you see fit as long as you provide a suitable overridding of
    # the lookup method.

    def __init__(self, data, size=5):
        super().__init__(data)
        self.size = size
        self.cache = {}
        # Use two dummy nodes which makes it easier to handle
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        # Remove a node from the linked list
        prev = node.prev
        next = node.next
        prev.next = next
        next.prev = prev

    def _add(self, node):
        # Add a node to the head of the linked list
        next = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = next
        next.prev = node

    # Look up an address. Uses caching if appropriate.
    def lookup(self, address):
        if address in self.cache:
            # If the key exists, remove the old node and add a new node to the head
            node = self.cache[address]
            self._remove(node)
            self._add(node)
            self.cache_hit_count += 1
            self.cache_hit_flag = True
            return node.val
        else:
            # If the key doesn't exist, add a new node to the head
            data = super().lookup(address)
            node = Node(address, data)
            self.cache[address] = node
            self._add(node)
            if len(self.cache) > self.size:
                # If the cache is full, remove the least recently used node (tail of linked list)
                node_to_remove = self.tail.prev
                self._remove(node_to_remove)
                del self.cache[node_to_remove.key]
            self.cache_hit_flag = False
            return data


class MRUCache(Cache):
    def name(self):
        return "MRU"

    # TODO: Edit the code below to provide an implementation of a
    # cache that uses a most recently used eviction strategy with the
    # given cache size.  You can use additional methods and variables
    # as you see fit as long as you provide a suitable overridding of
    # the lookup method.

    def __init__(self, data, size=5):
        super().__init__(data, size)
        self.size = size
        self.cache = {}  # Maps key to node
        self.head = Node(None, None)  # Dummy head
        self.tail = Node(None, None)  # Dummy tail
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
            self._remove(node)  # Remove from its current position
            self._add_to_front(node)  # Re-add to the front, marking it as most recently used
            self.cache_hit_count += 1
            self.cache_hit_flag = True
            return node.val
        else:
            data = super().lookup(key)
            if len(self.cache) >= self.size:
                # Remove the most recently used item, which is right behind the head
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

    # TODO: Edit the code below to provide an implementation of a
    # cache that uses a least frequently used eviction strategy with
    # the given cache size. For this strategy, the cache should keep a
    # count of the number of times an item has been requested. When
    # evicting, the item that is used least frequently should be
    # removed. If there are two items that have the same frequency,
    # then the item that was added *first*, i.e. the item that has
    # been in the cache for the longest time, should be removed. You
    # can use additional methods and variables as you see fit as long
    # as you provide a suitable overridding of the lookup method.

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

        # Remove the key from its current frequency list
        self.freq_to_keys[freq].pop(key)
        if not self.freq_to_keys[freq]:
            del self.freq_to_keys[freq]
            if freq == self.min_freq:
                # Find the next higher frequency that exists or adjust min_freq appropriately
                self.min_freq = min(self.freq_to_keys.keys(), default=self.min_freq + 1)

        # Add the key to the end of the new frequency list, updating the recency of access
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
                # Evict from the front of the lowest frequency list
                lfu_key, _ = next(iter(self.freq_to_keys[self.min_freq].items()))
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
