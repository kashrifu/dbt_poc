"""
Simple test script to verify MCP connection works
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_connection():
    """Test MCP connection"""
    server_params = StdioServerParameters(
        command="py",
        args=["-3.12", "-m", "dbt_mcp.main"],
        env={
            "DBT_PROJECT_DIR": r"C:\Rif\dbt_poc\metricflow_poc",
            "DBT_PROFILES_DIR": r"C:\Rif\dbt_poc\metricflow_poc",
            "DBT_PATH": r"C:\Users\Timer\.local\bin\dbt.exe",
        }
    )
    
    print("Starting MCP server...")
    transport_context = stdio_client(server_params)
    
    try:
        print("Entering transport context...")
        read_stream, write_stream = await asyncio.wait_for(
            transport_context.__aenter__(),
            timeout=60.0
        )
        print("✓ Transport context entered")
        
        print("Creating session...")
        session = ClientSession(read_stream, write_stream)
        
        print("Initializing session (this may take a while)...")
        await asyncio.wait_for(
            session.initialize(),
            timeout=120.0
        )
        print("✓ Session initialized")
        
        print("Testing list_metrics tool...")
        result = await session.call_tool("list_metrics", {})
        print(f"✓ Got result: {len(result.content) if result else 0} metrics")
        
        if result and result.content:
            print("\nFirst few metrics:")
            for metric in result.content[:5]:
                print(f"  - {metric.get('name', 'Unknown')}")
        
        await session.close()
        await transport_context.__aexit__(None, None, None)
        print("✓ Connection closed successfully")
        
    except asyncio.TimeoutError:
        print("✗ Connection timeout")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())

