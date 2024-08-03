# Cache Eviction Strategies

The basic operation of the cache is as follows.

* When an lookup is requested, check if the location is in the
  cache. If it is, return the appropriate value and increment the
  count of cache hits. 

* If the location is not in the cache, call ```super().lookup``` which
  will retrieve the data from 'memory'.

* The value should then be added to the cache. If the cache is full,
  then an entry needs to be evicted. The appropriate strategy should
  be used to determine which entry to evict.

Caching strategies implemented are:

1. a Cyclic strategy.
   * Assume slots ```1,...,N``` in the cache.
   * Keep track of the next slot in the cache to be used (starting
     with ```1```).
   * When an value is cached, we increment our slot count to use the
   next slot.
   * Once all slots have been filled, go back to slot ```1``` and
     cycle round. 
2. an LRU (least recently used) strategy.
   * Assume ```N``` slots.
   * Keep track of how recently each slot has been used (accessed or stored).
   * If the cache is full and a new value needs to be stored, we
     remove the entry from the slot that was least recently used and replace with
     the new value.
3. an MRU (most recently used) strategy.	 
   * Assume ```N``` slots.
   * Keep track of how recently each slot has been used (accessed or stored).
   * If the cache is full and a new value needs to be stored, we
     remove the entry from the slot that was most recently used and replace with
     the new value.
4. an LFU (least frequently used) strategy.
   * Assume ```N``` slots.
   * Keep track of how many times each item in the cache has been
     requested and the order in which they have been added to the cache.
   * If the cache is full and a new value needs to be stored. we
	 remove the entry that is least frequently used, i.e with the
	 smallest number of requests. If there is a "tie", then evict the
	 item that was least recently used, i.e. the item that has seen
	 the longest time since a request.

