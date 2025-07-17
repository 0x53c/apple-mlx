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

def main():
    cluster = MacMiniClusterThunderboltOptimized()
    
    if len(sys.argv) < 2:
        print("⚡ OPTIMIZED Thunderbolt Mac Mini Cluster")
        print("🚀 SSH Process Management + Thunderbolt Data Transfer")
        print("")
        print("Usage: python3 cluster_manager_thunderbolt_optimized.py <script> [job_name]")
        print("")
        print("🔧 Performance Architecture:")
        print("  📡 Process Launch: SSH (reliable, proven)")
        print("  📊 Data Transfer: Thunderbolt Bridge (high-speed)")
        print("  🎯 Best of both worlds!")
        return
    
    script_name = sys.argv[1]
    job_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = cluster.deploy_and_run(script_name, job_name)
    if success:
        print("✅ OPTIMIZED Thunderbolt job completed!")
    else:
        print("❌ Job failed")

if __name__ == "__main__":
    main()
