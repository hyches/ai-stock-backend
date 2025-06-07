import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import pytest
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def run_benchmarks():
    """Run all benchmark tests and collect results"""
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports/benchmarks")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for the report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"benchmark_report_{timestamp}.json"
    
    # Run benchmarks
    print("Running benchmarks...")
    start_time = time.time()
    
    # Run pytest with benchmark tests
    result = pytest.main([
        "tests/benchmarks/test_performance.py",
        "-v",
        "--capture=no"
    ])
    
    total_time = time.time() - start_time
    
    # Collect results from stdout
    results = {
        "timestamp": timestamp,
        "total_time": total_time,
        "cache": {},
        "database": {},
        "trading_service": {}
    }
    
    # Parse results from stdout
    current_section = None
    for line in sys.stdout:
        if "Cache Performance Results:" in line:
            current_section = "cache"
        elif "Database Performance Results:" in line:
            current_section = "database"
        elif "Trading Service Performance Results:" in line:
            current_section = "trading_service"
        elif ":" in line and current_section:
            key, value = line.strip().split(":")
            results[current_section][key.strip()] = float(value.strip().split()[0])
    
    # Save results to JSON
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nBenchmark results saved to {report_file}")
    return results

def generate_report(results):
    """Generate performance report with visualizations"""
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports/benchmarks")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Create DataFrame from results
    df = pd.DataFrame()
    
    # Add cache results
    cache_df = pd.DataFrame([results["cache"]])
    cache_df["component"] = "Cache"
    df = pd.concat([df, cache_df])
    
    # Add database results
    db_df = pd.DataFrame([results["database"]])
    db_df["component"] = "Database"
    df = pd.concat([df, db_df])
    
    # Add trading service results
    trading_df = pd.DataFrame([results["trading_service"]])
    trading_df["component"] = "Trading Service"
    df = pd.concat([df, trading_df])
    
    # Generate visualizations
    plt.style.use("seaborn")
    
    # Create performance comparison plot
    plt.figure(figsize=(12, 6))
    df_melted = df.melt(id_vars=["component"], var_name="operation", value_name="time_ms")
    sns.barplot(data=df_melted, x="operation", y="time_ms", hue="component")
    plt.title("Performance Comparison Across Components")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(reports_dir / "performance_comparison.png")
    
    # Create component-specific plots
    for component in ["Cache", "Database", "Trading Service"]:
        component_df = df[df["component"] == component]
        plt.figure(figsize=(10, 6))
        component_df_melted = component_df.melt(id_vars=["component"], var_name="operation", value_name="time_ms")
        sns.barplot(data=component_df_melted, x="operation", y="time_ms")
        plt.title(f"{component} Performance")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(reports_dir / f"{component.lower()}_performance.png")
    
    # Generate summary statistics
    summary = {
        "timestamp": results["timestamp"],
        "total_time": results["total_time"],
        "components": {}
    }
    
    for component in ["cache", "database", "trading_service"]:
        component_results = results[component]
        summary["components"][component] = {
            "min": min(component_results.values()),
            "max": max(component_results.values()),
            "avg": sum(component_results.values()) / len(component_results)
        }
    
    # Save summary to JSON
    with open(reports_dir / "benchmark_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\nPerformance report generated successfully!")
    print(f"Reports directory: {reports_dir}")

def main():
    """Main function to run benchmarks and generate report"""
    print("Starting performance benchmarks...")
    results = run_benchmarks()
    generate_report(results)
    print("\nBenchmark process completed!")

if __name__ == "__main__":
    main() 