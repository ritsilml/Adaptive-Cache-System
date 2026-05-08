import unittest
from cache_logic import LRUCache, LFUCache, FIFOCache, AdaptiveCache

class TestCacheLogic(unittest.TestCase):
    def test_lru_cache(self):
        cache = LRUCache(2)
        self.assertFalse(cache.access(1))
        self.assertFalse(cache.access(2))
        self.assertTrue(cache.access(1))
        self.assertFalse(cache.access(3)) # Evicts 2
        self.assertFalse(cache.access(2)) # 2 was evicted, so it's a miss
        self.assertTrue(cache.access(1))  # 1 is still in cache
        
        # Test hit rate
        self.assertEqual(cache.hits, 2)
        self.assertEqual(cache.misses, 4)
        
        slots = [s['key'] for s in cache.slots()]
        self.assertIn(1, slots)
        self.assertIn(2, slots)
        self.assertNotIn(3, slots)

    def test_lfu_cache(self):
        cache = LFUCache(2)
        self.assertFalse(cache.access(1))
        self.assertFalse(cache.access(2))
        self.assertTrue(cache.access(1)) # 1 has freq 2
        self.assertFalse(cache.access(3)) # Evicts 2 (freq 1)
        self.assertFalse(cache.access(2)) # Miss, evicts 3
        self.assertTrue(cache.access(1))  # Hit, freq 3
        
        slots = [s['key'] for s in cache.slots()]
        self.assertIn(1, slots)

    def test_fifo_cache(self):
        cache = FIFOCache(2)
        self.assertFalse(cache.access(1))
        self.assertFalse(cache.access(2))
        self.assertTrue(cache.access(1))  # Does not change order
        self.assertFalse(cache.access(3)) # Evicts 1 (oldest)
        self.assertFalse(cache.access(1)) # Miss

    def test_adaptive_cache(self):
        cache = AdaptiveCache(2, window_size=4, switch_threshold=0.5)
        # Sequence: 1, 2, 3, 4 (All misses) -> FIFO fallback
        self.assertFalse(cache.access(1))
        self.assertFalse(cache.access(2))
        self.assertFalse(cache.access(3))
        self.assertFalse(cache.access(4))
        
        # Test adaptive tracking
        self.assertEqual(cache.total_accesses, 4)
        self.assertEqual(cache.misses, 4)

if __name__ == '__main__':
    unittest.main()
