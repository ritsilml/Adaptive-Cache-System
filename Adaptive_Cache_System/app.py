from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from cache_logic import LRUCache, LFUCache, FIFOCache, AdaptiveCache

app = Flask(__name__)
app.secret_key = 'adaptive_cache_super_secret_key'

@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and not session.get('logged_in'):
        return redirect(url_for('login'))

cache = None
policy = "LRU"
capacity = 4

# Shadow caches for comparison bars
lru_shadow = None
lfu_shadow = None
fifo_shadow = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session['logged_in'] = True
        return redirect(url_for('index'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route("/docs")
def docs():
    return render_template("docs.html")

@app.route("/api/init", methods=["POST"])
def init_cache():
    global cache, policy, capacity
    global lru_shadow, lfu_shadow, fifo_shadow
    data = request.json
    policy = data.get("policy", "LRU")
    capacity = int(data.get("capacity", 4))
    
    if policy == "LRU":
        cache = LRUCache(capacity)
    elif policy == "LFU":
        cache = LFUCache(capacity)
    elif policy == "FIFO":
        cache = FIFOCache(capacity)
    else:
        cache = AdaptiveCache(capacity)
        
    lru_shadow = LRUCache(capacity)
    lfu_shadow = LFUCache(capacity)
    fifo_shadow = FIFOCache(capacity)
        
    return jsonify({"status": "ok", "policy": policy, "capacity": capacity})

@app.route("/api/step", methods=["POST"])
def step_cache():
    global cache, lru_shadow, lfu_shadow, fifo_shadow
    if not cache:
        return jsonify({"error": "Cache not initialized"}), 400
        
    data = request.json
    key = data.get("key")
    
    hit = cache.access(key)
    
    lru_shadow.access(key)
    lfu_shadow.access(key)
    fifo_shadow.access(key)
        
    slots = cache.slots()
    
    res = {
        "hit": hit,
        "slots": slots,
        "hits": cache.hits,
        "misses": cache.misses,
        "total": cache.hits + cache.misses,
        "comp": {
            "LRU": lru_shadow.hit_rate(),
            "LFU": lfu_shadow.hit_rate(),
            "FIFO": fifo_shadow.hit_rate()
        }
    }
    
    if isinstance(cache, AdaptiveCache):
        res["active_policy"] = cache.current_policy
        if cache.switched_from and cache.switched_to:
            res["switch_event"] = {"from": cache.switched_from, "to": cache.switched_to}
            
    return jsonify(res)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
