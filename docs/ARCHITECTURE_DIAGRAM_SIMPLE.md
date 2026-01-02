# Semantic Layer Architecture Comparison: dbt Cloud vs Databricks vs Cube.dev

## Three Semantic Layer Options Overview

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    OPTION 1: dbt Cloud Semantic Layer                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  [Clients] ──HTTPS──> [dbt Cloud API] ──> [dbt Cloud Semantic Layer]       ║
║     │                      │                        │                       ║
║     │                      │                        ├─> MetricFlow Engine    ║
║     │                      │                        ├─> dbt Execution        ║
║     │                      │                        ├─> Job Scheduler        ║
║     │                      │                        └─> Metadata Store       ║
║     │                      │                                                ║
║     │                      └──SQL──> [Your Data Warehouse]                  ║
║     │                                                                       ║
║     └───────────────────────Response───────────────────────────────────────┘ ║
║                                                                              ║
║  🔒 Managed by dbt Labs  |  💰 REQUIRES SUBSCRIPTION  |  🔄 Auto-updates    ║
║  ⚠️  LIMITATION: Must pay for dbt Cloud subscription to access semantic layer ║
╚══════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════╗
║              OPTION 2: Databricks Unity Catalog Semantic Layer                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  [Clients] ──SQL──> [Databricks SQL] ──> [Unity Catalog Metric Views]      ║
║     │                  │                        │                           ║
║     │                  │                        ├─> Metric Definitions      ║
║     │                  │                        ├─> Business Views           ║
║     │                  │                        └─> Unity Catalog RBAC        ║
║     │                  │                                                ║
║     │                  └──Direct Query──> [Databricks Warehouse]         ║
║     │                                                                       ║
║     └───────────────────────Response───────────────────────────────────────┘ ║
║                                                                              ║
║  🔒 Native to Databricks  |  💰 Databricks Platform Cost  |  🔄 Platform Updates ║
║  ⚠️  LIMITATION: Databricks-only, cannot use with other warehouses          ║
╚══════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════╗
║                    OPTION 3: Cube.dev Semantic Layer                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  [Clients] ──REST/GraphQL──> [Cube API] ──> [Cube Semantic Layer]          ║
║     │                  │                        │                           ║
║     │                  │                        ├─> Schema Definitions       ║
║     │                  │                        ├─> Pre-aggregations         ║
║     │                  │                        └─> Query Orchestration        ║
║     │                  │                                                ║
║     │                  └──SQL──> [Your Data Warehouse]                  ║
║     │                                                                       ║
║     └───────────────────────Response───────────────────────────────────────┘ ║
║                                                                              ║
║  🔒 Self-hosted or Cloud  |  💰 Open Source or Paid  |  🔄 You Manage        ║
║  ⚠️  LIMITATION: Requires separate infrastructure, different YAML format     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## OPTION 1: dbt Cloud Semantic Layer - Detailed Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    dbt Cloud Semantic Layer                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐                                                             │
│  │   Clients   │                                                             │
│  │  (BI Tools, │                                                             │
│  │   Web Apps, │                                                             │
│  │   Python)   │                                                             │
│  └──────┬──────┘                                                             │
│         │ HTTPS + dbt Cloud API Token                                        │
│         │ (REQUIRES: Active dbt Cloud Subscription)                          │
│         ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │              dbt Cloud Platform (Managed by dbt Labs)         │          │
│  │  ┌────────────────────────────────────────────────────────┐  │          │
│  │  │  API Gateway & Authentication                          │  │          │
│  │  │  • OAuth / API Key Auth                                │  │          │
│  │  │  • Rate Limiting                                       │  │          │
│  │  │  • Subscription Validation ⚠️                          │  │          │
│  │  └───────────────┬──────────────────────────────────────┘  │          │
│  │                  │                                          │          │
│  │  ┌───────────────┴──────────────────────────────────────┐  │          │
│  │  │  Semantic Layer Service (MetricFlow)                 │  │          │
│  │  │  • MetricFlow Engine (Managed)                      │  │          │
│  │  │  • SQL Generation                                    │  │          │
│  │  │  • Query Compilation                                 │  │          │
│  │  │  • Multi-hop Join Resolution                         │  │          │
│  │  └───────────────┬──────────────────────────────────────┘  │          │
│  │                  │                                          │          │
│  │  ┌───────────────┴──────────────────────────────────────┐  │          │
│  │  │  dbt Execution Environment                            │  │          │
│  │  │  • dbt Core (Managed)                                │  │          │
│  │  │  • Project Storage (Git Integration)                  │  │          │
│  │  │  • Job Scheduler                                     │  │          │
│  │  │  • Run History & Logs                               │  │          │
│  │  └───────────────┬──────────────────────────────────────┘  │          │
│  │                  │                                          │          │
│  │  ┌───────────────┴──────────────────────────────────────┐  │          │
│  │  │  Metadata Store (dbt Cloud Database)                  │  │          │
│  │  │  • Compiled Manifests                                 │  │          │
│  │  │  • Semantic Manifest (MetricFlow)                    │  │          │
│  │  │  • Lineage Graphs                                     │  │          │
│  │  │  • Metric Definitions                                 │  │          │
│  │  └──────────────────────────────────────────────────────┘  │          │
│  └───────────────────────┬──────────────────────────────────────┘          │
│                          │ SQL (Generated by MetricFlow)                   │
│                          ▼                                                │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │              Your Data Warehouse                             │          │
│  │  (Databricks, Snowflake, BigQuery, Redshift, etc.)           │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                              │
│  ✅ FEATURES:                                                                │
│     • Multi-warehouse support                                                │
│     • Automatic metric SQL generation                                        │
│     • Built-in web UI for metric exploration                                 │
│     • GraphQL & REST API access                                              │
│     • Automatic updates & maintenance                                         │
│     • Enterprise support                                                     │
│                                                                              │
│  ⚠️  LIMITATIONS:                                                            │
│     • REQUIRES dbt Cloud subscription (Developer/Team/Enterprise plan)      │
│     • Cannot use semantic layer without paying for dbt Cloud                 │
│     • Vendor lock-in to dbt Labs platform                                    │
│     • Limited customization of API behavior                                  │
│     • All data flows through dbt Cloud infrastructure                       │
│                                                                              │
│  💰 COST:                                                                    │
│     • Developer Plan: ~$X/month per developer                                │
│     • Team Plan: ~$Y/month per team                                          │
│     • Enterprise: Custom pricing                                             │
│     • Semantic layer access included in subscription                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### How dbt Cloud Semantic Layer Works:

1. **Setup**: Connect your dbt project (in Git) to dbt Cloud
2. **Definition**: Define semantic models and metrics in YAML files (same as self-hosted)
3. **Compilation**: dbt Cloud automatically compiles semantic layer on dbt runs
4. **Access**: Use dbt Cloud API (REST/GraphQL) to query metrics
5. **Execution**: dbt Cloud generates SQL and executes on your warehouse

### Key Limitation:
**You MUST have an active dbt Cloud subscription to access the semantic layer API.** There is no way to use dbt Cloud's semantic layer without paying for dbt Cloud.

---

## OPTION 2: Databricks Unity Catalog Semantic Layer - Detailed Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│              Databricks Unity Catalog Semantic Layer                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐                                                             │
│  │   Clients   │                                                             │
│  │  (BI Tools, │                                                             │
│  │   Databricks│                                                             │
│  │   SQL, Apps)│                                                             │
│  └──────┬──────┘                                                             │
│         │ Databricks SQL / JDBC / ODBC                                       │
│         │ (REQUIRES: Databricks Workspace with Unity Catalog)                │
│         ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │              Databricks Platform                               │          │
│  │  ┌────────────────────────────────────────────────────────┐  │          │
│  │  │  Databricks SQL Warehouse                               │  │          │
│  │  │  • Query Engine                                        │  │          │
│  │  │  • Unity Catalog Integration                           │  │          │
│  │  └───────────────┬──────────────────────────────────────┘  │          │
│  │                  │                                          │          │
│  │  ┌───────────────┴──────────────────────────────────────┐  │          │
│  │  │  Unity Catalog Semantic Layer                        │  │          │
│  │  │  • Metric Views (YAML definitions)                   │  │          │
│  │  │  • Business Views                                    │  │          │
│  │  │  • MEASURE() function support                        │  │          │
│  │  │  • Dimension & Measure definitions                   │  │          │
│  │  └───────────────┬──────────────────────────────────────┘  │          │
│  │                  │                                          │          │
│  │  ┌───────────────┴──────────────────────────────────────┐  │          │
│  │  │  Unity Catalog Governance                            │  │          │
│  │  │  • RBAC (Role-Based Access Control)                 │  │          │
│  │  │  • Data Lineage                                     │  │          │
│  │  │  • Data Quality                                     │  │          │
│  │  └──────────────────────────────────────────────────────┘  │          │
│  └───────────────────────┬──────────────────────────────────────┘          │
│                          │ Direct SQL Execution                            │
│                          ▼                                                │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │              Databricks Data Warehouse                       │          │
│  │  (Delta Lake Tables, Unity Catalog Managed)                  │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                              │
│  ✅ FEATURES:                                                                │
│     • Native to Databricks platform                                         │
│     • Zero external dependencies                                            │
│     • Direct SQL access with MEASURE() function                             │
│     • Unity Catalog governance & RBAC                                       │
│     • Integrated with Databricks SQL Assistant                              │
│     • No additional subscription needed (part of Databricks)                │
│                                                                              │
│  ⚠️  LIMITATIONS:                                                            │
│     • DATABRICKS-ONLY - Cannot use with other warehouses                    │
│     • Vendor lock-in to Databricks platform                                 │
│     • Manual join definitions (no automatic multi-hop)                       │
│     • Different YAML format than dbt MetricFlow                             │
│     • Limited metric types compared to dbt MetricFlow                       │
│     • Must use Databricks SQL syntax                                        │
│                                                                              │
│  💰 COST:                                                                    │
│     • Databricks platform costs (DBU usage)                                │
│     • Unity Catalog included (no extra fee)                                 │
│     • Requires Databricks workspace                                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### How Databricks Semantic Layer Works:

1. **Setup**: Enable Unity Catalog in your Databricks workspace
2. **Definition**: Create Metric Views using YAML (embedded in SQL or via UI)
3. **Storage**: Metric definitions stored in Unity Catalog
4. **Query**: Use native Databricks SQL with `MEASURE()` function
5. **Execution**: Direct execution on Databricks SQL Warehouse

### Key Limitation:
**Only works with Databricks.** Cannot use this semantic layer if you use Snowflake, BigQuery, Redshift, or any other warehouse.

---

## OPTION 3: Cube.dev Semantic Layer - Detailed Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Cube.dev Semantic Layer                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐                                                             │
│  │   Clients   │                                                             │
│  │  (BI Tools, │                                                             │
│  │   Web Apps, │                                                             │
│  │   Python)   │                                                             │
│  └──────┬──────┘                                                             │
│         │ REST API / GraphQL                                                  │
│         │ (Self-hosted or Cube Cloud)                                        │
│         ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │              Cube API Server (Your Infrastructure)             │          │
│  │  ┌────────────────────────────────────────────────────────┐  │          │
│  │  │  Cube API Gateway                                      │  │          │
│  │  │  • REST & GraphQL endpoints                            │  │          │
│  │  │  • Authentication (configurable)                      │  │          │
│  │  │  • Rate Limiting                                       │  │          │
│  │  └───────────────┬──────────────────────────────────────┘  │          │
│  │                  │                                          │          │
│  │  ┌───────────────┴──────────────────────────────────────┐  │          │
│  │  │  Cube Semantic Layer Engine                          │  │          │
│  │  │  • Schema Compiler (YAML/JS definitions)            │  │          │
│  │  │  • Query Orchestrator                                │  │          │
│  │  │  • Pre-aggregation Engine                            │  │          │
│  │  │  • SQL Generation                                    │  │          │
│  │  └───────────────┬──────────────────────────────────────┘  │          │
│  │                  │                                          │          │
│  │  ┌───────────────┴──────────────────────────────────────┐  │          │
│  │  │  Cube Cache Layer (Optional)                         │  │          │
│  │  │  • Redis / Memcached                                 │  │          │
│  │  │  • Pre-aggregated tables                             │  │          │
│  │  └──────────────────────────────────────────────────────┘  │          │
│  └───────────────────────┬──────────────────────────────────────┘          │
│                          │ SQL (Generated by Cube)                        │
│                          ▼                                                │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │              Your Data Warehouse                             │          │
│  │  (Snowflake, BigQuery, Databricks, Postgres, etc.)         │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                              │
│  ✅ FEATURES:                                                                │
│     • Multi-warehouse support                                                │
│     • Open source (self-hosted option)                                      │
│     • Pre-aggregations for performance                                      │
│     • REST & GraphQL APIs                                                   │
│     • Real-time data support                                                │
│     • Built-in caching                                                      │
│                                                                              │
│  ⚠️  LIMITATIONS:                                                            │
│     • Different YAML/JS schema format (not dbt compatible)                 │
│     • Requires separate infrastructure to run                                │
│     • Learning curve for Cube schema definitions                            │
│     • No direct dbt integration (separate tool)                             │
│     • Pre-aggregations require maintenance                                  │
│                                                                              │
│  💰 COST:                                                                    │
│     • Open Source: Free (self-hosted)                                       │
│     • Cube Cloud: Paid plans available                                     │
│     • Infrastructure costs for self-hosted                                  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### How Cube.dev Works:

1. **Setup**: Deploy Cube API server (Docker, Kubernetes, or Cube Cloud)
2. **Definition**: Define schema in YAML or JavaScript (different format than dbt)
3. **Compilation**: Cube compiles schema and generates SQL
4. **Query**: Use REST or GraphQL API to query metrics
5. **Execution**: Cube generates SQL and executes on your warehouse
6. **Caching**: Optional pre-aggregations for performance

### Key Limitation:
**Different schema format** - Cannot directly use dbt MetricFlow YAML files. Must rewrite metric definitions in Cube schema format.

---

## Comprehensive Comparison Table

| Feature | dbt Cloud | Databricks Unity Catalog | Cube.dev |
|---------|-----------|-------------------------|----------|
| **Warehouse Support** | ✅ Multi-warehouse (Snowflake, BigQuery, Databricks, Redshift, etc.) | ❌ **Databricks ONLY** | ✅ Multi-warehouse |
| **Subscription Required** | ⚠️ **YES - Must pay for dbt Cloud** | ❌ No (part of Databricks) | ❌ No (open source available) |
| **Schema Format** | dbt MetricFlow YAML | Unity Catalog YAML (different format) | Cube YAML/JS (different format) |
| **API Access** | ✅ REST & GraphQL | ⚠️ Databricks SQL only | ✅ REST & GraphQL |
| **Multi-hop Joins** | ✅ Automatic | ⚠️ Manual SQL joins | ✅ Automatic |
| **Pre-aggregations** | ❌ No | ❌ No | ✅ Yes (built-in) |
| **Caching** | ❌ No | ❌ No | ✅ Yes (Redis/Memcached) |
| **Version Control** | ✅ Git (YAML files) | ⚠️ Unity Catalog | ✅ Git (YAML/JS files) |
| **Governance** | dbt Cloud RBAC | ✅ Unity Catalog RBAC | Custom implementation |
| **BI Tool Integration** | ✅ Broad (JDBC, GraphQL, REST) | ⚠️ Databricks-native tools | ✅ Broad (REST, GraphQL) |
| **Learning Curve** | Low (if using dbt) | Medium | Medium-High |
| **Infrastructure** | Managed by dbt Labs | Managed by Databricks | You manage (or Cube Cloud) |
| **Cost** | 💰 Subscription fee | 💰 Databricks platform costs | 💰 Free (OSS) or paid (Cloud) |
| **Customization** | ⚠️ Limited | ⚠️ Limited | ✅ High |
| **dbt Integration** | ✅ Native | ❌ No | ❌ No |

---

## Decision Matrix: Which Semantic Layer Should You Choose?

### Choose dbt Cloud If:
```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Choose dbt Cloud if:                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  ✓ You already use dbt and want integrated semantic layer                │
│  ✓ You need multi-warehouse support                                      │
│  ✓ You have budget for dbt Cloud subscription                            │
│  ✓ You want zero DevOps for semantic layer                              │
│  ✓ You need built-in collaboration tools                                 │
│  ✓ You want automatic updates & maintenance                              │
│  ✓ You need enterprise support                                          │
│  ✓ You want web UI out of the box                                       │
│                                                                          │
│  ⚠️  LIMITATION: Must pay for dbt Cloud subscription                    │
│  ⚠️  LIMITATION: Cannot use without subscription                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Choose Databricks Unity Catalog If:
```
┌─────────────────────────────────────────────────────────────────────────┐
│              Choose Databricks Unity Catalog if:                        │
├─────────────────────────────────────────────────────────────────────────┤
│  ✓ You use Databricks as your ONLY warehouse                           │
│  ✓ You want native integration with Databricks platform                │
│  ✓ You need Unity Catalog governance features                           │
│  ✓ You want zero external dependencies                                 │
│  ✓ You prefer direct SQL access                                        │
│  ✓ You're already paying for Databricks platform                       │
│                                                                          │
│  ⚠️  LIMITATION: Databricks-only (vendor lock-in)                      │
│  ⚠️  LIMITATION: Cannot use with Snowflake, BigQuery, etc.              │
│  ⚠️  LIMITATION: Different YAML format than dbt MetricFlow              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Choose Cube.dev If:
```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Choose Cube.dev if:                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  ✓ You need multi-warehouse support                                      │
│  ✓ You want open source option (self-hosted)                            │
│  ✓ You need pre-aggregations for performance                            │
│  ✓ You want REST/GraphQL APIs                                          │
│  ✓ You're building a custom BI platform                                 │
│  ✓ You want full control over infrastructure                            │
│  ✓ You don't use dbt (or want separate semantic layer)                 │
│                                                                          │
│  ⚠️  LIMITATION: Different schema format (not dbt compatible)           │
│  ⚠️  LIMITATION: Requires separate infrastructure                        │
│  ⚠️  LIMITATION: Learning curve for Cube schema                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: Key Limitations Summary

### dbt Cloud Limitations:
- ⚠️ **REQUIRES SUBSCRIPTION** - Cannot access semantic layer without paying for dbt Cloud
- ⚠️ Vendor lock-in to dbt Labs platform
- ⚠️ Limited customization of API behavior
- ⚠️ All queries flow through dbt Cloud infrastructure

### Databricks Unity Catalog Limitations:
- ⚠️ **DATABRICKS-ONLY** - Cannot use with other warehouses
- ⚠️ Vendor lock-in to Databricks platform
- ⚠️ Manual join definitions (no automatic multi-hop)
- ⚠️ Different YAML format than dbt MetricFlow
- ⚠️ Limited metric types compared to dbt MetricFlow

### Cube.dev Limitations:
- ⚠️ **Different schema format** - Not compatible with dbt MetricFlow YAML
- ⚠️ Requires separate infrastructure to run
- ⚠️ Learning curve for Cube schema definitions
- ⚠️ No direct dbt integration (separate tool)
- ⚠️ Pre-aggregations require maintenance

---

## What's Compatible?

### dbt Cloud ↔ Self-Hosted dbt MetricFlow:
- ✅ **100% Compatible** - Same YAML format
- ✅ Can migrate definitions between both
- ✅ Same semantic models and metrics syntax

### dbt MetricFlow ↔ Databricks Unity Catalog:
- ❌ **NOT Compatible** - Different YAML formats
- ❌ Must rewrite metric definitions
- ❌ Different query interfaces

### dbt MetricFlow ↔ Cube.dev:
- ❌ **NOT Compatible** - Different schema formats
- ❌ Must rewrite metric definitions
- ❌ Different query interfaces

---

## Summary

| Option | Best For | Key Limitation |
|--------|----------|----------------|
| **dbt Cloud** | Teams using dbt with budget for subscription | ⚠️ Requires paid subscription |
| **Databricks Unity Catalog** | Databricks-only environments | ⚠️ Databricks-only, vendor lock-in |
| **Cube.dev** | Multi-warehouse with open source preference | ⚠️ Different schema format, separate infrastructure |

**Recommendation**: If you're already using dbt and want to avoid subscription costs, consider **self-hosting dbt MetricFlow** (as shown in your `headless_bi_fastapi_mcp.py` setup) - it gives you the same functionality as dbt Cloud without the subscription requirement!

---

## End-to-End Flow Comparison

### dbt Cloud Flow:
```
1. Developer
   └─> Defines metrics in YAML (Git repo)
       └─> Pushes to GitHub/GitLab
           └─> dbt Cloud detects changes
               └─> Runs dbt parse (compiles semantic layer)
                   └─> Stores semantic_manifest.json in dbt Cloud

2. Client Application
   └─> Calls dbt Cloud API with API token
       └─> dbt Cloud validates subscription ⚠️
           └─> Loads semantic_manifest.json
               └─> MetricFlow generates SQL
                   └─> Executes SQL on your warehouse
                       └─> Returns results to client

⚠️  BLOCKER: Step 2 fails if no active subscription
```

### Databricks Unity Catalog Flow:
```
1. Developer
   └─> Creates Metric View in Databricks (YAML in SQL or UI)
       └─> Stores in Unity Catalog
           └─> Unity Catalog validates and stores definition

2. Client Application
   └─> Connects to Databricks SQL Warehouse
       └─> Executes SQL with MEASURE() function
           └─> Databricks processes query
               └─> Returns results to client

⚠️  BLOCKER: Only works if warehouse is Databricks
```

### Cube.dev Flow:
```
1. Developer
   └─> Defines schema in Cube YAML/JS format
       └─> Deploys Cube API server (Docker/K8s/Cloud)
           └─> Cube compiles schema
               └─> Ready to serve queries

2. Client Application
   └─> Calls Cube REST/GraphQL API
       └─> Cube validates query
           └─> Checks cache (if enabled)
               └─> Generates SQL
                   └─> Executes SQL on your warehouse
                       └─> Returns results to client

⚠️  BLOCKER: Must rewrite metrics in Cube schema format
```

---

## Visual Architecture Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPTION 1: dbt Cloud                                      │
│                                                                              │
│  Client ──API Token──> dbt Cloud ──SQL──> Warehouse                       │
│              │              │                                               │
│              │              └─> ⚠️  Requires Subscription                  │
│              │                                                               │
│              └─> ❌ Fails if no subscription                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPTION 2: Databricks                                     │
│                                                                              │
│  Client ──SQL──> Databricks ──Direct──> Databricks Warehouse               │
│              │         │                                                      │
│              │         └─> ⚠️  Databricks Only                              │
│              │                                                               │
│              └─> ❌ Fails if warehouse is not Databricks                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPTION 3: Cube.dev                                       │
│                                                                              │
│  Client ──REST/GraphQL──> Cube API ──SQL──> Warehouse                     │
│              │                  │                                            │
│              │                  └─> ⚠️  Different Schema Format             │
│              │                                                               │
│              └─> ❌ Must rewrite metrics in Cube format                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPTION 4: Self-Hosted dbt MetricFlow (Your Setup)        │
│                                                                              │
│  Client ──HTTP──> FastAPI ──MCP──> dbt MetricFlow ──SQL──> Warehouse     │
│              │         │              │                                       │
│              │         │              └─> ✅ No Subscription Needed          │
│              │         │                                                      │
│              │         └─> ✅ Full Control                                   │
│              │                                                               │
│              └─> ✅ Works with any warehouse                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

