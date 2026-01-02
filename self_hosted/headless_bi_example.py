"""
Headless BI Use Case: Querying dbt Metrics via MCP Server

This example demonstrates how to use dbt MCP server to build headless BI applications
that query metrics programmatically without a traditional BI tool UI.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

# MCP client imports (you'll need to install: pip install mcp)
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("Install MCP client: pip install mcp")
    exit(1)


class DbtMetricQueryClient:
    """Client for querying dbt metrics via MCP server"""
    
    def __init__(self, project_dir: str, profiles_dir: str, dbt_path: str):
        self.project_dir = project_dir
        self.profiles_dir = profiles_dir
        self.dbt_path = dbt_path
        self.session: Optional[ClientSession] = None
        self.transport_context = None
    
    async def connect(self):
        """Connect to dbt MCP server"""
        server_params = StdioServerParameters(
            command="py",
            args=["-3.12", "-m", "dbt_mcp.main"],
            env={
                "DBT_PROJECT_DIR": self.project_dir,
                "DBT_PROFILES_DIR": self.profiles_dir,
                "DBT_PATH": self.dbt_path,
            }
        )
        
        # stdio_client returns an async context manager
        self.transport_context = stdio_client(server_params)
        read_stream, write_stream = await self.transport_context.__aenter__()
        self.session = ClientSession(read_stream, write_stream)
        await self.session.initialize()
        print("✓ Connected to dbt MCP server")
    
    async def list_metrics(self) -> List[Dict[str, Any]]:
        """List all available metrics"""
        result = await self.session.call_tool("list_metrics", {})
        return result.content if result else []
    
    async def query_metrics(
        self,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        time_grain: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query metrics with optional dimensions and filters
        
        Args:
            metrics: List of metric names (e.g., ["total_revenue", "total_orders"])
            dimensions: List of dimensions to group by (e.g., ["order__order_date__month"])
            filters: Dictionary of filters (e.g., {"order__order_status": "completed"})
            time_grain: Time grain for time dimensions (e.g., "month")
            limit: Maximum number of rows to return
        """
        query_params = {
            "metrics": metrics,
        }
        
        if dimensions:
            query_params["dimensions"] = dimensions
        
        if filters:
            query_params["where"] = self._build_where_clause(filters)
        
        if time_grain:
            query_params["time_grain"] = time_grain
        
        if limit:
            query_params["limit"] = limit
        
        result = await self.session.call_tool("query_metrics", query_params)
        return result.content if result else {}
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> str:
        """Build WHERE clause from filter dictionary"""
        conditions = []
        for key, value in filters.items():
            if isinstance(value, str):
                conditions.append(f"{{{{ Dimension('{key}') }}}} = '{value}'")
            elif isinstance(value, list):
                values = "', '".join(str(v) for v in value)
                conditions.append(f"{{{{ Dimension('{key}') }}}} IN ('{values}')")
            else:
                conditions.append(f"{{{{ Dimension('{key}') }}}} = {value}")
        return " AND ".join(conditions)
    
    async def get_metric_sql(
        self,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get compiled SQL for a metric query"""
        query_params = {
            "metrics": metrics,
        }
        
        if dimensions:
            query_params["dimensions"] = dimensions
        
        if filters:
            query_params["where"] = self._build_where_clause(filters)
        
        result = await self.session.call_tool("get_metrics_compiled_sql", query_params)
        return result.content[0].text if result and result.content else ""
    
    async def close(self):
        """Close the MCP session"""
        if self.session:
            await self.session.close()
            self.session = None
        if self.transport_context:
            await self.transport_context.__aexit__(None, None, None)
            self.transport_context = None


# ============================================================================
# USE CASE 1: Automated Daily Revenue Report
# ============================================================================

async def generate_daily_revenue_report(client: DbtMetricQueryClient):
    """Generate a daily revenue report for the last 7 days"""
    print("\n" + "="*60)
    print("USE CASE 1: Daily Revenue Report")
    print("="*60)
    
    # Get revenue metrics for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    result = await client.query_metrics(
        metrics=["total_revenue", "completed_revenue", "total_orders"],
        dimensions=["order__order_date__day"],
        filters={
            "order__order_date__day": f">= '{start_date.strftime('%Y-%m-%d')}'"
        },
        limit=100
    )
    
    print("\nDaily Revenue Report (Last 7 Days):")
    print("-" * 60)
    if result and "data" in result:
        for row in result["data"]:
            print(f"Date: {row.get('order__order_date__day', 'N/A')}")
            print(f"  Total Revenue: ${row.get('total_revenue', 0):,.2f}")
            print(f"  Completed Revenue: ${row.get('completed_revenue', 0):,.2f}")
            print(f"  Total Orders: {row.get('total_orders', 0)}")
            print()


# ============================================================================
# USE CASE 2: Store Performance Dashboard Data
# ============================================================================

async def get_store_performance_data(client: DbtMetricQueryClient):
    """Get store performance metrics for dashboard"""
    print("\n" + "="*60)
    print("USE CASE 2: Store Performance Dashboard")
    print("="*60)
    
    # Query revenue by store type
    result = await client.query_metrics(
        metrics=["total_revenue", "average_order_value", "total_orders"],
        dimensions=["store__store_type"],
        limit=50
    )
    
    print("\nStore Performance by Type:")
    print("-" * 60)
    if result and "data" in result:
        for row in result["data"]:
            store_type = row.get("store__store_type", "Unknown")
            revenue = row.get("total_revenue", 0)
            aov = row.get("average_order_value", 0)
            orders = row.get("total_orders", 0)
            
            print(f"\n{store_type}:")
            print(f"  Revenue: ${revenue:,.2f}")
            print(f"  Average Order Value: ${aov:,.2f}")
            print(f"  Total Orders: {orders}")


# ============================================================================
# USE CASE 3: Conversion Funnel Analysis
# ============================================================================

async def analyze_conversion_funnel(client: DbtMetricQueryClient):
    """Analyze conversion metrics for funnel analysis"""
    print("\n" + "="*60)
    print("USE CASE 3: Conversion Funnel Analysis")
    print("="*60)
    
    # Get conversion metrics
    result = await client.query_metrics(
        metrics=[
            "visit_to_order_conversion_rate_7d",
            "visit_to_order_conversion_rate_30d",
            "order_completion_rate",
            "credit_card_adoption_rate"
        ],
        dimensions=["visit__visit_date__month"],
        limit=12
    )
    
    print("\nConversion Metrics by Month:")
    print("-" * 60)
    if result and "data" in result:
        for row in result["data"]:
            month = row.get("visit__visit_date__month", "N/A")
            conv_7d = row.get("visit_to_order_conversion_rate_7d", 0)
            conv_30d = row.get("visit_to_order_conversion_rate_30d", 0)
            completion = row.get("order_completion_rate", 0)
            cc_adoption = row.get("credit_card_adoption_rate", 0)
            
            print(f"\n{month}:")
            print(f"  Visit→Order (7d): {conv_7d:.2f}%")
            print(f"  Visit→Order (30d): {conv_30d:.2f}%")
            print(f"  Order Completion: {completion:.2f}%")
            print(f"  Credit Card Adoption: {cc_adoption:.2f}%")


# ============================================================================
# USE CASE 4: Real-time Metric API Endpoint
# ============================================================================

async def get_metric_api_response(
    client: DbtMetricQueryClient,
    metric_name: str,
    dimension: Optional[str] = None,
    filter_value: Optional[str] = None
) -> Dict[str, Any]:
    """Get metric data formatted for API response"""
    metrics = [metric_name]
    dimensions = [dimension] if dimension else None
    filters = {dimension: filter_value} if filter_value else None
    
    result = await client.query_metrics(
        metrics=metrics,
        dimensions=dimensions,
        filters=filters,
        limit=100
    )
    
    return {
        "metric": metric_name,
        "dimension": dimension,
        "filter": filter_value,
        "timestamp": datetime.now().isoformat(),
        "data": result.get("data", []) if result else []
    }


# ============================================================================
# USE CASE 5: Automated Alerting System
# ============================================================================

async def check_revenue_threshold(client: DbtMetricQueryClient, threshold: float = 10000):
    """Check if revenue meets threshold and send alert if not"""
    print("\n" + "="*60)
    print("USE CASE 5: Automated Revenue Alert")
    print("="*60)
    
    # Get today's revenue
    today = datetime.now().strftime('%Y-%m-%d')
    result = await client.query_metrics(
        metrics=["total_revenue"],
        dimensions=["order__order_date__day"],
        filters={"order__order_date__day": f"= '{today}'"},
        limit=1
    )
    
    if result and "data" in result and len(result["data"]) > 0:
        revenue = result["data"][0].get("total_revenue", 0)
        
        print(f"\nToday's Revenue: ${revenue:,.2f}")
        print(f"Threshold: ${threshold:,.2f}")
        
        if revenue < threshold:
            print(f"⚠️  ALERT: Revenue below threshold!")
            # In production, send email/Slack notification here
            return {
                "alert": True,
                "message": f"Revenue ${revenue:,.2f} is below threshold ${threshold:,.2f}",
                "revenue": revenue,
                "threshold": threshold
            }
        else:
            print("✓ Revenue meets threshold")
            return {
                "alert": False,
                "message": "Revenue is healthy",
                "revenue": revenue,
                "threshold": threshold
            }
    else:
        print("No data available for today")
        return {"alert": False, "message": "No data", "revenue": 0}


# ============================================================================
# USE CASE 6: SQL Generation for Custom Analysis
# ============================================================================

async def generate_custom_analysis_sql(client: DbtMetricQueryClient):
    """Generate SQL for custom analysis"""
    print("\n" + "="*60)
    print("USE CASE 6: Generate SQL for Custom Analysis")
    print("="*60)
    
    sql = await client.get_metric_sql(
        metrics=["total_revenue", "average_order_value"],
        dimensions=["store__store_type", "customer__customer_region"],
        filters={"order__order_status": "completed"}
    )
    
    print("\nGenerated SQL:")
    print("-" * 60)
    print(sql)
    
    return sql


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main function demonstrating headless BI use cases"""
    
    # Initialize client
    client = DbtMetricQueryClient(
        project_dir=r"C:\Rif\dbt_poc\metricflow_poc",
        profiles_dir=r"C:\Rif\dbt_poc\metricflow_poc",
        dbt_path=r"C:\Users\Timer\.local\bin\dbt.exe"
    )
    
    try:
        # Connect to MCP server
        await client.connect()
        
        # List available metrics
        print("\n" + "="*60)
        print("Available Metrics:")
        print("="*60)
        metrics = await client.list_metrics()
        for metric in metrics[:10]:  # Show first 10
            print(f"  - {metric.get('name', 'Unknown')}")
        
        # Run use cases
        await generate_daily_revenue_report(client)
        await get_store_performance_data(client)
        await analyze_conversion_funnel(client)
        await check_revenue_threshold(client, threshold=5000)
        await generate_custom_analysis_sql(client)
        
        # Example API response
        print("\n" + "="*60)
        print("USE CASE 4: API Response Example")
        print("="*60)
        api_response = await get_metric_api_response(
            client,
            metric_name="total_revenue",
            dimension="store__store_type"
        )
        print(json.dumps(api_response, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())

