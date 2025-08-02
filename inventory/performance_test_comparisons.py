import time
import random
from inventory.service.inventory_service import InventoryService
from inventory.service.thread_safe_inventory_service import ThreadSafeInventoryService


def benchmark_upsert(inv_class, n_items):
    inv = inv_class()
    start = time.perf_counter()
    for i in range(n_items):
        price = random.random() * 100
        qty = random.randint(1, 100)
        inv.upsert_item(f"item_{i}", price, qty)
    return time.perf_counter() - start


def benchmark_range_queries(inv, n_queries, price_min, price_max):
    # Pre-generate random ranges
    ranges = [(random.uniform(price_min, price_max - 1), random.uniform(price_min + 1, price_max)) for _ in
              range(n_queries)]
    start = time.perf_counter()
    for low, high in ranges:
        inv.range_query_quantity(low, high)
        inv.range_query_value(low, high)
    return time.perf_counter() - start


def benchmark_top_k(inv, k, repeats):
    start = time.perf_counter()
    for _ in range(repeats):
        inv.top_k_by_price(k)
        inv.top_k_by_quantity(k)
    return time.perf_counter() - start


def run_benchmarks(
        n_items=50000,
        n_queries=500,
        top_k=50,
        repeats=50,
        inv_type="thread_safe"
):
    random.seed(0)
    print(f"Original ThreadSafeInventoryService Performance Test")
    print(f"Parameters: {n_items} items, {n_queries} range queries, top-{top_k} x {repeats} repeats\n")

    # Upsert benchmark
    t_upsert = benchmark_upsert(InventoryService, n_items)
    print(f"Upsert: {t_upsert:.4f} seconds for {n_items} items")

    # Prepare instance for queries
    if inv_type == "thread_safe":
        inv = ThreadSafeInventoryService()
    else:
        inv = InventoryService()

    for i in range(n_items):
        price = random.random() * 100
        qty = random.randint(1, 100)
        inv.upsert_item(f"item_{i}", price, qty)

    # Range query benchmark
    t_range = benchmark_range_queries(inv, n_queries, 0, 100)
    print(f"Range Queries: {t_range:.4f} seconds for {n_queries} queries")

    # Top-K benchmark
    t_topk = benchmark_top_k(inv, top_k, repeats)
    print(f"Top-K Queries: {t_topk:.4f} seconds for top-{top_k} x {repeats}")


if __name__ == "__main__":
    print("----------------------- Old Inventory Service Performance Benchmark --------------------------")
    run_benchmarks(
        n_items=100000,
        n_queries=1000,
        top_k=50,
        repeats=50,
        inv_type="non_safe")

    print("----------------------- New Inventory Service Performance Benchmark--------------------------")
    run_benchmarks(
        n_items=100000,
        n_queries=1000,
        top_k=50,
        repeats=50,
        inv_type="thread_safe")
