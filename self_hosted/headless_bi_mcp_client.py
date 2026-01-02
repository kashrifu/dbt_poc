"""
Headless BI Client using dbt MCP Server

This shows how a headless BI application connects to dbt MCP server
and queries metrics that execute on Databricks.
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class HeadlessBIClient:
    """
    Client for headless BI applications to query metrics via dbt MCP server.
    
    Flow:
    1. Headless BI App (this client)
    2. → Connects to dbt MCP Server
    3. → MCP Server uses MetricFlow
    4. → MetricFlow generates SQL
    5. → SQL executes on Databricks
    6. → Results returned to Headless BI App
    """
    
    def __init__(
        self,
        project_dir: str = r"C:\Rif\dbt_poc\metricflow_poc",
        profiles_dir: str = r"C:\Rif\dbt_poc\metricflow_poc",
        dbt_path: str = r"C:\Users\Timer\.local\bin\dbt.exe"
    ):
        self.project_dir = project_dir
        self.profiles_dir = profiles_dir
        self.dbt_path = dbt_path
        self.session: Optional[ClientSession] = None
        self.transport_context = None
    
    async def connect(self):
        """Connect to dbt MCP server"""
        import sys
        import os
        import subprocess
        
        # Pre-parse dbt project to speed up MCP initialization
        semantic_manifest = os.path.join(self.project_dir, "target", "semantic_manifest.json")
        if not os.path.exists(semantic_manifest):
            print("Pre-parsing dbt project...")
            try:
                subprocess.run(
                    [self.dbt_path, "parse", "--quiet"],
                    cwd=self.project_dir,
                    env={**os.environ, "DBT_PROFILES_DIR": self.profiles_dir},
                    capture_output=True,
                    timeout=60
                )
                print("✓ Project parsed")
            except:
                pass
        
        server_params = StdioServerParameters(
            command=sys.executable,  # Use venv Python
            args=["-m", "dbt_mcp.main"],
            env={
                "DBT_PROJECT_DIR": self.project_dir,
                "DBT_PROFILES_DIR": self.profiles_dir,
                "DBT_PATH": self.dbt_path,
            }
        )
        
        print("Connecting to dbt MCP server...")
        print(f"  Using Python: {sys.executable}")
        print(f"  Project: {self.project_dir}")
        try:
            print("  Starting MCP server process...")
            self.transport_context = stdio_client(server_params)
            
            print("  Entering transport context...")
            read_stream, write_stream = await asyncio.wait_for(
                self.transport_context.__aenter__(),
                timeout=60.0
            )
            print("  ✓ Transport context established")
            
            print("  Creating client session...")
            self.session = ClientSession(read_stream, write_stream)
            
            print("  Initializing MCP session...")
            print("  ⏳ This may take 2-5 minutes on first run (MCP server is parsing dbt project)...")
            print("  ⏳ Please wait - the server is loading semantic models and metrics...")
            
            # Try to initialize with progress updates
            # MCP initialization can take 10-15+ minutes on first run
            print("  ⏳ Initialization timeout set to 15 minutes (first run is very slow)...")
            try:
                await asyncio.wait_for(
                    self.session.initialize(),
                    timeout=900.0  # 15 minutes - first run can be extremely slow
                )
                print("✓ Connected to dbt MCP server")
            except asyncio.TimeoutError:
                print("\n✗ TIMEOUT: MCP server took more than 15 minutes to initialize")
                print("  This indicates a serious issue. Possible causes:")
                print("    1. MCP server process crashed or hung")
                print("    2. Communication breakdown between client and server")
                print("    3. dbt project has parsing errors")
                print("\n  Check:")
                print("    - Run 'dbt parse' manually to see if there are errors")
                print("    - Check if MCP server process is still running")
                print("    - Try running MCP server manually: python -m dbt_mcp.main")
                raise
        except asyncio.TimeoutError:
            print("✗ Timeout - MCP server took too long to initialize")
            print("  Try running 'dbt parse' first, then try again")
            raise
        except Exception as e:
            print(f"✗ Connection error: {e}")
            raise
    
    async def list_metrics(self) -> List[Dict[str, Any]]:
        """List all available metrics"""
        result = await self.session.call_tool("list_metrics", {})
        return result.content if result else []
    
    async def query_metrics(
        self,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        where: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query metrics - SQL executes on Databricks
        
        Args:
            metrics: List of metric names (e.g., ["total_revenue", "total_orders"])
            dimensions: Optional dimensions to group by (e.g., ["store__store_type"])
            where: Optional WHERE clause filter
            limit: Optional row limit
        
        Returns:
            Query results from Databricks
        """
        query_params = {
            "metrics": metrics
        }
        
        if dimensions:
            query_params["dimensions"] = dimensions
        
        if where:
            query_params["where"] = where
        
        if limit:
            query_params["limit"] = limit
        
        # This calls MCP server -> MetricFlow -> Generates SQL -> Executes on Databricks
        result = await self.session.call_tool("query_metrics", query_params)
        return result.content if result else {}
    
    async def get_sql(
        self,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        where: Optional[str] = None
    ) -> str:
        """Get the compiled SQL that will execute on Databricks"""
        query_params = {"metrics": metrics}
        
        if dimensions:
            query_params["dimensions"] = dimensions
        
        if where:
            query_params["where"] = where
        
        result = await self.session.call_tool("get_metrics_compiled_sql", query_params)
        return result.content[0].text if result and result.content else ""
    
    async def close(self):
        """Close MCP connection"""
        try:
            if self.transport_context:
                await self.transport_context.__aexit__(None, None, None)
                self.transport_context = None
        except Exception as e:
            print(f"Warning during close: {e}")
        self.session = None


# ============================================================================
# EXAMPLE: Headless BI Application
# ============================================================================

async def example_headless_bi_app():
    """
    Example: How a headless BI application uses MCP server
    
    This simulates a headless BI application that:
    1. Connects to MCP server
    2. Queries metrics
    3. Gets results from Databricks
    4. Processes data programmatically
    """
    
    client = HeadlessBIClient()
    
    try:
        # Step 1: Connect to MCP server
        await client.connect()
        
        # Step 2: Discover available metrics
        print("\n" + "="*60)
        print("STEP 1: Discover Metrics")
        print("="*60)
        metrics = await client.list_metrics()
        print(f"Found {len(metrics)} metrics:")
        for metric in metrics[:5]:  # Show first 5
            print(f"  - {metric.get('name')}: {metric.get('label')}")
        
        # Step 3: Query revenue by store type (executes on Databricks)
        print("\n" + "="*60)
        print("STEP 2: Query Metrics (Executes on Databricks)")
        print("="*60)
        result = await client.query_metrics(
            metrics=["total_revenue", "total_orders"],
            dimensions=["store__store_type"],
            limit=10
        )
        
        print("\nQuery Results from Databricks:")
        if result and "data" in result:
            for row in result["data"]:
                store_type = row.get("store__store_type", "N/A")
                revenue = row.get("total_revenue", 0)
                orders = row.get("total_orders", 0)
                print(f"  {store_type}: ${revenue:,.2f} revenue, {orders} orders")
        
        # Step 4: Get the SQL that was executed
        print("\n" + "="*60)
        print("STEP 3: View Generated SQL")
        print("="*60)
        sql = await client.get_sql(
            metrics=["total_revenue"],
            dimensions=["store__store_type"]
        )
        print("SQL executed on Databricks:")
        print(sql[:500] + "..." if len(sql) > 500 else sql)
        
        # Step 5: Query with filters (executes on Databricks)
        print("\n" + "="*60)
        print("STEP 4: Query with Filters")
        print("="*60)
        result = await client.query_metrics(
            metrics=["completed_revenue"],
            dimensions=["order__order_date__month"],
            where="{{ TimeDimension('order__order_date__month') }} >= '2024-01'",
            limit=12
        )
        
        print("\nCompleted Revenue by Month (from Databricks):")
        if result and "data" in result:
            for row in result["data"]:
                month = row.get("order__order_date__month", "N/A")
                revenue = row.get("completed_revenue", 0)
                print(f"  {month}: ${revenue:,.2f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


# ============================================================================
# EXAMPLE: Automated Report Generator
# ============================================================================

async def generate_daily_report():
    """Example: Automated daily report using MCP"""
    
    client = HeadlessBIClient()
    
    try:
        await client.connect()
        
        # Query today's metrics
        result = await client.query_metrics(
            metrics=["total_revenue", "total_orders", "average_order_value"],
            dimensions=["order__order_date__day"],
            where="{{ TimeDimension('order__order_date__day') }} = CURRENT_DATE",
            limit=1
        )
        
        # Process results
        if result and "data" in result and len(result["data"]) > 0:
            data = result["data"][0]
            print("Daily Report:")
            print(f"  Revenue: ${data.get('total_revenue', 0):,.2f}")
            print(f"  Orders: {data.get('total_orders', 0)}")
            print(f"  AOV: ${data.get('average_order_value', 0):,.2f}")
            
            # In production: Send email, save to file, etc.
            return data
        else:
            print("No data for today")
            return None
            
    finally:
        await client.close()


# ============================================================================
# EXAMPLE: Real-time Dashboard Data
# ============================================================================

async def get_dashboard_data():
    """Example: Get data for a real-time dashboard"""
    
    client = HeadlessBIClient()
    
    try:
        await client.connect()
        
        # Get multiple metrics for dashboard
        dashboard_data = {}
        
        # Revenue by store type
        revenue_by_store = await client.query_metrics(
            metrics=["total_revenue"],
            dimensions=["store__store_type"]
        )
        dashboard_data["revenue_by_store"] = revenue_by_store
        
        # Conversion rates
        conversions = await client.query_metrics(
            metrics=["order_completion_rate", "credit_card_adoption_rate"]
        )
        dashboard_data["conversions"] = conversions
        
        return dashboard_data
        
    finally:
        await client.close()


if __name__ == "__main__":
    print("="*60)
    print("Headless BI Client - Using dbt MCP Server")
    print("="*60)
    print("\nThis demonstrates how headless BI applications")
    print("use MCP server to query metrics on Databricks.\n")
    
    # Run example
    asyncio.run(example_headless_bi_app())

