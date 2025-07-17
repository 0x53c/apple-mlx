#!/usr/bin/env python3

import mlx.core as mx
import socket
import os
import time
import gc

def thunderbolt_benchmark():
    """Thunderbolt optimized benchmark for comparison with SSH"""
    print(f"⚡ THUNDERBOLT BENCHMARK")
    print(f"Hostname: {socket.gethostname()}")
    
    try:
        mx.set_default_device(mx.cpu)
        world = mx.distributed.init()
        rank = world.rank()
        size = world.size()
        
        print(f"✅ Node {rank}/{size} initialized")
        tcp_if = os.environ.get('OMPI_MCA_btl_tcp_if_include', 'DEFAULT')
        print(f"⚡ Network: {tcp_if}")
        
        # Verify we're using Thunderbolt
        if "169.254.1" in tcp_if:
            print(f"🔥 CONFIRMED: Using Thunderbolt Bridge network!")
        else:
            print(f"⚠️  WARNING: May not be using Thunderbolt optimization")
        
        # Test 1: Large Data Transfer
        print(f"\n📊 Test 1: Large Data Transfer")
        large_sizes = [10000, 15000, 20000]
        
        for size_dim in large_sizes:
            print(f"  Node {rank}: Testing {size_dim}x{size_dim} matrix...")
            
            large_data = mx.random.normal([size_dim, size_dim])
            data_size_mb = (size_dim * size_dim * 4) / (1024**2)
            
            start_time = time.time()
            result = mx.distributed.all_sum(large_data)
            end_time = time.time()
            
            transfer_time = end_time - start_time
            total_data_mb = data_size_mb * size
            bandwidth_mbps = total_data_mb / transfer_time
            
            print(f"  Node {rank}: {size_dim}x{size_dim} ({data_size_mb:.1f}MB) - {transfer_time:.3f}s - {bandwidth_mbps:.1f} MB/s")
            
            del large_data, result
            gc.collect()
            time.sleep(0.5)
        
        # Test 2: Sustained Operations
        print(f"\n📊 Test 2: Sustained Operations (30s)")
        
        test_duration = 30
        matrix_size = 12000
        start_time = time.time()
        operation_count = 0
        total_data_transferred = 0
        
        while time.time() - start_time < test_duration:
            data = mx.random.normal([matrix_size, matrix_size])
            data_size_mb = (matrix_size * matrix_size * 4) / (1024**2)
            
            result = mx.distributed.all_sum(data)
            
            operation_count += 1
            total_data_transferred += data_size_mb * size
            
            if operation_count % 5 == 0:
                elapsed = time.time() - start_time
                rate = operation_count / elapsed
                throughput_mbps = total_data_transferred / elapsed
                print(f"  Node {rank}: {operation_count} ops - {rate:.1f} ops/s - {throughput_mbps:.1f} MB/s")
            
            del data, result
            gc.collect()
        
        total_time = time.time() - start_time
        final_rate = operation_count / total_time
        final_throughput = total_data_transferred / total_time
        
        print(f"✅ Node {rank}: Thunderbolt Final - {final_rate:.1f} ops/s - {final_throughput:.1f} MB/s")
        
        # Test 3: Message Storm
        print(f"\n📊 Test 3: Message Storm (500 rapid ops)")
        
        num_ops = 500
        start_time = time.time()
        
        for i in range(num_ops):
            tiny_data = mx.array([float(rank + i)])
            result = mx.distributed.all_sum(tiny_data)
            
            if i % 100 == 0 and i > 0:
                elapsed = time.time() - start_time
                ops_per_sec = i / elapsed
                print(f"  Node {rank}: {i}/{num_ops} ops - {ops_per_sec:.0f} ops/s")
        
        total_time = time.time() - start_time
        final_ops_per_sec = num_ops / total_time
        
        print(f"✅ Node {rank}: Thunderbolt message storm - {final_ops_per_sec:.0f} ops/s")
        
        if rank == 0:
            print(f"\n{'='*50}")
            print(f"⚡ THUNDERBOLT BENCHMARK COMPLETE")
            print(f"Network: {tcp_if}")
            print(f"{'='*50}")
        
    except Exception as e:
        print(f"❌ Thunderbolt benchmark failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    thunderbolt_benchmark()
