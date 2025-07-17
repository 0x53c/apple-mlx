import subprocess
import re
import time
import statistics
import json
from datetime import datetime

class PerformanceComparator:
    def __init__(self):
        self.ssh_results = []
        self.thunderbolt_results = []
        
    def run_benchmark(self, cluster_manager, benchmark_script, network_type):
        print(f"\n🚀 Running {network_type} benchmark...")
        print(f"Command: python3 {cluster_manager} {benchmark_script}")
        
        try:
            result = subprocess.run(
                ['python3', cluster_manager, benchmark_script],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                print(f"❌ {network_type} benchmark failed:")
                print(f"STDERR: {result.stderr}")
                return None
                
            output = result.stdout
            print(f"✅ {network_type} benchmark completed")
            
            # Parse the output for performance metrics
            metrics = self.parse_benchmark_output(output, network_type)
            return metrics
            
        except subprocess.TimeoutExpired:
            print(f"❌ {network_type} benchmark timed out")
            return None
        except Exception as e:
            print(f"❌ {network_type} benchmark error: {e}")
            return None
    
    def parse_benchmark_output(self, output, network_type):
        """Extract performance metrics from benchmark output"""
        metrics = {
            'network_type': network_type,
            'timestamp': datetime.now().isoformat(),
            'large_transfer_bandwidth': [],
            'sustained_ops_rate': None,
            'sustained_throughput': None,
            'message_storm_rate': None
        }
        
        lines = output.split('\n')
        
        for line in lines:
            # Parse large data transfer results
            # Format: "Node X: 10000x10000 (381.5MB) - 2.345s - 487.2 MB/s"
            large_transfer_match = re.search(r'(\d+)x\1.*?(\d+\.\d+)\s*MB/s', line)
            if large_transfer_match:
                bandwidth = float(large_transfer_match.group(2))
                metrics['large_transfer_bandwidth'].append(bandwidth)
            
            # Parse sustained operations final results
            # Format: "Node X: SSH Final - 12.3 ops/s - 1234.5 MB/s"
            sustained_match = re.search(r'(SSH|Thunderbolt) Final.*?(\d+\.\d+) ops/s.*?(\d+\.\d+) MB/s', line)
            if sustained_match:
                metrics['sustained_ops_rate'] = float(sustained_match.group(2))
                metrics['sustained_throughput'] = float(sustained_match.group(3))
            
            # Parse message storm results
            # Format: "Node X: SSH message storm - 1234 ops/s"
            storm_match = re.search(r'(SSH|Thunderbolt) message storm.*?(\d+) ops/s', line)
            if storm_match:
                metrics['message_storm_rate'] = float(storm_match.group(2))
        
        return metrics
    
    def calculate_improvements(self):
        """Calculate performance improvements from SSH to Thunderbolt"""
        if not self.ssh_results or not self.thunderbolt_results:
            print("❌ Missing benchmark results for comparison")
            return None
        
        improvements = {}
        
        # Compare large transfer bandwidth
        ssh_bandwidth = statistics.mean([
            bw for run in self.ssh_results 
            for bw in run['large_transfer_bandwidth']
        ]) if any(run['large_transfer_bandwidth'] for run in self.ssh_results) else 0
        
        tb_bandwidth = statistics.mean([
            bw for run in self.thunderbolt_results 
            for bw in run['large_transfer_bandwidth']
        ]) if any(run['large_transfer_bandwidth'] for run in self.thunderbolt_results) else 0
        
        if ssh_bandwidth > 0:
            improvements['large_transfer_bandwidth'] = {
                'ssh_avg': ssh_bandwidth,
                'thunderbolt_avg': tb_bandwidth,
                'improvement_percent': ((tb_bandwidth - ssh_bandwidth) / ssh_bandwidth) * 100
            }
        
        # Compare sustained operations
        ssh_ops = statistics.mean([
            run['sustained_ops_rate'] for run in self.ssh_results 
            if run['sustained_ops_rate'] is not None
        ]) if any(run['sustained_ops_rate'] for run in self.ssh_results) else 0
        
        tb_ops = statistics.mean([
            run['sustained_ops_rate'] for run in self.thunderbolt_results 
            if run['sustained_ops_rate'] is not None
        ]) if any(run['sustained_ops_rate'] for run in self.thunderbolt_results) else 0
        
        if ssh_ops > 0:
            improvements['sustained_ops_rate'] = {
                'ssh_avg': ssh_ops,
                'thunderbolt_avg': tb_ops,
                'improvement_percent': ((tb_ops - ssh_ops) / ssh_ops) * 100
            }
        
        # Compare sustained throughput
        ssh_throughput = statistics.mean([
            run['sustained_throughput'] for run in self.ssh_results 
            if run['sustained_throughput'] is not None
        ]) if any(run['sustained_throughput'] for run in self.ssh_results) else 0
        
        tb_throughput = statistics.mean([
            run['sustained_throughput'] for run in self.thunderbolt_results 
            if run['sustained_throughput'] is not None
        ]) if any(run['sustained_throughput'] for run in self.thunderbolt_results) else 0
        
        if ssh_throughput > 0:
            improvements['sustained_throughput'] = {
                'ssh_avg': ssh_throughput,
                'thunderbolt_avg': tb_throughput,
                'improvement_percent': ((tb_throughput - ssh_throughput) / ssh_throughput) * 100
            }
        
        # Compare message storm rate
        ssh_storm = statistics.mean([
            run['message_storm_rate'] for run in self.ssh_results 
            if run['message_storm_rate'] is not None
        ]) if any(run['message_storm_rate'] for run in self.ssh_results) else 0
        
        tb_storm = statistics.mean([
            run['message_storm_rate'] for run in self.thunderbolt_results 
            if run['message_storm_rate'] is not None
        ]) if any(run['message_storm_rate'] for run in self.thunderbolt_results) else 0
        
        if ssh_storm > 0:
            improvements['message_storm_rate'] = {
                'ssh_avg': ssh_storm,
                'thunderbolt_avg': tb_storm,
                'improvement_percent': ((tb_storm - ssh_storm) / ssh_storm) * 100
            }
        
        return improvements
    
    def print_comparison_report(self, improvements):
        """Print a detailed comparison report"""
        print(f"\n{'='*70}")
        print(f"🔍 SSH vs THUNDERBOLT PERFORMANCE COMPARISON REPORT")
        print(f"{'='*70}")
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔢 SSH Runs: {len(self.ssh_results)}")
        print(f"⚡ Thunderbolt Runs: {len(self.thunderbolt_results)}")
        print(f"{'='*70}")
        
        if not improvements:
            print("❌ No performance data available for comparison")
            return
        
        overall_improvements = []
        
        for metric_name, data in improvements.items():
            improvement = data['improvement_percent']
            overall_improvements.append(improvement)
            
            print(f"\n📊 {metric_name.replace('_', ' ').title()}")
            print(f"  🔗 SSH Average:        {data['ssh_avg']:.2f}")
            print(f"  ⚡ Thunderbolt Average: {data['thunderbolt_avg']:.2f}")
            
            if improvement > 0:
                print(f"  ✅ Improvement:        +{improvement:.2f}%")
            elif improvement < 0:
                print(f"  ❌ Regression:         {improvement:.2f}%")
            else:
                print(f"  ➖ No Change:          {improvement:.2f}%")
        
        if overall_improvements:
            avg_improvement = statistics.mean(overall_improvements)
            print(f"\n{'='*70}")
            print(f"📈 OVERALL AVERAGE IMPROVEMENT: {avg_improvement:.2f}%")
            
            if avg_improvement > 5:
                print(f"🚀 EXCELLENT: Thunderbolt shows significant improvement!")
            elif avg_improvement > 1:
                print(f"✅ GOOD: Thunderbolt shows measurable improvement")
            elif avg_improvement > -1:
                print(f"➖ NEUTRAL: Performance is roughly equivalent")
            else:
                print(f"⚠️  CONCERN: SSH may be performing better")
            
            print(f"{'='*70}")
    
    def save_results(self, filename="performance_comparison.json"):
        """Save results to JSON file"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'ssh_results': self.ssh_results,
            'thunderbolt_results': self.thunderbolt_results,
            'improvements': self.calculate_improvements()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Results saved to {filename}")
    
    def run_comparison(self, num_runs=3):
        """Run complete comparison with multiple runs for accuracy"""
        print(f"🎯 Starting SSH vs Thunderbolt Performance Comparison")
        print(f"🔄 Running {num_runs} iterations of each benchmark")
        
        # Run SSH benchmarks
        for i in range(num_runs):
            print(f"\n📡 SSH Benchmark Run {i+1}/{num_runs}")
            result = self.run_benchmark(
                'cluster_manager.py', 
                'ssh_baseline_benchmark.py', 
                'SSH'
            )
            if result:
                self.ssh_results.append(result)
            time.sleep(5)  # Brief pause between runs
        
        # Run Thunderbolt benchmarks
        for i in range(num_runs):
            print(f"\n⚡ Thunderbolt Benchmark Run {i+1}/{num_runs}")
            result = self.run_benchmark(
                'cluster_manager_thunderbolt.py', 
                'thunderbolt_benchmark.py', 
                'Thunderbolt'
            )
            if result:
                self.thunderbolt_results.append(result)
            time.sleep(5)  # Brief pause between runs
        
        # Calculate and display results
        improvements = self.calculate_improvements()
        self.print_comparison_report(improvements)
        self.save_results()

def main():
    print("🚀 MLX Distributed Performance Comparator")
    print("This script will run SSH and Thunderbolt benchmarks and calculate differences")
    
    # Allow user to choose number of runs
    try:
        num_runs = int(input("\nEnter number of benchmark runs per network type (default 3): ") or "3")
        if num_runs < 1:
            num_runs = 1
    except ValueError:
        num_runs = 3
    
    comparator = PerformanceComparator()
    comparator.run_comparison(num_runs)

if __name__ == "__main__":
    main()
