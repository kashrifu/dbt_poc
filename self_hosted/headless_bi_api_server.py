"""
Headless BI API Server using dbt MCP

This creates a REST API server that exposes dbt metrics as API endpoints.
Perfect for building custom dashboards, mobile apps, or integrating with other systems.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio
import os
import uvicorn

# MCP client imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("Install MCP client: pip install mcp")
    exit(1)

# Global MCP client session
mcp_session: Optional[ClientSession] = None


class DbtMcpManager:
    """Manages MCP connection lifecycle"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.transport_context = None
        self.project_dir = r"C:\Rif\dbt_poc\metricflow_poc"
        self.profiles_dir = r"C:\Rif\dbt_poc\metricflow_poc"
        # Use Python's dbt module instead of executable to avoid dbt Fusion
        import sys
        self.python_exe = sys.executable  # Use current Python (from venv)
        self.dbt_path = r"C:\Users\Timer\.local\bin\dbt.exe"  # Fallback
    
    async def ensure_connected(self):
        """Ensure MCP connection is established (lazy connection)"""
        if self.session:
            return
        
        await self.connect()
    
    async def connect(self):
        """Connect to dbt MCP server"""
        if self.session:
            return
        
        print(f"  Project dir: {self.project_dir}")
        print(f"  Profiles dir: {self.profiles_dir}")
        print(f"  dbt path: {self.dbt_path}")
        
        # Ensure dbt project is parsed and semantic manifest exists
        import subprocess
        semantic_manifest = os.path.join(self.project_dir, "target", "semantic_manifest.json")
        
        if not os.path.exists(semantic_manifest):
            print("  Parsing dbt project to generate semantic manifest...")
            try:
                result = subprocess.run(
                    [self.dbt_path, "parse", "--quiet"],
                    cwd=self.project_dir,
                    env={**os.environ, "DBT_PROFILES_DIR": self.profiles_dir},
                    capture_output=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print("  ✓ dbt project parsed successfully")
                else:
                    print(f"  ⚠ dbt parse warning (return code: {result.returncode})")
            except Exception as e:
                print(f"  ⚠ Could not parse dbt project: {e}")
                print("  Continuing anyway...")
        else:
            print("  ✓ Semantic manifest found")
        
        # Use current Python executable (from venv) to run dbt-mcp
        server_params = StdioServerParameters(
            command=self.python_exe,
            args=["-m", "dbt_mcp.main"],
            env={
                "DBT_PROJECT_DIR": self.project_dir,
                "DBT_PROFILES_DIR": self.profiles_dir,
                "DBT_PATH": self.dbt_path,
            }
        )
        
        print("  Starting MCP server process...")
        try:
            # stdio_client returns an async context manager
            self.transport_context = stdio_client(server_params)
            print("  Entering transport context...")
            read_stream, write_stream = await asyncio.wait_for(
                self.transport_context.__aenter__(),
                timeout=60.0
            )
            print("  Creating client session...")
            self.session = ClientSession(read_stream, write_stream)
            print("  Initializing session (this may take 2-5 minutes on first run)...")
            print("  The MCP server is parsing your dbt project and loading semantic models...")
            # MCP initialization can take much longer, especially on first run
            # The server needs to parse the dbt project, load semantic models, and initialize LSP
            await asyncio.wait_for(
                self.session.initialize(),
                timeout=300.0  # 5 minutes - first run can be very slow
            )
            print("✓ Connected to dbt MCP server")
        except asyncio.TimeoutError:
            print("✗ Connection timeout - MCP server took too long to respond")
            print("  This might happen on first run. Try again in a moment.")
            raise
        except Exception as e:
            print(f"✗ Connection error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.session:
            await self.session.close()
            self.session = None
        if self.transport_context:
            await self.transport_context.__aexit__(None, None, None)
            self.transport_context = None


manager = DbtMcpManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MCP connection lifecycle"""
    # Startup - Don't connect immediately, use lazy connection
    print("MCP server will connect on first request...")
    
    yield
    
    # Shutdown
    print("Disconnecting from dbt MCP server...")
    try:
        await manager.disconnect()
        print("✓ MCP connection closed")
    except Exception as e:
        print(f"Warning: Error during disconnect: {e}")


app = FastAPI(
    title="dbt Metrics API",
    description="Headless BI API powered by dbt MCP server",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "dbt Metrics API",
        "version": "1.0.0",
        "description": "Headless BI API powered by dbt MCP server",
        "endpoints": {
            "metrics": "/api/metrics",
            "query": "/api/query",
            "sql": "/api/sql",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_connected": manager.session is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/metrics")
async def list_metrics():
    """List all available metrics"""
    try:
        await manager.ensure_connected()
        if not manager.session:
            raise HTTPException(
                status_code=503, 
                detail="MCP server connection failed. Check server logs for details."
            )
        result = await manager.session.call_tool("list_metrics", {})
        metrics = result.content if result else []
        
        return {
            "count": len(metrics),
            "metrics": [
                {
                    "name": m.get("name"),
                    "label": m.get("label"),
                    "description": m.get("description"),
                    "type": m.get("type")
                }
                for m in metrics
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"Error in list_metrics: {error_detail}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/api/query")
async def query_metrics(
    metrics: List[str] = Query(..., description="List of metric names to query"),
    dimensions: Optional[List[str]] = Query(None, description="Dimensions to group by"),
    filters: Optional[str] = Query(None, description="JSON string of filters"),
    limit: Optional[int] = Query(100, description="Maximum rows to return")
):
    """
    Query metrics with optional dimensions and filters
    
    Example:
        POST /api/query?metrics=total_revenue&metrics=total_orders&dimensions=store__store_type
    """
    try:
        await manager.ensure_connected()
        import json
        
        query_params = {"metrics": metrics}
        
        if dimensions:
            query_params["dimensions"] = dimensions
        
        if filters:
            filter_dict = json.loads(filters)
            # Convert filter dict to WHERE clause
            conditions = []
            for key, value in filter_dict.items():
                if isinstance(value, str):
                    conditions.append(f"{{{{ Dimension('{key}') }}}} = '{value}'")
                else:
                    conditions.append(f"{{{{ Dimension('{key}') }}}} = {value}")
            query_params["where"] = " AND ".join(conditions)
        
        if limit:
            query_params["limit"] = limit
        
        result = await manager.session.call_tool("query_metrics", query_params)
        
        return {
            "metrics": metrics,
            "dimensions": dimensions or [],
            "filters": filters,
            "data": result.content if result else {},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/query/revenue")
async def query_revenue(
    dimension: Optional[str] = Query(None, description="Dimension to group by"),
    store_type: Optional[str] = Query(None, description="Filter by store type"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    limit: int = Query(100, description="Maximum rows")
):
    """
    Convenience endpoint for revenue queries
    
    Example:
        GET /api/query/revenue?dimension=store__store_type&store_type=Premium
    """
    try:
        await manager.ensure_connected()
        metrics = ["total_revenue", "completed_revenue", "average_order_value"]
        dimensions = [dimension] if dimension else None
        
        filters = {}
        if store_type:
            filters["store__store_type"] = store_type
        if status:
            filters["order__order_status"] = status
        
        query_params = {"metrics": metrics}
        if dimensions:
            query_params["dimensions"] = dimensions
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{{{{ Dimension('{key}') }}}} = '{value}'")
            query_params["where"] = " AND ".join(conditions)
        if limit:
            query_params["limit"] = limit
        
        result = await manager.session.call_tool("query_metrics", query_params)
        
        return {
            "metrics": metrics,
            "dimension": dimension,
            "filters": filters,
            "data": result.content if result else {},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sql")
async def get_sql(
    metrics: List[str] = Query(..., description="List of metric names"),
    dimensions: Optional[List[str]] = Query(None, description="Dimensions to group by"),
    filters: Optional[str] = Query(None, description="JSON string of filters")
):
    """Get compiled SQL for a metric query"""
    try:
        await manager.ensure_connected()
        import json
        
        query_params = {"metrics": metrics}
        
        if dimensions:
            query_params["dimensions"] = dimensions
        
        if filters:
            filter_dict = json.loads(filters)
            conditions = []
            for key, value in filter_dict.items():
                if isinstance(value, str):
                    conditions.append(f"{{{{ Dimension('{key}') }}}} = '{value}'")
                else:
                    conditions.append(f"{{{{ Dimension('{key}') }}}} = {value}")
            query_params["where"] = " AND ".join(conditions)
        
        result = await manager.session.call_tool("get_metrics_compiled_sql", query_params)
        sql = result.content[0].text if result and result.content else ""
        
        return {
            "sql": sql,
            "metrics": metrics,
            "dimensions": dimensions or [],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/{metric_name}")
async def get_metric_details(metric_name: str):
    """Get details about a specific metric"""
    try:
        await manager.ensure_connected()
        result = await manager.session.call_tool("list_metrics", {})
        metrics = result.content if result else []
        
        metric = next((m for m in metrics if m.get("name") == metric_name), None)
        
        if not metric:
            raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")
        
        return {
            "name": metric.get("name"),
            "label": metric.get("label"),
            "description": metric.get("description"),
            "type": metric.get("type"),
            "details": metric
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting dbt Metrics API Server...")
    print("API Documentation: http://localhost:8000/docs")
    print("API Root: http://localhost:8000/")
    uvicorn.run(app, host="0.0.0.0", port=8000)

