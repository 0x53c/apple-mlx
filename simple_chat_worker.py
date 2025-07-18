#!/usr/bin/env python3
# minimal_chat_worker.py

import socket
import argparse

def test_basic_generation():
    """Test basic generation with minimal parameters"""
    try:
        from mlx_lm import load, generate
        
        print("🧠 Loading model...")
        model, tokenizer = load("mlx-community/Llama-3.2-1B-Instruct-4bit")
        print("✅ Model loaded!")
        
        # Test with minimal parameters
        prompt = "Hello, how are you?"
        print(f"🤖 Testing generation with prompt: '{prompt}'")
        
        # Try with just required parameters
        response = generate(model, tokenizer, prompt=prompt)
        print(f"✅ Generation successful!")
        print(f"🎯 Response: {response}")
        
        return True
    except Exception as e:
        print(f"❌ Basic generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_max_tokens():
    """Test generation with max_tokens parameter"""
    try:
        from mlx_lm import load, generate
        
        print("🧠 Loading model...")
        model, tokenizer = load("mlx-community/Llama-3.2-1B-Instruct-4bit")
        print("✅ Model loaded!")
        
        prompt = "Hello, how are you?"
        print(f"🤖 Testing with max_tokens...")
        
        # Try with max_tokens
        response = generate(model, tokenizer, prompt=prompt, max_tokens=50)
        print(f"✅ Generation with max_tokens successful!")
        print(f"🎯 Response: {response}")
        
        return True
    except Exception as e:
        print(f"❌ Generation with max_tokens failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-basic", action="store_true", help="Test basic generation")
    parser.add_argument("--test-max-tokens", action="store_true", help="Test with max_tokens")
    parser.add_argument("--prompt", help="Custom prompt")
    
    args = parser.parse_args()
    
    print(f"🖥️  Minimal Chat Worker on: {socket.gethostname()}")
    
    if args.test_basic:
        test_basic_generation()
    elif args.test_max_tokens:
        test_with_max_tokens()
    elif args.prompt:
        try:
            from mlx_lm import load, generate
            
            print("🧠 Loading model...")
            model, tokenizer = load("mlx-community/Llama-3.2-1B-Instruct-4bit")
            
            print(f"🤖 Generating response for: '{args.prompt}'")
            response = generate(model, tokenizer, prompt=args.prompt, max_tokens=100)
            
            print(f"🎯 Response: {response}")
        except Exception as e:
            print(f"❌ Failed: {e}")
    else:
        print("Use --test-basic, --test-max-tokens, or --prompt 'your message'")

if __name__ == "__main__":
    main()
