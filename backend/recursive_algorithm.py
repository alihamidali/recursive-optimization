import tracemalloc
import time
import sys
import asyncio
import psutil
import os
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecursiveAlgorithms:
    def __init__(self):
        self.memo = {}
        self.recursion_depth_metrics = []
        self.max_recursion_depth = sys.getrecursionlimit() - 50

    def fibonacci_naive(self, n: int) -> int:
        """Naive recursive Fibonacci - demonstrates exponential time complexity"""
        if n < 0:
            raise ValueError("Fibonacci not defined for negative numbers")
        if n <= 1:
            return n

        # Track recursion depth for monitoring
        current_depth = len(sys._getframe(1).f_back.f_back.f_code.co_names) if hasattr(sys, '_getframe') else 0
        if current_depth > self.max_recursion_depth:
            raise RecursionError(f"Approaching recursion limit at depth {current_depth}")

        return self.fibonacci_naive(n - 1) + self.fibonacci_naive(n - 2)

    def fibonacci_memoized(self, n: int, depth: int = 0) -> int:
        """Memoized Fibonacci - optimized version"""
        if depth > 1000:  # Safety check
            raise RecursionError("Maximum safe recursion depth exceeded")

        if n < 0:
            raise ValueError("Fibonacci not defined for negative numbers")
        if n in self.memo:
            return self.memo[n]
        if n <= 1:
            return n

        result = self.fibonacci_memoized(n - 1, depth + 1) + self.fibonacci_memoized(n - 2, depth + 1)
        self.memo[n] = result
        return result

    def fibonacci_iterative(self, n: int) -> int:
        """Iterative Fibonacci - avoids recursion limits"""
        if n < 0:
            raise ValueError("Fibonacci not defined for negative numbers")
        if n <= 1:
            return n

        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def tree_traversal_naive(self, node: Dict, depth: int = 0) -> List:
        """Naive tree traversal - can cause stack overflow"""
        if depth > 1000:  # Artificial limit to prevent infinite recursion
            raise RecursionError("Maximum recursion depth exceeded")

        results = [node.get('value')]

        for child in node.get('children', []):
            results.extend(self.tree_traversal_naive(child, depth + 1))

        return results

    def tree_traversal_iterative(self, root: Dict) -> List:
        """Iterative tree traversal using stack"""
        if not root:
            return []

        stack = [root]
        results = []

        while stack:
            node = stack.pop()
            results.append(node.get('value'))

            # Add children in reverse order for DFS
            for child in reversed(node.get('children', [])):
                stack.append(child)

        return results

    def pathfinding_naive(self, grid: List[List[int]], x: int, y: int,
                          target_x: int, target_y: int, path: List = None,
                          depth: int = 0) -> List:
        """Naive pathfinding that can cause infinite loops"""
        if depth > 1000:
            raise RecursionError("Pathfinding recursion depth exceeded")

        if path is None:
            path = []

        # Check for infinite loops
        if (x, y) in path:
            return []  # Already visited this cell

        # Boundary checks
        if (x < 0 or x >= len(grid) or y < 0 or y >= len(grid[0]) or
                grid[x][y] == 1):  # 1 represents obstacle
            return []

        current_path = path + [(x, y)]

        # Base case: reached target
        if x == target_x and y == target_y:
            return current_path

        # Explore neighbors (this can create exponential paths)
        paths = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_path = self.pathfinding_naive(grid, x + dx, y + dy,
                                              target_x, target_y, current_path, depth + 1)
            if new_path:
                paths.append(new_path)

        return min(paths, key=len) if paths else []

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            'memory_rss': memory_info.rss,
            'memory_vms': memory_info.vms,
            'cpu_percent': process.cpu_percent(),
            'thread_count': process.num_threads(),
            'recursion_metrics_count': len(self.recursion_depth_metrics)
        }

    def calculate_recursion_metrics(self, n: int, execution_time: float,
                                    memory_usage: int, algorithm: str, success: bool = True):
        """Track performance metrics for each recursion call"""
        metric = {
            'timestamp': time.time(),
            'datetime': time.strftime('%Y-%m-%d %H:%M:%S'),
            'recursion_depth': n,
            'execution_time': execution_time,
            'memory_usage': memory_usage,
            'algorithm': algorithm,
            'success': success,
            'system_metrics': self.get_system_metrics()
        }
        self.recursion_depth_metrics.append(metric)
        logger.info(f"Recursion metric: depth={n}, time={execution_time:.4f}s, memory={memory_usage}")

    def clear_metrics(self):
        """Clear stored metrics"""
        self.recursion_depth_metrics.clear()
        self.memo.clear()