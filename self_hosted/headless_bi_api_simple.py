"""
Simplified Headless BI API Server

This version uses dbt CLI commands directly instead of MCP server,
as a workaround for MCP connection initialization issues.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import subprocess
import json
import os

app = FastAPI(
    title="dbt Metrics API (Simple)",
    description="Headless BI API using dbt CLI directly",
    version="1.0.0"
)

PROJECT_DIR = r"C:\Rif\dbt_poc\metricflow_poc"
PROFILES_DIR = r"C:\Rif\dbt_poc\metricflow_poc"
DBT_PATH = r"C:\Users\Timer\.local\bin\dbt.exe"


def run_dbt_command(args: List[str]) -> dict:
    """Run a dbt command and return the result"""
    try:
        env = os.environ.copy()
        env["DBT_PROFILES_DIR"] = PROFILES_DIR
        
        result = subprocess.run(
            [DBT_PATH] + args,
            cwd=PROJECT_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_metrics_from_manifest() -> List[dict]:
    """Extract metrics from semantic manifest"""
    semantic_manifest_path = os.path.join(PROJECT_DIR, "target", "semantic_manifest.json")
    
    if not os.path.exists(semantic_manifest_path):
        # Parse the project first to generate semantic manifest
        print("Semantic manifest not found, parsing dbt project...")
        run_dbt_command(["parse"])
    
    try:
        with open(semantic_manifest_path, 'r', encoding='utf-8') as f:
            semantic_manifest = json.load(f)
        
        metrics = []
        if "metrics" in semantic_manifest:
            for metric_data in semantic_manifest["metrics"]:
                metrics.append({
                    "name": metric_data.get("name", "unknown"),
                    "label": metric_data.get("label", metric_data.get("name", "unknown")),
                    "description": metric_data.get("description", ""),
                    "type": metric_data.get("type", "unknown")
                })
        
        return metrics
    except FileNotFoundError:
        print(f"Semantic manifest not found at: {semantic_manifest_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing semantic manifest: {e}")
        return []
    except Exception as e:
        print(f"Error reading metrics: {e}")
        import traceback
        traceback.print_exc()
        return []


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "dbt Metrics API (Simple)",
        "version": "1.0.0",
        "description": "Headless BI API using dbt CLI directly",
        "note": "This is a simplified version that uses dbt CLI instead of MCP server",
        "endpoints": {
            "metrics": "/api/metrics",
            "health": "/api/health",
            "parse": "/api/parse"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dbt_path": DBT_PATH,
        "project_dir": PROJECT_DIR
    }


@app.get("/api/metrics")
async def list_metrics():
    """List all available metrics"""
    try:
        # Ensure project is parsed
        parse_result = run_dbt_command(["parse", "--quiet"])
        
        if not parse_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse dbt project: {parse_result.get('stderr', 'Unknown error')}"
            )
        
        metrics = get_metrics_from_manifest()
        
        return {
            "count": len(metrics),
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/parse")
async def parse_project():
    """Parse the dbt project"""
    result = run_dbt_command(["parse"])
    
    return {
        "success": result["success"],
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/query")
async def query_metrics_simple(
    metric: str = Query(..., description="Metric name to query"),
    dimension: Optional[str] = Query(None, description="Dimension to group by")
):
    """
    Query a metric using MetricFlow CLI
    
    Note: This is a simplified version. For full functionality, use the MCP server version.
    """
    try:
        # Build mf query command
        cmd = ["mf", "query", "--metrics", metric]
        
        if dimension:
            cmd.extend(["--group-by", dimension])
        
        # Run the command
        result = run_dbt_command(cmd)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Query failed: {result.get('stderr', 'Unknown error')}"
            )
        
        return {
            "metric": metric,
            "dimension": dimension,
            "result": result["stdout"],
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("Starting dbt Metrics API Server (Simple Version)...")
    print("API Documentation: http://localhost:8000/docs")
    print("API Root: http://localhost:8000/")
    uvicorn.run(app, host="0.0.0.0", port=8000)

