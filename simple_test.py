#!/usr/bin/env python3
# simple_test.py

import socket
import time
import sys
import os

def simple_test():
    print(f"🖥️  Node: {socket.gethostname()}")
    print(f"🔧 Python: {sys.version}")
    print(f"📁 Working Dir: {os.getcwd()}")
    print(f"⏰ Time: {time.ctime()}")
    
    # Test basic MLX import
    try:
        import mlx.core as mx
        print("✅ MLX imported successfully")
        
        # Test basic operation
        x = mx.array([1, 2, 3])
        print(f"✅ Basic MLX operation: {x}")
        
    except Exception as e:
        print(f"❌ MLX test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("✅ Simple test passed!")
    else:
        print("❌ Simple test failed!")
