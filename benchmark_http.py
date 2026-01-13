#!/usr/bin/env python3
"""
Benchmark HTTP/1.1 vs HTTP/2 Gateway Performance
=================================================
Requires: requests, httpx (with h2 support), and a valid JWT token from auth-service.
"""

import time
import requests
import httpx
import sys
from typing import Tuple

# Configuration
HTTP1_URL = "http://localhost:8005/api/v1"
HTTP2_URL = "https://localhost:8006/api/v1"

# Replace with actual token from login/register
TOKEN = None


def get_token():
    """Get JWT token from auth-service."""
    global TOKEN
    if TOKEN:
        return TOKEN
    
    print("Getting JWT token from auth-service...")
    try:
        # Try login with demo account
        resp = requests.post(
            "http://localhost:8004/api/v1/login",
            json={"username": "nia", "password": "nia12345"},
            timeout=5
        )
        if resp.status_code == 200:
            TOKEN = resp.json().get("access_token")
            print(f"✅ Token: {TOKEN[:30]}...")
            return TOKEN
        else:
            print(f"❌ Login failed: {resp.json()}")
            print("Please register/login first via main.py CLI")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        sys.exit(1)


def test_http1_single(num_requests: int = 10) -> Tuple[float, float]:
    """Test HTTP/1.1: sequential requests (connection reuse)."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    session = requests.Session()
    
    print(f"\n{'='*60}")
    print(f"HTTP/1.1 - {num_requests} Sequential Requests")
    print(f"{'='*60}")
    
    times = []
    start_total = time.time()
    
    for i in range(num_requests):
        start = time.time()
        try:
            resp = session.get(
                f"{HTTP1_URL}/account/info",
                headers=headers,
                timeout=10
            )
            elapsed = time.time() - start
            times.append(elapsed)
            
            status = "✅" if resp.status_code == 200 else "❌"
            print(f"  Request {i+1:2d}: {elapsed*1000:6.2f}ms  {status}")
        except Exception as e:
            print(f"  Request {i+1:2d}: ERROR - {e}")
            return 0, 0
    
    total_time = time.time() - start_total
    avg_time = sum(times) / len(times) if times else 0
    
    session.close()
    
    print(f"\nTotal: {total_time:.2f}s | Avg: {avg_time*1000:.2f}ms per request")
    return total_time, avg_time


def test_http2_single(num_requests: int = 10) -> Tuple[float, float]:
    """Test HTTP/2: sequential requests (multiplexed)."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    print(f"\n{'='*60}")
    print(f"HTTP/2 - {num_requests} Sequential Requests (Multiplexed)")
    print(f"{'='*60}")
    
    times = []
    start_total = time.time()
    
    # Use httpx for HTTP/2 support
    with httpx.Client(
        http2=True,
        verify=False,  # Self-signed cert
        timeout=10
    ) as client:
        for i in range(num_requests):
            start = time.time()
            try:
                resp = client.get(
                    f"{HTTP2_URL}/account/info",
                    headers=headers
                )
                elapsed = time.time() - start
                times.append(elapsed)
                
                status = "✅" if resp.status_code == 200 else "❌"
                print(f"  Request {i+1:2d}: {elapsed*1000:6.2f}ms  {status}")
            except Exception as e:
                print(f"  Request {i+1:2d}: ERROR - {e}")
                return 0, 0
    
    total_time = time.time() - start_total
    avg_time = sum(times) / len(times) if times else 0
    
    print(f"\nTotal: {total_time:.2f}s | Avg: {avg_time*1000:.2f}ms per request")
    return total_time, avg_time


def test_http2_concurrent(num_requests: int = 10) -> Tuple[float, float]:
    """Test HTTP/2: concurrent requests (true multiplexing advantage)."""
    import asyncio
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    print(f"\n{'='*60}")
    print(f"HTTP/2 - {num_requests} Concurrent Requests (Multiplexed)")
    print(f"{'='*60}")
    
    async def run_concurrent():
        times = []
        start_total = time.time()
        
        # Use httpx AsyncClient for HTTP/2 support
        async with httpx.AsyncClient(
            http2=True,
            verify=False,
            timeout=httpx.Timeout(60.0)  # High timeout for slow single-threaded backend
        ) as client:
            async def fetch(i):
                start = time.time()
                try:
                    resp = await client.get(
                        f"{HTTP2_URL}/account/info",
                        headers=headers
                    )
                    elapsed = time.time() - start
                    status = "✅" if resp.status_code == 200 else "❌"
                    print(f"  Request {i+1:2d}: {elapsed*1000:6.2f}ms  {status}")
                    return elapsed
                except Exception as e:
                    elapsed = time.time() - start
                    print(f"  Request {i+1:2d}: ERROR ({elapsed:.2f}s) - {type(e).__name__}: {str(e)[:50]}")
                    return 0
            
            tasks = [fetch(i) for i in range(num_requests)]
            times = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_total
        avg_time = sum(times) / len(times) if times else 0
        
        print(f"\nTotal: {total_time:.2f}s | Avg: {avg_time*1000:.2f}ms per request")
        return total_time, avg_time
    
    try:
        return asyncio.run(run_concurrent())
    except Exception as e:
        print(f"Concurrent test failed: {e}")
        return 0, 0


def main():
    """Run all benchmarks."""
    print("\n" + "="*60)
    print("DANA SERVICE: HTTP/1.1 vs HTTP/2 Benchmark")
    print("="*60)
    print(f"HTTP/1.1 endpoint: {HTTP1_URL}")
    print(f"HTTP/2 endpoint:   {HTTP2_URL}")
    
    # Get token
    get_token()
    
    num_requests = 10
    
    # Test HTTP/1.1
    h1_total, h1_avg = test_http1_single(num_requests)
    
    # Test HTTP/2 sequential
    h2_seq_total, h2_seq_avg = test_http2_single(num_requests)
    
    # Test HTTP/2 concurrent (10 requests with high timeout due to backend bottleneck)
    h2_con_total, h2_con_avg = test_http2_concurrent(num_requests)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"HTTP/1.1 Sequential:       {h1_total:.2f}s (avg {h1_avg*1000:.2f}ms/req)")
    print(f"HTTP/2 Sequential:         {h2_seq_total:.2f}s (avg {h2_seq_avg*1000:.2f}ms/req)")
    print(f"HTTP/2 Concurrent:         {h2_con_total:.2f}s (avg {h2_con_avg*1000:.2f}ms/req)")
    print(f"{'='*60}")
    
    if h1_total > 0:
        speedup_seq = h1_total / h2_seq_total
        print(f"H2 Sequential speedup: {speedup_seq:.2f}x")
    
    if h2_con_total > 0:
        speedup_con = h1_total / h2_con_total
        print(f"H2 Concurrent speedup: {speedup_con:.2f}x")
    
    print("\nNote: HTTP/2 multiplexing advantage is most visible with")
    print("concurrent requests or high-latency connections.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBenchmark cancelled.")
        sys.exit(0)
