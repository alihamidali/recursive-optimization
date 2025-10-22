import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import asyncio
import json
import time
import logging
from optimization import OptimizedRecursion
import psutil
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recursion_app.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI(title="Recursive Algorithms API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize optimization engine
optimizer = OptimizedRecursion()


# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logging.error(f"Error broadcasting message: {e}")


manager = ConnectionManager()


@app.get("/")
async def root():
    return {
        "message": "Recursive Algorithms API",
        "version": "1.0.0",
        "endpoints": [
            "/compute/{algorithm}",
            "/metrics",
            "/stats",
            "/system-info"
        ]
    }


@app.post("/compute/{algorithm}")
async def compute_recursive(algorithm: str, depth: int, optimized: bool = True):
    """Compute recursive algorithm with given depth"""
    start_time = time.time()

    result = await optimizer.process_recursive_task(algorithm, depth, optimized)

    total_time = time.time() - start_time
    result["total_processing_time"] = total_time
    result["server_timestamp"] = time.strftime('%Y-%m-%d %H:%M:%S')

    return result


@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    return {
        "recursion_metrics": optimizer.recursion_engine.recursion_depth_metrics[-100:],  # Last 100 metrics
        "total_requests": len(optimizer.recursion_engine.recursion_depth_metrics)
    }


@app.get("/stats")
async def get_stats():
    """Get performance statistics"""
    return optimizer.get_performance_stats()


@app.get("/system-info")
async def get_system_info():
    """Get system information"""
    process = psutil.Process()
    memory_info = process.memory_info()

    return {
        "system": {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_used": psutil.virtual_memory().used,
        },
        "process": {
            "memory_rss": memory_info.rss,
            "memory_vms": memory_info.vms,
            "cpu_percent": process.cpu_percent(),
            "thread_count": process.num_threads(),
            "create_time": process.create_time()
        },
        "python": {
            "recursion_limit": sys.getrecursionlimit(),
            "implementation": sys.implementation.name,
            "version": sys.version
        }
    }


@app.post("/clear-metrics")
async def clear_metrics():
    """Clear performance metrics"""
    optimizer.recursion_engine.clear_metrics()
    return {"message": "Metrics cleared"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)

            # Validate request
            if 'algorithm' not in request or 'depth' not in request:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Missing algorithm or depth"}),
                    websocket
                )
                continue

            # Send progress updates
            for i in range(5):
                await manager.send_personal_message(
                    json.dumps({"type": "progress", "value": i * 20, "stage": f"Processing {i + 1}/5"}),
                    websocket
                )
                await asyncio.sleep(0.3)

            # Compute result
            result = await optimizer.process_recursive_task(
                request["algorithm"],
                request["depth"],
                request.get("optimized", True)
            )

            await manager.send_personal_message(
                json.dumps({"type": "result", "data": result}),
                websocket
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": str(e)}),
            websocket
        )
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    logging.info("Recursive Algorithms API starting up...")
    logging.info(f"Available algorithms: fibonacci, tree_traversal, pathfinding")
    logging.info(f"CPU cores: {psutil.cpu_count()}")
    logging.info(f"System memory: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )