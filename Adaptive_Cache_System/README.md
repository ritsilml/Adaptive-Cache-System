# Adaptive Cache Management System - Complete Overview

 This document breaks down exactly how the entire project works, from the caching algorithms under the hood to the visual components on the web dashboard.

---

## 1. The Big Picture (Architecture)

The application is built using a modern **Client-Server Architecture**:

*   **The Backend (Python + Flask):** This is the brain of the operation. It runs your data structure algorithms (`LRUCache`, `LFUCache`, `FIFOCache`, and `AdaptiveCache`). A lightweight Flask server exposes these Python classes via REST API endpoints (`/api/init` and `/api/step`).
*   **The Frontend (HTML + CSS + JavaScript):** This is the interactive dashboard you see in your browser. It doesn't do any heavy lifting or cache calculation itself; instead, it sends the "workload sequence" step-by-step to the Python backend and beautifully renders the results returned by the server.

---

## 2. The Core Algorithms (The Cache Policies)

A "cache" is a small, fast memory space that stores recently used data to speed up future requests. When the cache is full and new data arrives, an "Eviction Policy" decides which old data to kick out. Your system supports four policies:

### 1. LRU (Least Recently Used)
*   **How it works:** Evicts the item that hasn't been accessed for the longest time. 
*   **Best for:** "Temporal" workloads where data accessed recently is likely to be accessed again soon.
*   **Data Structure:** A Hash Map (for `O(1)` fast lookups) combined with a Doubly Linked List (to easily move recently accessed items to the front).

### 2. LFU (Least Frequently Used)
*   **How it works:** Evicts the item that has been accessed the fewest number of times overall.
*   **Best for:** "Frequency" workloads where certain data items are extremely popular, regardless of when they were last accessed.
*   **Data Structure:** A Hash Map (for tracking frequencies) and a Min-Heap (to quickly find and remove the lowest frequency item in `O(log n)` time).

### 3. FIFO (First In, First Out)
*   **How it works:** The simplest policy. It evicts the oldest item inserted, exactly like a queue line at a store.
*   **Best for:** Sequential workloads (scanning a list from start to finish once).
*   **Data Structure:** A simple `Deque` (Double-ended queue) for `O(1)` insertions and evictions.

### 4. The Adaptive Cache (The AI Policy)
*   **How it works:** This is the crown jewel of the system. Instead of rigidly sticking to one policy, it monitors the workload in real-time using a sliding window.
    *   If it detects a high hit rate, it knows the current pattern is temporal, so it switches to **LRU**.
    *   If it detects a "Frequency Skew" (e.g., one item makes up >40% of all traffic), it switches to **LFU**.
    *   If the workload looks random with no distinct pattern, it defaults to **FIFO**.
*   **Seamless Switching:** To ensure that switching policies doesn't completely wipe out your cache memory, the Adaptive Cache runs "shadow caches" under the hood. It keeps LRU, LFU, and FIFO in sync simultaneously, so when it decides to switch, the new policy is already populated and ready to go!

---

## 3. The Interactive Dashboard (Frontend Features)

The webpage provides a live, visual representation of how the backend is managing data.

*   **The Workload Sequence:** You can select patterns (Temporal, Frequency, Sequential) or type your own custom sequence. The sequence represents "Keys" (pieces of data) being requested by a user over time.
*   **The Cache Slots:** This represents your computer's limited cache memory (e.g., 4 slots). You can visually see keys entering the slots. 
    *   **Green Flash:** A HIT (the data was already in the cache, saving time).
    *   **Red Flash:** A MISS (the data wasn't in the cache, causing an eviction to make room).
*   **Live Hit Rate Comparison:** Even if you select LRU as your main policy, the backend quietly runs LFU and FIFO in the shadows. The progress bars at the bottom show you exactly what the hit rate *would have been* if you had chosen those other policies instead!
*   **Time & Space Complexity:** A quick-reference cheat sheet for developers to understand the Big-O performance cost of the underlying Python algorithms.

---

## 4. How a "Simulation Step" Actually Works

When you click **Start**, the system doesn't run everything instantly. It loops through your workload sequence one by one. Here is the lifecycle of a single step:

1.  **Frontend Request:** The Javascript grabs the next number in your sequence (e.g., `Key 3`) and sends a `fetch()` request to the Flask server at `/api/step`.
2.  **Backend Calculation:** Flask receives `Key 3` and passes it to the active Python Cache class (`cache.access(3)`). The Python logic checks its dictionaries/queues to see if `3` is present. It updates its internal hits/misses and potentially evicts old data.
3.  **Backend Response:** Flask gathers the new state of the cache (what's in the slots right now, the new hit rate) and sends a JSON response back to the browser.
4.  **Frontend Render:** The Javascript reads the JSON, flashes the slot green or red, moves the progress bars, and adds a line to the Access Log.

And that is the entirety of your Adaptive Cache Management System! It's a perfect visual demonstration of data structure algorithms meeting dynamic workload analysis.

---

## 5. Demonstration Instructions

To run this application locally, follow these steps:

### Prerequisites
Make sure you have Python 3.x installed on your machine.

### Installation & Running
1. Clone the repository:
   ```bash
   git clone https://github.com/ritsilml/Adaptive-Cache-System.git
   cd Adaptive-Cache-System
   ```
2. Install the required dependencies:
   ```bash
   pip install Flask
   ```
3. Start the application:
   ```bash
   python app.py
   ```
4. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```
   
You can now interact with the Adaptive Cache Management System!
