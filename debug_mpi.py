import mlx.core as mx
import socket
import os

def debug_mpi_setup():
    
    print(f"🔍 MPI/MLX Debug Information")
    print(f"Hostname: {socket.gethostname()}")
    print(f"PID: {os.getpid()}")
    
    mpi_vars = ['OMPI_COMM_WORLD_SIZE', 'OMPI_COMM_WORLD_RANK', 'OMPI_UNIVERSE_SIZE']
    for var in mpi_vars:
        value = os.environ.get(var, 'NOT SET')
        print(f"  {var}: {value}")
    
    print("\n🚀 Initializing MLX distributed...")
    
    try:
        mx.set_default_device(mx.cpu)
        world = mx.distributed.init()
        rank = world.rank()
        size = world.size()
        
        print(f"✅ MLX Distributed Initialized")
        print(f"  Rank: {rank}")
        print(f"  Size: {size}")
        print(f"  Expected Size: 3")
        
        if size != 3:
            print(f"❌ ERROR: Expected 3 nodes, got {size}")
        else:
            print(f"✅ Correct node count!")
            
        test_data = mx.array([float(rank)])
        result = mx.distributed.all_sum(test_data)
        print(f"  Test all_sum result: {result}")
        
    except Exception as e:
        print(f"❌ MLX distributed init failed: {e}")

if __name__ == "__main__":
    debug_mpi_setup()
