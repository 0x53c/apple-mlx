import subprocess
import sys
import os
import time
from pathlib import Path

class MacMiniClusterThunderboltOptimized:
    
    def __init__(self):
        self.nodes = ["n1", "n2", "n3"]
        self.ssh_ips = ["192.168.183.173", "192.168.183.158", "192.168.183.122"]
        self.thunderbolt_ips = ["169.254.1.1", "169.254.1.2", "169.254.1.3"]
        self.remote_base_dir = "/Users/0x53c/cluster_jobs"
        self.git_repo_dir = Path.cwd()
        self.venv_path = "/Users/0x53c/ray-cluster-venv"
        
    def deploy_script(self, script_name):
        """Deploy script via SSH management network"""
        local_script = self.git_repo_dir / script_name
        if not local_script.exists():
            print(f"❌ Script {script_name} not found")
            return False
        
        print(f"📂 Deploying {script_name} via SSH...")
        for node in self.nodes:
            result = subprocess.run([
                "scp", str(local_script), f"{node}:{self.remote_base_dir}/"
            ], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to deploy to {node}")
                return False
        print("✅ Deployment complete")
        return True
        
    def run_optimized_thunderbolt_job(self, script_name, job_name):
        """Run MPI with SSH process management + Thunderbolt data transfer"""
        print(f"⚡ OPTIMIZED Thunderbolt job: {job_name}")
        print("🚀 Architecture: SSH process launch + Thunderbolt data transfer")
        
        # The magic: SSH hostnames for process management, 
        # Thunderbolt network forced for all MPI data traffic
        cluster_command = f"""
        export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
        source {self.venv_path}/bin/activate
        cd {self.remote_base_dir}
        
        echo "⚡ THUNDERBOLT OPTIMIZED Environment: $(hostname)"
        echo "🔧 Process Management: SSH (reliable)"
        echo "📊 Data Transfer: Thunderbolt Bridge (high-performance)"
        echo "🌐 Thunderbolt IPs: 169.254.1.1, 169.254.1.2, 169.254.1.3"
        echo ""
        
        # Key optimization: Use SSH IPs for launching, force Thunderbolt for data
        /opt/homebrew/bin/mpirun \\
            -np 3 \\
            -H 192.168.183.173,192.168.183.158,192.168.183.122 \\
            --map-by :OVERSUBSCRIBE \\
            --mca btl_tcp_if_include 169.254.1.0/24 \\
            --mca pml ob1 \\
            --mca btl tcp,self \\
            --mca orte_base_help_aggregate 0 \\
            python3 {script_name}
        """
        
        result = subprocess.run([
            "ssh", "n1", cluster_command
        ], capture_output=True, text=True, timeout=600)
        
        return result
        
    def deploy_and_run(self, script_name, job_name=None):
        if job_name is None:
            job_name = f"thunderbolt_optimized_{int(time.time())}"
            
        if not self.deploy_script(script_name):
            return False
            
        result = self.run_optimized_thunderbolt_job(script_name, job_name)
        
        print("📊 OPTIMIZED Thunderbolt Output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Errors/Info:")
            print(result.stderr)
        
        # Save results
        results_file = self.git_repo_dir / f"{job_name}_results.txt"
        with open(results_file, 'w') as f:
            f.write(f"Job: {job_name}\n")
            f.write(f"Architecture: SSH process launch + Thunderbolt data\n")
            f.write(f"Performance: Thunderbolt Bridge optimized\n")
            f.write(f"Timestamp: {time.ctime()}\n")
            f.write("-" * 50 + "\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\nSTDERR:\n")
                f.write(result.stderr)
        
        print(f"💾 Results: {results_file}")
        return result.returncode == 0

    def run_mlx_inference(self, prompt, model_name="llama3.2:latest"):
        print(f"🧠 MLX Inference: {model_name}")
        print(f"💬 Prompt: {prompt[:50]}...")
        escaped_prompt = prompt.replace('"', '\\"').replace('$', '\\$')
        
        inference_command = f"""
        export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
        source {self.venv_path}/bin/activate
        cd {self.remote_base_dir}
        
        echo "🧠 MLX Inference on Thunderbolt cluster"
        /opt/homebrew/bin/mpirun \\
            -np 3 \\
            -H {','.join(self.ssh_ips)} \\
            --map-by :OVERSUBSCRIBE \\
            --mca btl_tcp_if_include 169.254.1.0/24 \\
            --mca pml ob1 \\
            --mca btl tcp,self \\
            --mca orte_base_help_aggregate 0 \\
            --allow-run-as-root \\
            python3 mlx_inference_worker.py --prompt "{escaped_prompt}" --model {model_name}
        """
        
        result = subprocess.run([
            "ssh", "n1", inference_command
        ], capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ MLX inference failed: {result.stderr}")
            return None
        
    def run_mlx_chat(self, prompt, model_name="mlx-community/Llama-3.2-3B-Instruct-4bit", system_prompt=None):
        """Run MLX chat inference with proper argument handling"""
        print(f"🧠 MLX Chat: {model_name}")
        print(f"💬 Prompt: {prompt[:50]}...")
        
        # Escape special characters
        escaped_prompt = prompt.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        system_arg = f'--system "{system_prompt}"' if system_prompt else ""
        
        chat_command = f"""
        export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
        source {self.venv_path}/bin/activate
        cd {self.remote_base_dir}
        
        echo "🧠 MLX Chat on Thunderbolt cluster"
        /opt/homebrew/bin/mpirun \\
            -np 3 \\
            -H {','.join(self.ssh_ips)} \\
            --map-by :OVERSUBSCRIBE \\
            --mca btl_tcp_if_include 169.254.1.0/24 \\
            --mca pml ob1 \\
            --mca btl tcp,self \\
            --mca orte_base_help_aggregate 0 \\
            --allow-run-as-root \\
            python3 mlx_chat_worker.py --prompt "{escaped_prompt}" --model {model_name} {system_arg}
        """
        
        result = subprocess.run([
            "ssh", "n1", chat_command
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Extract the response from the output
            output = result.stdout.strip()
            if "🤖 Response:" in output:
                response = output.split("🤖 Response:")[-1].strip()
                return response
            else:
                return output
        else:
            print(f"❌ MLX chat failed: {result.stderr}")
            return None
        
    def run_simple_chat(self, prompt, use_mock=False):
        """Run simple chat without distributed complexity"""
        print(f"🧠 Simple Chat Test")
        print(f"💬 Prompt: {prompt[:50]}...")
        
        escaped_prompt = prompt.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        mock_flag = "--mock" if use_mock else ""
        
        chat_command = f"""
        export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
        source {self.venv_path}/bin/activate
        cd {self.remote_base_dir}
        
        echo "🧠 Simple Chat Test"
        python3 simple_chat_worker.py --prompt "{escaped_prompt}" {mock_flag}
        """
        
        result = subprocess.run([
            "ssh", "n1", chat_command
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Simple chat successful!")
            print(result.stdout)
            return result.stdout
        else:
            print(f"❌ Simple chat failed: {result.stderr}")
            return None
    def debug_ssh_connection(self):
        """Debug SSH connections to all nodes"""
        print("🔍 Debugging SSH connections...")
        
        for i, (node, ip) in enumerate(zip(self.nodes, self.ssh_ips)):
            print(f"Testing {node} ({ip})...")
            
            result = subprocess.run([
                "ssh", "-o", "ConnectTimeout=5", node, "echo 'SSH OK'; hostname; uptime"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ {node}: {result.stdout.strip()}")
            else:
                print(f"❌ {node}: {result.stderr.strip()}")
    def run_script_with_args(self, script_name, script_args=None, job_name=None):
        """Run script with arguments on the cluster"""
        if job_name is None:
            job_name = f"script_{int(time.time())}"
        
        print(f"🚀 Running {script_name} with args: {script_args}")
        
        # Build the script command with arguments
        args_str = f" {script_args}" if script_args else ""
        
        cluster_command = f"""
        export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
        source {self.venv_path}/bin/activate
        cd {self.remote_base_dir}
        
        echo "🚀 Running script: {script_name}"
        echo "📝 Arguments: {script_args or 'none'}"
        
        # Run on single node first for testing
        python3 {script_name}{args_str}
        """
        
        result = subprocess.run([
            "ssh", "n1", cluster_command
        ], capture_output=True, text=True, timeout=300)
        
        return result

    def run_distributed_script_with_args(self, script_name, script_args=None, job_name=None):   
        """Run script with arguments across all nodes"""
        if job_name is None:
            job_name = f"distributed_{int(time.time())}"
        
        print(f"⚡ Distributed: {script_name} with args: {script_args}")
        
        args_str = f" {script_args}" if script_args else ""
        
        cluster_command = f"""
        export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
        source {self.venv_path}/bin/activate
        cd {self.remote_base_dir}
        
        echo "⚡ DISTRIBUTED: {script_name}"
        echo "📝 Arguments: {script_args or 'none'}"
        
        /opt/homebrew/bin/mpirun \\
            -np 3 \\
            -H {','.join(self.ssh_ips)} \\
            --map-by :OVERSUBSCRIBE \\
            --mca btl_tcp_if_include 169.254.1.0/24 \\
            --mca pml ob1 \\
            --mca btl tcp,self \\
            --mca orte_base_help_aggregate 0 \\
            python3 {script_name}{args_str}
        """
        
        result = subprocess.run([
            "ssh", "n1", cluster_command
        ], capture_output=True, text=True, timeout=300)
        
        return result

def main():
    cluster = MacMiniClusterThunderboltOptimized()
    
    if len(sys.argv) < 2:
        print("⚡ OPTIMIZED Thunderbolt Mac Mini Cluster")
        print("🚀 SSH Process Management + Thunderbolt Data Transfer")
        print("")
        print("Usage:")
        print("  python3 cluster_manager_thunderbolt.py <script>")
        print("  python3 cluster_manager_thunderbolt.py <script> --args 'script arguments'")
        print("  python3 cluster_manager_thunderbolt.py <script> --distributed --args 'script arguments'")
        print("  python3 cluster_manager_thunderbolt.py chat \"your message\"")
        print("  python3 cluster_manager_thunderbolt.py debug")
        print("")
        print("Examples:")
        print("  python3 cluster_manager_thunderbolt.py simple_chat_worker.py --args '--test-mlx'")
        print("  python3 cluster_manager_thunderbolt.py simple_chat_worker.py --args '--prompt \"hello\"'")
        print("  python3 cluster_manager_thunderbolt.py simple_test.py --distributed")
        return
    
    script_name = sys.argv[1]
    
    # Handle special commands
    if script_name == "chat":
        if len(sys.argv) < 3:
            print("❌ Please provide a message for chat")
            return
        message = sys.argv[2]
        # Deploy and run chat (implement this later)
        print(f"💬 Chat: {message}")
        return
    
    if script_name == "debug":
        cluster.debug_ssh_connection()
        return
    
    # Parse arguments
    distributed = False
    script_args = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--distributed":
            distributed = True
        elif sys.argv[i] == "--args" and i + 1 < len(sys.argv):
            script_args = sys.argv[i + 1]
            i += 1
        i += 1
    
    # Deploy the script
    if not cluster.deploy_script(script_name):
        print("❌ Failed to deploy script")
        return
    
    # Run the script
    if distributed:
        result = cluster.run_distributed_script_with_args(script_name, script_args)
    else:
        result = cluster.run_script_with_args(script_name, script_args)
    
    print("📊 Output:")
    print(result.stdout)
    
    if result.stderr:
        print("⚠️  Errors/Info:")
        print(result.stderr)
    
    if result.returncode == 0:
        print("✅ Script completed successfully!")
    else:
        print("❌ Script failed")
    
    def run_distributed_chat(self, prompt, model_name="mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit"):
        print(f"🌐 Distributed Chat: {model_name}")
        print(f"💬 Prompt: {prompt[:50]}...")
        
        escaped_prompt = prompt.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        distributed_command = f"""
        export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
        source {self.venv_path}/bin/activate
        cd {self.remote_base_dir}
        
        echo "🌐 Distributed Chat Inference"
        /opt/homebrew/bin/mpirun \\
            -np 3 \\
            -H {','.join(self.ssh_ips)} \\
            --map-by :OVERSUBSCRIBE \\
            --mca btl_tcp_if_include 169.254.1.0/24 \\
            --mca pml ob1 \\
            --mca btl tcp,self \\
            --mca orte_base_help_aggregate 0 \\
            python3 distributed_chat_worker.py --prompt "{escaped_prompt}" --model {model_name}
        """
        
        result = subprocess.run([
            "ssh", "n1", distributed_command
        ], capture_output=True, text=True, timeout=300)
        
        return result



if __name__ == "__main__":
    main()
