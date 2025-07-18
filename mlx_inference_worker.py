#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path

# Add MLX to path if needed
sys.path.append('/opt/homebrew/lib/python3.11/site-packages')

def main():
    parser = argparse.ArgumentParser(description='MLX Inference Worker')
    parser.add_argument('--prompt', required=True, help='Input prompt')
    parser.add_argument('--model', required=True, help='Model name')
    parser.add_argument('--max-tokens', type=int, default=500, help='Max tokens')
    args = parser.parse_args()
    
    try:
        # Import MLX (only when actually running)
        import mlx.core as mx
        from mlx_lm import load, generate
        
        print(f"🧠 MLX Worker starting on {os.uname().nodename}")
        print(f"📝 Loading model: {args.model}")
        
        # Load model - DON'T add mlx-community/ prefix since it's already included
        model, tokenizer = load(args.model)  # Use args.model directly
        
        print(f"💭 Generating response for: {args.prompt[:50]}...")
        
        # Generate response
        response = generate(
            model, 
            tokenizer, 
            prompt=args.prompt, 
            max_tokens=args.max_tokens,
            verbose=False
        )
        
        # Output just the response (captured by MPI)
        print(response)
        
    except Exception as e:
        print(f"❌ MLX Worker Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
