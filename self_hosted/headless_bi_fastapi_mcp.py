"""
FastAPI Consumption Layer over dbt-MCP (stdio-based)

Responsibilities:
- Expose dbt semantic layer over HTTP
- Delegate ALL computation to dbt-MCP
- Return dbt/MetricFlow-generated SQL & metadata
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import asyncio
import sys

# MCP imports (stdio mode)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# -----------------------------
# Configuration
# -----------------------------

PROJECT_DIR = r"C:\Rif\dbt_poc\metricflow_poc"
PROFILES_DIR = r"C:\Rif\dbt_poc\metricflow_poc"
DBT_PATH = r"C:\Users\Timer\.local\bin\dbt.exe"

MCP_INIT_TIMEOUT_SECONDS = 900  # 15 minutes (first run)

# -----------------------------
# Global MCP State
# -----------------------------

mcp_session: Optional[ClientSession] = None
mcp_transport = None

# -----------------------------
# Request Models
# -----------------------------

class MetricSQLRequest(BaseModel):
    metric_names: List[str]
    dimensions: Optional[List[str]] = None
    time_granularity: Optional[str] = None
    where: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None


class ValidateDimensionsRequest(BaseModel):
    metric_name: str
    dimensions: List[str]

# -----------------------------
# MCP Connection Handling
# -----------------------------

async def connect_mcp():
    """Start and initialize dbt-MCP via stdio (lazy)."""
    global mcp_session, mcp_transport

    if mcp_session:
        return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "dbt_mcp.main"],
        env={
            "DBT_PROJECT_DIR": PROJECT_DIR,
            "DBT_PROFILES_DIR": PROFILES_DIR,
            "DBT_PATH": DBT_PATH,
        },
    )

    print("Connecting to dbt-MCP server...")
    mcp_transport = stdio_client(server_params)

    read_stream, write_stream = await mcp_transport.__aenter__()
    mcp_session = ClientSession(read_stream, write_stream)

    print("Initializing MCP session (first run may take several minutes)...")
    await asyncio.wait_for(
        mcp_session.initialize(),
        timeout=MCP_INIT_TIMEOUT_SECONDS,
    )

    print("✓ dbt-MCP connected and ready")


async def disconnect_mcp():
    """Gracefully shut down MCP."""
    global mcp_session, mcp_transport

    if mcp_transport:
        await mcp_transport.__aexit__(None, None, None)

    mcp_transport = None
    mcp_session = None


async def ensure_mcp():
    if not mcp_session:
        await connect_mcp()
    if not mcp_session:
        raise HTTPException(status_code=503, detail="dbt-MCP not available")

# -----------------------------
# FastAPI Lifecycle
# -----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI starting (MCP will connect on first request)...")
    yield
    await disconnect_mcp()

app = FastAPI(
    title="dbt MCP Semantic API",
    description="Headless semantic layer powered by dbt-MCP",
    version="1.0.0",
    lifespan=lifespan,
)

# -----------------------------
# Health
# -----------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mcp_connected": mcp_session is not None,
        "project_dir": PROJECT_DIR,
    }

# -----------------------------
# MetricFlow APIs
# -----------------------------

@app.get("/metrics")
async def list_metrics():
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "metricflow.list_metrics",
        {},
    )
    return {
        "metrics": result.content if result else [],
        "count": len(result.content) if result else 0,
    }


@app.get("/metrics/{metric_name}")
async def get_metric(metric_name: str):
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "metricflow.get_metric",
        {"metric_name": metric_name},
    )
    if not result or not result.content:
        raise HTTPException(status_code=404, detail="Metric not found")
    return result.content


@app.post("/metrics/sql")
async def generate_metric_sql(req: MetricSQLRequest):
    await ensure_mcp()

    payload = {
        "metric_names": req.metric_names,
        "dimensions": req.dimensions,
        "time_granularity": req.time_granularity,
        "where": req.where,
        "limit": req.limit,
    }

    payload = {k: v for k, v in payload.items() if v is not None}

    result = await mcp_session.call_tool(
        "metricflow.generate_sql",
        payload,
    )

    if not result or not result.content:
        raise HTTPException(status_code=400, detail="SQL generation failed")

    return {"sql": result.content}


@app.post("/metrics/validate-dimensions")
async def validate_dimensions(req: ValidateDimensionsRequest):
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "metricflow.validate_dimensions",
        {
            "metric_name": req.metric_name,
            "dimensions": req.dimensions,
        },
    )
    return result.content

# -----------------------------
# Semantic Models
# -----------------------------

@app.get("/semantic-models")
async def list_semantic_models():
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "metricflow.list_semantic_models",
        {},
    )
    return result.content if result else []

# -----------------------------
# dbt Metadata APIs
# -----------------------------

@app.get("/dbt/models")
async def list_models():
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "dbt.list_models",
        {},
    )
    return result.content if result else []


@app.get("/dbt/models/{model_name}")
async def get_model(model_name: str):
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "dbt.get_model",
        {"model_name": model_name},
    )
    if not result or not result.content:
        raise HTTPException(status_code=404, detail="Model not found")
    return result.content


@app.get("/dbt/sources")
async def list_sources():
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "dbt.list_sources",
        {},
    )
    return result.content if result else []


@app.get("/dbt/lineage/{model_name}")
async def get_lineage(model_name: str):
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "dbt.get_lineage",
        {"model_name": model_name},
    )
    return result.content if result else []

# -----------------------------
# Entrypoint
# -----------------------------

if __name__ == "__main__":
    import uvicorn

    print("Starting dbt MCP Semantic API")
    print("→ http://localhost:8080")
    print("→ MCP will initialize on first request")

    uvicorn.run(app, host="0.0.0.0", port=8080)
"""
FastAPI Consumption Layer over dbt-MCP (stdio-based)

Responsibilities:
- Expose dbt semantic layer over HTTP
- Delegate ALL computation to dbt-MCP
- Return dbt/MetricFlow-generated SQL & metadata
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import asyncio
import sys

# MCP imports (stdio mode)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# -----------------------------
# Configuration
# -----------------------------

PROJECT_DIR = r"C:\Rif\dbt_poc\metricflow_poc"
PROFILES_DIR = r"C:\Rif\dbt_poc\metricflow_poc"
DBT_PATH = r"C:\Users\Timer\.local\bin\dbt.exe"

MCP_INIT_TIMEOUT_SECONDS = 900  # 15 minutes (first run)

# -----------------------------
# Global MCP State
# -----------------------------

mcp_session: Optional[ClientSession] = None
mcp_transport = None

# -----------------------------
# Request Models
# -----------------------------

class MetricSQLRequest(BaseModel):
    metric_names: List[str]
    dimensions: Optional[List[str]] = None
    time_granularity: Optional[str] = None
    where: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None


class ValidateDimensionsRequest(BaseModel):
    metric_name: str
    dimensions: List[str]

# -----------------------------
# MCP Connection Handling
# -----------------------------

async def connect_mcp():
    """Start and initialize dbt-MCP via stdio (lazy)."""
    global mcp_session, mcp_transport

    if mcp_session:
        return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "dbt_mcp.main"],
        env={
            "DBT_PROJECT_DIR": PROJECT_DIR,
            "DBT_PROFILES_DIR": PROFILES_DIR,
            "DBT_PATH": DBT_PATH,
        },
    )

    print("Connecting to dbt-MCP server...")
    mcp_transport = stdio_client(server_params)

    read_stream, write_stream = await mcp_transport.__aenter__()
    mcp_session = ClientSession(read_stream, write_stream)

    print("Initializing MCP session (first run may take several minutes)...")
    await asyncio.wait_for(
        mcp_session.initialize(),
        timeout=MCP_INIT_TIMEOUT_SECONDS,
    )

    print("✓ dbt-MCP connected and ready")


async def disconnect_mcp():
    """Gracefully shut down MCP."""
    global mcp_session, mcp_transport

    if mcp_transport:
        await mcp_transport.__aexit__(None, None, None)

    mcp_transport = None
    mcp_session = None


async def ensure_mcp():
    if not mcp_session:
        await connect_mcp()
    if not mcp_session:
        raise HTTPException(status_code=503, detail="dbt-MCP not available")

# -----------------------------
# FastAPI Lifecycle
# -----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI starting (MCP will connect on first request)...")
    yield
    await disconnect_mcp()

app = FastAPI(
    title="dbt MCP Semantic API",
    description="Headless semantic layer powered by dbt-MCP",
    version="1.0.0",
    lifespan=lifespan,
)

# -----------------------------
# Health
# -----------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mcp_connected": mcp_session is not None,
        "project_dir": PROJECT_DIR,
    }

# -----------------------------
# MetricFlow APIs
# -----------------------------

@app.get("/metrics")
async def list_metrics():
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "metricflow.list_metrics",
        {},
    )
    return {
        "metrics": result.content if result else [],
        "count": len(result.content) if result else 0,
    }


@app.get("/metrics/{metric_name}")
async def get_metric(metric_name: str):
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "metricflow.get_metric",
        {"metric_name": metric_name},
    )
    if not result or not result.content:
        raise HTTPException(status_code=404, detail="Metric not found")
    return result.content


@app.post("/metrics/sql")
async def generate_metric_sql(req: MetricSQLRequest):
    await ensure_mcp()

    payload = {
        "metric_names": req.metric_names,
        "dimensions": req.dimensions,
        "time_granularity": req.time_granularity,
        "where": req.where,
        "limit": req.limit,
    }

    payload = {k: v for k, v in payload.items() if v is not None}

    result = await mcp_session.call_tool(
        "metricflow.generate_sql",
        payload,
    )

    if not result or not result.content:
        raise HTTPException(status_code=400, detail="SQL generation failed")

    return {"sql": result.content}


@app.post("/metrics/validate-dimensions")
async def validate_dimensions(req: ValidateDimensionsRequest):
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "metricflow.validate_dimensions",
        {
            "metric_name": req.metric_name,
            "dimensions": req.dimensions,
        },
    )
    return result.content

# -----------------------------
# Semantic Models
# -----------------------------

@app.get("/semantic-models")
async def list_semantic_models():
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "metricflow.list_semantic_models",
        {},
    )
    return result.content if result else []

# -----------------------------
# dbt Metadata APIs
# -----------------------------

@app.get("/dbt/models")
async def list_models():
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "dbt.list_models",
        {},
    )
    return result.content if result else []


@app.get("/dbt/models/{model_name}")
async def get_model(model_name: str):
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "dbt.get_model",
        {"model_name": model_name},
    )
    if not result or not result.content:
        raise HTTPException(status_code=404, detail="Model not found")
    return result.content


@app.get("/dbt/sources")
async def list_sources():
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "dbt.list_sources",
        {},
    )
    return result.content if result else []


@app.get("/dbt/lineage/{model_name}")
async def get_lineage(model_name: str):
    await ensure_mcp()
    result = await mcp_session.call_tool(
        "dbt.get_lineage",
        {"model_name": model_name},
    )
    return result.content if result else []

# -----------------------------
# Entrypoint
# -----------------------------

if __name__ == "__main__":
    import uvicorn

    print("Starting dbt MCP Semantic API")
    print("→ http://localhost:8080")
    print("→ MCP will initialize on first request")

    uvicorn.run(app, host="0.0.0.0", port=8080)
