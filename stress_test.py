import asyncio
import aiohttp
import time
import statistics
import logging
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StressTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []

    async def make_request(self, session, algorithm: str, depth: int, optimized: bool):
        start_time = time.time()
        try:
            url = f"{self.base_url}/compute/{algorithm}?depth={depth}&optimized={optimized}"
            async with session.post(url, timeout=30) as response:
                result = await response.json()
                execution_time = time.time() - start_time

                return {
                    "success": result.get("success", False),
                    "execution_time": execution_time,
                    "error": result.get("error"),
                    "depth": depth,
                    "optimized": optimized,
                    "algorithm": algorithm,
                    "timestamp": datetime.now().isoformat()
                }

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "execution_time": execution_time,
                "error": "Request timeout",
                "depth": depth,
                "optimized": optimized,
                "algorithm": algorithm,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "execution_time": execution_time,
                "error": str(e),
                "depth": depth,
                "optimized": optimized,
                "algorithm": algorithm,
                "timestamp": datetime.now().isoformat()
            }

    async def run_stress_test(self, num_requests: int, algorithm: str,
                              depth_range: tuple, optimized: bool = False,
                              batch_size: int = 100):
        logger.info(f"Starting stress test: {num_requests} requests, algorithm={algorithm}, optimized={optimized}")

        start_time = time.time()
        connector = aiohttp.TCPConnector(limit=100)  # Limit connections
        async with aiohttp.ClientSession(connector=connector) as session:

            # Process in batches to avoid overwhelming the server
            completed = 0
            batch_results = []

            for batch_start in range(0, num_requests, batch_size):
                batch_end = min(batch_start + batch_size, num_requests)
                batch_size_actual = batch_end - batch_start

                logger.info(
                    f"Processing batch {batch_start // batch_size + 1}/{(num_requests + batch_size - 1) // batch_size}")

                tasks = []
                for i in range(batch_start, batch_end):
                    depth = depth_range[0] + (i % (depth_range[1] - depth_range[0] + 1))
                    task = self.make_request(session, algorithm, depth, optimized)
                    tasks.append(task)

                batch_result = await asyncio.gather(*tasks)
                batch_results.extend(batch_result)
                completed += batch_size_actual

                # Small delay between batches
                await asyncio.sleep(0.1)

        total_time = time.time() - start_time

        # Analyze results
        successful = [r for r in batch_results if r["success"]]
        failed = [r for r in batch_results if not r["success"]]
        execution_times = [r["execution_time"] for r in successful]

        analysis = {
            "total_requests": num_requests,
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / num_requests * 100,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "avg_execution_time": statistics.mean(execution_times) if execution_times else 0,
            "max_execution_time": max(execution_times) if execution_times else 0,
            "min_execution_time": min(execution_times) if execution_times else 0,
            "common_errors": self._analyze_errors(failed),
            "test_timestamp": datetime.now().isoformat()
        }

        self.results.append(analysis)
        self._print_analysis(analysis)
        return analysis

    def _analyze_errors(self, failed_requests):
        error_counts = {}
        for req in failed_requests:
            error = req["error"]
            error_key = error[:100]  # Limit error string length
            error_counts[error_key] = error_counts.get(error_key, 0) + 1
        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5])

    def _print_analysis(self, analysis):
        print("\n" + "=" * 60)
        print("STRESS TEST RESULTS")
        print("=" * 60)
        print(f"Timestamp: {analysis['test_timestamp']}")
        print(f"Total Requests: {analysis['total_requests']}")
        print(f"Successful: {analysis['successful']}")
        print(f"Failed: {analysis['failed']}")
        print(f"Success Rate: {analysis['success_rate']:.2f}%")
        print(f"Total Time: {analysis['total_time']:.2f}s")
        print(f"Requests/Second: {analysis['requests_per_second']:.2f}")
        print(f"Avg Execution Time: {analysis['avg_execution_time']:.4f}s")
        print(f"Max Execution Time: {analysis['max_execution_time']:.4f}s")
        print(f"Min Execution Time: {analysis['min_execution_time']:.4f}s")
        print(f"Top Errors: {analysis['common_errors']}")
        print("=" * 60)


async def main():
    tester = StressTester()

    print("🔴 TEST 1: Unoptimized Fibonacci (5000 requests - EXPECTING FAILURES)")
    print("   This should demonstrate stack overflows and high latency")
    await tester.run_stress_test(5000, "fibonacci", (30, 35), optimized=False, batch_size=50)

    print("\n🟢 TEST 2: Optimized Fibonacci (10000 requests - EXPECTING SUCCESS)")
    print("   This should demonstrate stable performance")
    await tester.run_stress_test(10000, "fibonacci", (30, 35), optimized=True, batch_size=100)

    print("\n🔴 TEST 3: Tree Traversal - Deep Recursion (2000 requests)")
    await tester.run_stress_test(2000, "tree_traversal", (100, 200), optimized=False, batch_size=50)

    print("\n🟢 TEST 4: Tree Traversal - Optimized (3000 requests)")
    await tester.run_stress_test(3000, "tree_traversal", (100, 200), optimized=True, batch_size=100)

    print("\n🔴 TEST 5: Pathfinding - Complex Cases (1000 requests)")
    await tester.run_stress_test(1000, "pathfinding", (8, 12), optimized=False, batch_size=50)


if __name__ == "__main__":
    print("🚀 Starting Comprehensive Stress Tests")
    print("System Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    asyncio.run(main())