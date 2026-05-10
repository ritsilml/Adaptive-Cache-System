from collections import deque, defaultdict
import heapq

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.hits = 0
        self.misses = 0

    def _remove(self, node):
        p, n = node.prev, node.next
        p.next, n.prev = n, p

    def _add(self, node):
        p = self.tail.prev
        p.next = node
        node.prev = p
        node.next = self.tail
        self.tail.prev = node

    def access(self, key):
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add(node)
            self.hits += 1
            return True
        else:
            self.misses += 1
            if len(self.cache) >= self.capacity:
                lru = self.head.next
                self._remove(lru)
                del self.cache[lru.key]
            new_node = Node(key, key)
            self._add(new_node)
            self.cache[key] = new_node
            return False

    def slots(self):
        curr = self.head.next
        res = []
        while curr != self.tail:
            res.append({"key": curr.key, "meta": "MRU→"})
            curr = curr.next
        return res
    
    def hit_rate(self):
        t = self.hits + self.misses
        return round((self.hits / t) * 100) if t > 0 else 0


class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}                     
        self.freq_map = defaultdict(list)   
        self.counter = 0
        self.hits = 0
        self.misses = 0

    def _increment(self, key):
        value, freq = self.cache[key]
        self.cache[key] = [value, freq + 1]
        self.counter += 1
        heapq.heappush(self.freq_map[freq + 1], (self.counter, key))

    def access(self, key):
        if key in self.cache:
            self._increment(key)
            self.hits += 1
            return True
        else:
            self.misses += 1
            if self.capacity == 0:
                return False
            if len(self.cache) >= self.capacity:
                self._evict()
            self.counter += 1
            self.cache[key] = [key, 1]
            heapq.heappush(self.freq_map[1], (self.counter, key))
            return False

    def _evict(self):
        for freq in sorted(self.freq_map):
            bucket = self.freq_map[freq]
            while bucket:
                _, key = heapq.heappop(bucket)
                if key in self.cache and self.cache[key][1] == freq:
                    del self.cache[key]
                    return
            del self.freq_map[freq]

    def slots(self):
        items = [(k, v[0], v[1]) for k, v in self.cache.items()]
        items.sort(key=lambda x: x[2])
        return [{"key": k, "meta": f"f={f}"} for k, _, f in items]

    def hit_rate(self):
        t = self.hits + self.misses
        return round((self.hits / t) * 100) if t > 0 else 0


class FIFOCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = deque()
        self.cache = set()
        self.hits = 0
        self.misses = 0

    def access(self, key):
        if key in self.cache:
            self.hits += 1
            return True
            
        self.misses += 1
        if self.capacity == 0:
            return False
            
        if len(self.queue) >= self.capacity:
            oldest_key = self.queue.popleft()
            self.cache.remove(oldest_key)
            
        self.queue.append(key)
        self.cache.add(key)
        return False

    def slots(self):
        return [{"key": k, "meta": "oldest←"} for k in self.queue]

    def hit_rate(self):
        t = self.hits + self.misses
        return round((self.hits / t) * 100) if t > 0 else 0


class AdaptiveCache:
    def __init__(self, capacity, window_size=6, switch_threshold=0.6):
        self.capacity = capacity
        self.window_size = window_size
        self.switch_threshold = switch_threshold

        self.lru = LRUCache(capacity)
        self.lfu = LFUCache(capacity)
        self.fifo = FIFOCache(capacity)

        self.current_policy = "LRU"
        self.active = self.lru

        self.window = deque(maxlen=window_size)
        self.access_freq = defaultdict(int)

        self.hits = 0
        self.misses = 0
        self.total_accesses = 0
        
        self.switched_from = None
        self.switched_to = None

    def _hit_rate_in_window(self):
        if not self.window:
            return 0
        return sum(self.window) / len(self.window)

    def _frequency_skew(self):
        if not self.access_freq:
            return False
        counts = list(self.access_freq.values())
        return (max(counts) / sum(counts)) > 0.40

    def _detect_and_switch(self):
        hit_rate = self._hit_rate_in_window()
        skewed   = self._frequency_skew()

        if hit_rate >= self.switch_threshold:
            best = "LRU"
        elif skewed:
            best = "LFU"
        else:
            best = "FIFO"

        if best != self.current_policy:
            self.switched_from = self.current_policy
            self.switched_to = best
            self.current_policy = best
            self.active = {"LRU": self.lru, "LFU": self.lfu, "FIFO": self.fifo}[best]

    def access(self, key):
        self.total_accesses += 1
        self.access_freq[key] += 1
        self.switched_from = None
        self.switched_to = None
        
        # Keep all underlying caches in sync so switching is seamless
        h_lru = self.lru.access(key)
        h_lfu = self.lfu.access(key)
        h_fifo = self.fifo.access(key)
        
        if self.current_policy == "LRU":
            hit = h_lru
        elif self.current_policy == "LFU":
            hit = h_lfu
        else:
            hit = h_fifo
            
        self.window.append(1 if hit else 0)
        if hit:
            self.hits += 1
        else:
            self.misses += 1
            
        if len(self.window) == self.window_size:
            self._detect_and_switch()
            
        return hit

    def slots(self):
        return self.active.slots()
        
    def hit_rate(self):
        t = self.hits + self.misses
        return round((self.hits / t) * 100) if t > 0 else 0
