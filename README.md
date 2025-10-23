
# Recursive Optimization App (Task 2: Performance and Edge-Case Handling)

This project demonstrates **recursive algorithms with edge-case handling, optimization, and real-time visualization** via a FastAPI backend and a simple frontend interface.

---

## �� Features
- Recursive function with edge cases (e.g., deep recursion, infinite loop protection)
- Optimized via memoization and async handling
- WebSocket/HTTP integration for progress updates
- Frontend visualization (parameters, real-time progress, results/errors)
- Stress-tested with 10,000+ requests to ensure stability

---

## �� Project Structure
```
Recursive-Optimization/
│
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── recursion_algorithm.py  # Recursive algorithm & optimization logic
│   ├── optimization.py         
│   ├── stress_test.py          # Automated stress testing (Task 2 requirement)
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── index.html              # Basic UI for interaction
│   ├── script.js                  # Handles API calls, WebSocket, and progress bar
│   └── styles.css              # Basic styling
│
└── README.md                   # This file
```

---

## �� Installation & Setup

### 1️⃣ Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Run the FastAPI Server
```bash
uvicorn main:app --reload
```
Backend runs at: **http://127.0.0.1:8000**

---

### 3️⃣ Frontend Setup
Simply open `frontend/index.html` in your browser.

If your browser blocks WebSocket connections due to CORS, you can serve it via a local server:
```bash
cd frontend
python -m http.server 8080
```
Frontend runs at: **http://127.0.0.1:8080**

---

## ⚡ Stress Test (Task 2)
Run this script to bombard the backend with recursive requests and measure performance:
```bash
cd backend
python stress_test.py
```

Expected output includes:
- Total execution time
- CPU usage pattern (via `psutil`)
- Memory stability after optimization
- Error count before and after optimization

---

## �� Key Files Explained

### �� `recursive_algorithm.py`
Implements recursive functions (e.g., Fibonacci, factorial, tree traversal) with:
- Edge case handling (max depth, infinite loop prevention)
- Memoization
- Async & multiprocessing variants for performance

### ⚙️ `websocket_manager.py`
Handles:
- Real-time communication with frontend
- Progress updates (recursion depth, completion percentage)
- Error or success messages

### �� `stress_test.py`
Simulates 5,000–10,000 requests concurrently to:
- Trigger stack overflow edge cases
- Test latency & concurrency handling
- Verify stability after optimization

---

## �� Artifacts Required (as per Task 2)

You must provide:
1. **Screenshots** or console logs showing recursive requests under load (before and after optimization)
2. **CPU/memory metrics** during stress test
3. **Video or GIF** of frontend showing recursion progress bar and error handling
4. Final test logs proving 10,000 successful iterations

---

## �� Troubleshooting

| Issue | Cause | Fix |
|--------|--------|-----|
| `Could not open requirements.txt` | Missing file | Copy dependencies into backend/requirements.txt |
| `WebSocket connection failed` | Wrong port/CORS | Ensure both backend & frontend are on same host |
| Recursion limit error | Deep recursion | Increase recursion limit or optimize using iteration |
| High CPU usage | No concurrency limit | Use async throttling or multiprocessing |

---

## ✅ Example Commands

```bash
# Run backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Run stress test
python stress_test.py

# Serve frontend
python -m http.server 8080
```

---
