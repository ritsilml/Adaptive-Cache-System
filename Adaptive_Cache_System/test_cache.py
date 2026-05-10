import unittest
from cache_logic import LRUCache, LFUCache, FIFOCache, AdaptiveCache

class TestCacheLogic(unittest.TestCase):
    def test_lru_cache(self):
        cache = LRUCache(2)
        self.assertFalse(cache.access(1))
        self.assertFalse(cache.access(2))
        self.assertTrue(cache.access(1))
        self.assertFalse(cache.access(3)) # Evicts 2
        self.assertTrue(cache.access(1))  # Hit, 1 is in cache
        self.assertFalse(cache.access(2)) # Miss, evicts 3
        
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

    def test_temporal_workload(self):
        cache = AdaptiveCache(4)
        sequence = [1,2,3,1,2,4,1,2,3,1,2,1,3,2,1,4,5,1,2,1]
        for key in sequence:
            cache.access(key)
        self.assertEqual(cache.hits + cache.misses, len(sequence))

    def test_frequency_workload(self):
        cache = AdaptiveCache(4)
        sequence = [1,1,1,2,2,3,1,1,2,4,1,1,2,3,5,1,2,1,1,2]
        for key in sequence:
            cache.access(key)
        self.assertEqual(cache.hits + cache.misses, len(sequence))

    def test_custom_workload(self):
        cache = AdaptiveCache(4)
        sequence = [4, 5, 3, 2, 6, 1, 5, 2, 3, 4, 1, 2, 5, 2, 3, 1, 5, 2, 3, 1, 2, 2, 5, 1, 3, 5, 4, 1]
        for key in sequence:
            cache.access(key)
        self.assertEqual(cache.hits + cache.misses, len(sequence))

if __name__ == '__main__':
    unittest.main()
