"""
Thread pool executor for handling database operations.

Instead of using the default executor (which has limited threads),
we create a dedicated pool sized appropriately for our workload.
"""
from concurrent.futures import ThreadPoolExecutor
import os

# Size the thread pool based on CPU cores
# For I/O-bound operations (like database queries), we can use more threads
max_workers = min(32, (os.cpu_count() or 1) * 4)

# Global thread pool executor
# This is reused across all async endpoints to avoid creating/destroying threads
db_executor = ThreadPoolExecutor(
    max_workers=max_workers,
    thread_name_prefix="db_worker"
)


def get_executor():
    """Get the shared database executor instance"""
    return db_executor
