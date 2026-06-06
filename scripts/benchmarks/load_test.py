import time
import asyncio
import aiohttp
import numpy as np
import argparse

async def fetch_query(session, url, query):
    start_time = time.perf_counter()
    try:
        async with session.post(url, json={"query": query, "stream": False}) as response:
            await response.json()
            end_time = time.perf_counter()
            return end_time - start_time
    except Exception as e:
        print(f"Request failed: {e}")
        return None

async def run_load_test(url, queries, concurrent_users):
    async with aiohttp.ClientSession() as session:
        tasks = []
        # Distribute queries across concurrent "users"
        for i in range(concurrent_users):
            query = queries[i % len(queries)]
            tasks.append(fetch_query(session, url, query))
        
        latencies = await asyncio.gather(*tasks)
        return [l for l in latencies if l is not None]

def main():
    parser = argparse.ArgumentParser(description="HybridRAG Load Tester")
    parser.add_argument("--url", default="http://localhost:8000/api/query/ask", help="API Endpoint")
    parser.add_argument("--users", type=int, default=5, help="Concurrent users")
    args = parser.parse_args()

    test_queries = [
        "How does contextual chunking work?",
        "What is Hybrid Retrieval?",
        "Explain LangGraph orchestration.",
        "How to install HybridRAG?",
        "What are the benefits of local RAG?"
    ]

    print(f"🚀 Starting Load Test: {args.users} concurrent users...")
    latencies = asyncio.run(run_load_test(args.url, test_queries, args.users))

    if latencies:
        print("\n--- 📈 Performance Metrics ---")
        print(f"Average Latency: {np.mean(latencies):.2f}s")
        print(f"P95 Latency:     {np.percentile(latencies, 95):.2f}s")
        print(f"Min Latency:     {np.min(latencies):.2f}s")
        print(f"Max Latency:     {np.max(latencies):.2f}s")
        print(f"Throughput:      {len(latencies)/np.sum(latencies):.2f} req/s")
    else:
        print("❌ No successful requests recorded.")

if __name__ == "__main__":
    main()
