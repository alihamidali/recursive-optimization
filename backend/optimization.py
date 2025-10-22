import asyncio
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import tracemalloc
from typing import Dict, Any, List

import psutil
from recursive_algorithm import RecursiveAlgorithms
import logging

logger = logging.getLogger(__name__)


class OptimizedRecursion:
    def __init__(self):
        self.recursion_engine = RecursiveAlgorithms()
        self.max_workers = min(multiprocessing.cpu_count(), 4)  # Limit workers
        self.request_counter = 0
        self.error_counter = 0

    async def process_recursive_task(self, algorithm: str, n: int,
                                     use_optimization: bool = True) -> Dict[str, Any]:
        """Process recursive tasks with optimization options"""
        self.request_counter += 1
        request_id = self.request_counter

        logger.info(f"Request {request_id}: Processing {algorithm} with depth {n}, optimized={use_optimization}")

        start_time = time.time()
        tracemalloc.start()

        try:
            # Input validation
            if n <= 0:
                raise ValueError("Depth must be positive")
            if n > 10000 and not use_optimization:
                raise ValueError("Unoptimized recursion depth too high")

            if algorithm == "fibonacci":
                if use_optimization:
                    result = self.recursion_engine.fibonacci_iterative(n)
                else:
                    if n > 35:  # Safe limit for naive Fibonacci
                        raise RecursionError(f"Naive Fibonacci too slow for n={n}")
                    result = self.recursion_engine.fibonacci_naive(n)

            elif algorithm == "tree_traversal":
                tree = self.generate_deep_tree(n)
                if use_optimization:
                    result = self.recursion_engine.tree_traversal_iterative(tree)
                else:
                    if n > 500:  # Safe limit for naive tree traversal
                        raise RecursionError(f"Naive tree traversal too deep for n={n}")
                    result = self.recursion_engine.tree_traversal_naive(tree)

            elif algorithm == "pathfinding":
                grid = self.generate_grid(min(n, 20))  # Limit grid size
                result = self.recursion_engine.pathfinding_naive(grid, 0, 0,
                                                                 min(n - 1, 19), min(n - 1, 19))
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")

            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            execution_time = time.time() - start_time

            # Track metrics
            self.recursion_engine.calculate_recursion_metrics(
                n, execution_time, peak, algorithm, success=True
            )

            logger.info(f"Request {request_id}: Success in {execution_time:.4f}s")

            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "memory_peak": peak,
                "recursion_depth": n,
                "request_id": request_id
            }

        except RecursionError as e:
            tracemalloc.stop()
            self.error_counter += 1
            logger.error(f"Request {request_id}: RecursionError - {str(e)}")

            self.recursion_engine.calculate_recursion_metrics(
                n, time.time() - start_time, 0, algorithm, success=False
            )

            return {
                "success": False,
                "error": f"RecursionError: {str(e)}",
                "execution_time": time.time() - start_time,
                "recursion_depth": n,
                "request_id": request_id
            }
        except Exception as e:
            tracemalloc.stop()
            self.error_counter += 1
            logger.error(f"Request {request_id}: Error - {str(e)}")

            return {
                "success": False,
                "error": f"Error: {str(e)}",
                "execution_time": time.time() - start_time,
                "recursion_depth": n,
                "request_id": request_id
            }

    def generate_deep_tree(self, depth: int) -> Dict:
        """Generate a deep tree for testing"""
        if depth <= 0:
            return {"value": "leaf", "children": []}

        return {
            "value": f"node_{depth}",
            "children": [self.generate_deep_tree(depth - 1)]
        }

    def generate_grid(self, size: int) -> List[List[int]]:
        """Generate a grid for pathfinding"""
        grid = [[0 for _ in range(size)] for _ in range(size)]
        # Add some obstacles
        for i in range(1, size - 1, 2):
            grid[i][size // 2] = 1
        return grid

    async def process_multiple_requests(self, requests: List[Dict]) -> List[Dict]:
        """Process multiple recursive requests with concurrency control"""
        semaphore = asyncio.Semaphore(50)  # Limit concurrent requests

        async def process_with_semaphore(request):
            async with semaphore:
                return await self.process_recursive_task(
                    request['algorithm'],
                    request['depth'],
                    request.get('optimized', True)
                )

        tasks = [process_with_semaphore(req) for req in requests]
        return await asyncio.gather(*tasks)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics"""
        successful_requests = [m for m in self.recursion_engine.recursion_depth_metrics if m['success']]
        failed_requests = [m for m in self.recursion_engine.recursion_depth_metrics if not m['success']]

        execution_times = [m['execution_time'] for m in successful_requests]

        stats = {
            'total_requests': self.request_counter,
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'error_rate': (len(failed_requests) / self.request_counter * 100) if self.request_counter > 0 else 0,
            'avg_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
            'max_execution_time': max(execution_times) if execution_times else 0,
            'system_metrics': self.recursion_engine.get_system_metrics()
        }

        return stats