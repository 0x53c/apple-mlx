import subprocess
import sys
import os
import time
from pathlib import Path

class MacMiniCluster:
    def __init__(self):
        self.nodes = ["n1", "n2", "n3"]
        self.node_ips = ["192.168.183.173", "192.168.183.158", "192.168.183.122"]  # Original network IPs
        self.remote_base_dir = "/Users/0x53c/cluster_jobs"
        self.git_repo_dir = Path.cwd()
        self.venv_path = "/Users/0x53c/ray-cluster-venv"
        
    def deploy_and_run(self, script_name, job_name=None):
        if job_name is None:
            job_name = f"job_{int(time.time())}"
            
        local_script = self.git_repo_dir / script_name
        if not local_script.exists():
            print(f"❌ Script {script_name} not found in {self.git_repo_dir}")
            return False
        
        print(f"📤 Deploying {script_name} to cluster...")
        
        # Deploy to all nodes
        for node in self.nodes:
            print(f"  📂 Deploying to {node}...")
            result = subprocess.run([
                "scp", str(local_script), 
                f"{node}:{self.remote_base_dir}/"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"    ❌ Failed to deploy to {node}")
                return False
        
        print(f"🚀 Running distributed job: {job_name}")
        
        host_list = ",".join(self.node_ips)
        cluster_command = f"""
        export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
        source {self.venv_path}/bin/activate
        cd {self.remote_base_dir}
        
        echo "🔍 Environment: $(hostname)"
        echo "📍 Python: $(which python3)"
        echo "🔧 MPI: $(which mpirun)"
        echo ""
        
        # Run with the working configuration - use original IPs directly
        /opt/homebrew/bin/mpirun -np 3 --host {host_list} --map-by :OVERSUBSCRIBE python3 {script_name}
        """
        
        result = subprocess.run([
            "ssh", "n1", cluster_command
        ], capture_output=True, text=True, timeout=300)
        
        print("📊 Job Output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Errors:")
            print(result.stderr)
        
        # Save results
        results_file = self.git_repo_dir / f"{job_name}_results.txt"
        with open(results_file, 'w') as f:
            f.write(f"Job: {job_name}\n")
            f.write(f"Script: {script_name}\n")
            f.write(f"Timestamp: {time.ctime()}\n")
            f.write("-" * 50 + "\n")
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
        
        print(f"💾 Results saved to: {results_file}")
        
        return result.returncode == 0

def main():
    cluster = MacMiniCluster()
    
    if len(sys.argv) < 2:
        print("Mac Mini Cluster Manager")
        print("Usage: python3 cluster_manager.py <script_name> [job_name]")
        print("Example: python3 cluster_manager.py thunderbolt_vs_ssh_benchmark.py")
        print("Example: python3 cluster_manager.py cluster_test.py")
        return
    
    script_name = sys.argv[1]
    job_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = cluster.deploy_and_run(script_name, job_name)
    if success:
        print("✅ Distributed job completed successfully!")
    else:
        print("❌ Distributed job failed!")

if __name__ == "__main__":
    main()
