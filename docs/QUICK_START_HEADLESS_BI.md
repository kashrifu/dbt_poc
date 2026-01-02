# Quick Start: Headless BI API Server

## ⚠️ MCP Connection Issue

The MCP server connection is timing out. This is a known issue with dbt-mcp initialization.

## ✅ Solution: Use Simple Version (Recommended)

The simple version works immediately without MCP:

```powershell
python headless_bi_api_simple.py
```

This version:
- ✅ Starts instantly
- ✅ Works with dbt CLI directly
- ✅ No connection timeouts
- ✅ All basic features work

## Alternative: Wait Longer for MCP

If you want to use the MCP version:

1. **Start the server:**
   ```powershell
   python headless_bi_api_server.py
   ```

2. **Wait 5+ minutes** on first request to `/api/metrics`
   - The MCP server needs to parse your entire dbt project
   - It loads all semantic models and metrics
   - First run is always slow

3. **Subsequent requests will be faster** once initialized

## Recommended Approach

**For now, use the simple version:**
```powershell
python headless_bi_api_simple.py
```

Then access:
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health
- Metrics: http://localhost:8000/api/metrics

This works immediately without waiting for MCP initialization.

