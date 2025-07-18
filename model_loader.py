import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load
import socket
import json
import argparse
import os

class DistributedModelManager:
    def __init__(self, model_path="mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit"):
        self.model_path = model_path
        self.world = None
        self.rank = None
        self.size = None
        self.hostname = socket.gethostname()
        
    def initialize_distributed(self):
        """Initialize distributed MLX"""
        try:
            self.world = mx.distributed.init()
            self.rank = self.world.rank()
            self.size = self.world.size()
            
            print(f"🌐 Node {self.rank}/{self.size} ({self.hostname}) initialized")
            return True
        except Exception as e:
            print(f"❌ Distributed init failed: {e}")
            return False
    
    def inspect_model_structure(self, model):
        """Inspect MLX model structure"""
        try:
            print(f"🔍 Inspecting model structure on rank {self.rank}")
            
            # Check if it's a container with modules
            if hasattr(model, 'modules'):
                modules = model.modules()
                print(f"📊 Model has {len(modules)} modules")
                
                for i, (name, module) in enumerate(modules.items()):
                    print(f"  Module {i}: {name} -> {type(module).__name__}")
                    if i >= 5:  # Show first 5 modules
                        print(f"  ... and {len(modules) - 5} more modules")
                        break
            
            # Check model attributes
            print(f"📋 Model attributes:")
            for attr in dir(model):
                if not attr.startswith('_') and not callable(getattr(model, attr)):
                    try:
                        value = getattr(model, attr)
                        print(f"  {attr}: {type(value).__name__}")
                    except:
                        print(f"  {attr}: <inaccessible>")
            
            # Try to get model parameters
            if hasattr(model, 'parameters'):
                params = model.parameters()
                print(f"📊 Model has {len(params)} parameters")
                
                total_params = 0
                for name, param in params.items():
                    if hasattr(param, 'shape'):
                        param_count = 1
                        for dim in param.shape:
                            param_count *= dim
                        total_params += param_count
                        
                        if len(name) < 50:  # Show shorter names
                            print(f"  {name}: {param.shape}")
                
                print(f"📊 Total parameters: {total_params:,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Model inspection failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_model_distributed(self):
        """Load model with distributed strategy"""
        try:
            if self.rank == 0:
                print(f"📥 Rank 0 downloading model: {self.model_path}")
                # Only rank 0 downloads the model
                model, tokenizer = load(self.model_path)
                print(f"✅ Model downloaded and loaded on rank 0")
                
                # Inspect the model structure
                self.inspect_model_structure(model)
                
            else:
                print(f"⏳ Rank {self.rank} waiting for model distribution...")
                model, tokenizer = None, None
            
            # Synchronize all ranks
            mx.distributed.barrier()
            
            if self.rank == 0:
                print("🔄 Broadcasting model info to other ranks...")
            
            # Non-rank-0 nodes load from cache (much faster)
            if self.rank != 0:
                print(f"📦 Rank {self.rank} loading from cache...")
                model, tokenizer = load(self.model_path)
                print(f"✅ Rank {self.rank} loaded from cache")
            
            return model, tokenizer
            
        except Exception as e:
            print(f"❌ Distributed loading failed: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def create_distributed_strategy(self, model):
        """Create a distributed inference strategy"""
        if not model:
            return None
        
        try:
            # Simple strategy: divide work by rank
            if self.rank == 0:
                role = "tokenizer_and_embeddings"
                print(f"🔧 Rank 0: Handling tokenization and input embeddings")
            elif self.rank == 1:
                role = "transformer_layers"
                print(f"🔧 Rank 1: Handling transformer computations")
            elif self.rank == 2:
                role = "output_and_generation"
                print(f"🔧 Rank 2: Handling output layers and generation")
            else:
                role = "auxiliary"
                print(f"🔧 Rank {self.rank}: Auxiliary processing")
            
            return {
                "rank": self.rank,
                "role": role,
                "model": model,
                "nodes": self.size
            }
            
        except Exception as e:
            print(f"❌ Strategy creation failed: {e}")
            return None

def test_distributed_loading():
    """Test distributed model loading"""
    manager = DistributedModelManager()
    
    if not manager.initialize_distributed():
        return False
    
    print(f"🧪 Testing distributed loading on rank {manager.rank}")
    
    # Load model
    model, tokenizer = manager.load_model_distributed()
    
    if model and tokenizer:
        print(f"✅ Rank {manager.rank} has model loaded")
        
        # Create distributed strategy
        strategy = manager.create_distributed_strategy(model)
        if strategy:
            print(f"📊 Rank {manager.rank} strategy: {strategy['role']}")
        
        # Test simple distributed operation
        test_input = mx.array([float(manager.rank + 1)])
        result = mx.distributed.all_sum(test_input)
        print(f"🔗 Rank {manager.rank} distributed test: {result}")
        
        if manager.rank == 0:
            print("🤖 Testing simple generation on rank 0...")
            try:
                from mlx_lm import generate
                simple_prompt = "Hello"
                response = generate(model, tokenizer, prompt=simple_prompt, max_tokens=10, verbose=False)
                print(f"🎯 Simple generation result: {response[:50]}...")
            except Exception as e:
                print(f"⚠️ Generation test failed: {e}")
        
        return True
    else:
        print(f"❌ Rank {manager.rank} failed to load model")
        return False

def test_model_info():
    try:
        print("🔍 Can this model be extracted?...")
        from mlx_lm import load
        
        model, tokenizer = load("mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit")
        
        print(f"✅ Model loaded successfully")
        print(f"📊 Model type: {type(model).__name__}")
        print(f"📊 Tokenizer type: {type(tokenizer).__name__}")
        
        if hasattr(model, 'modules'):
            modules = model.modules()
            print(f"📊 Model modules: {len(modules)}")
            for name, module in list(modules.items())[:3]:
                print(f"  {name}: {type(module).__name__}")
        
        if hasattr(tokenizer, 'vocab_size'):
            print(f"📊 Vocab size: {tokenizer.vocab_size}")
        
        test_text = "Hello world"
        if hasattr(tokenizer, 'encode'):
            tokens = tokenizer.encode(test_text)
            print(f"📊 Test encoding: '{test_text}' -> {tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model info test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit")
    parser.add_argument("--test", action="store_true", help="Test distributed loading")
    parser.add_argument("--info", action="store_true", help="Test model info only")
    
    args = parser.parse_args()
    
    if args.info:
        success = test_model_info()
        if success:
            print("✅ Model info test passed!")
        else:
            print("❌ Model info test failed!")
    elif args.test:
        success = test_distributed_loading()
        if success:
            print("✅ Distributed loading test passed!")
        else:
            print("❌ Distributed loading test failed!")
    else:
        print("Use --test for distributed loading or --info for model info")

if __name__ == "__main__":
    main()
