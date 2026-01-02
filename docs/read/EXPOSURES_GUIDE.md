# dbt Exposures Guide for MetricFlow POC

## What are Exposures?

Exposures in dbt are used to **document downstream uses** of your dbt models, metrics, and semantic models. They help you:

1. **Track Lineage**: See where your metrics are being used
2. **Impact Analysis**: Understand what breaks when you change a metric
3. **Documentation**: Catalog all uses of your data assets
4. **Governance**: Know who owns and uses each metric

## Use Cases for Exposures with MetricFlow

### 1. **Dashboard Documentation**
Document which metrics are used in BI dashboards (Tableau, Looker, Power BI, etc.)

**Example:**
```yaml
- name: revenue_dashboard
  type: dashboard
  depends_on:
    - metric: total_revenue
    - metric: total_orders
```

**Benefits:**
- Know which dashboards will be affected if you change a metric
- Track metric usage across the organization
- Document dashboard ownership

### 2. **Report Documentation**
Document scheduled reports and automated emails that use metrics

**Example:**
```yaml
- name: daily_revenue_report
  type: notebook
  depends_on:
    - metric: total_revenue
```

**Benefits:**
- Track automated reporting dependencies
- Understand report freshness requirements
- Document report owners

### 3. **API/Application Usage**
Document how applications consume metrics via APIs

**Example:**
```yaml
- name: revenue_api_endpoint
  type: application
  depends_on:
    - metric: total_revenue
```

**Benefits:**
- Track API dependencies on metrics
- Understand application data requirements
- Plan for metric changes

### 4. **Analysis Documentation**
Document ad-hoc analyses and notebooks

**Example:**
```yaml
- name: q4_revenue_analysis
  type: analysis
  depends_on:
    - metric: total_revenue
    - semantic_model: orders
```

**Benefits:**
- Catalog important analyses
- Track analysis dependencies
- Share analysis context

### 5. **ML Model Dependencies**
Document machine learning models that use metrics

**Example:**
```yaml
- name: revenue_forecast_model
  type: ml
  depends_on:
    - metric: total_revenue
```

**Benefits:**
- Track ML model dependencies
- Understand data requirements for models
- Plan for metric changes

## Exposure Types

| Type | Use Case | Example |
|------|----------|---------|
| `dashboard` | BI dashboards | Tableau, Looker, Power BI |
| `notebook` | Reports, Jupyter notebooks | Scheduled reports, analysis notebooks |
| `application` | APIs, applications | REST APIs, internal apps |
| `analysis` | Ad-hoc analyses | One-off analyses, investigations |
| `ml` | Machine learning models | Forecasting, prediction models |

## Viewing Exposures

### In dbt Docs
```bash
dbt docs generate
dbt docs serve
```

Navigate to the "Exposures" section to see all documented downstream uses.

### In dbt Cloud
Exposures appear in the lineage graph, showing connections from metrics to downstream consumers.

## Best Practices

1. **Document All Major Uses**: Add exposures for all significant uses of your metrics
2. **Keep Updated**: Update exposures when dashboards/reports change
3. **Include Owners**: Always specify owners for accountability
4. **Add URLs**: Include links to dashboards/reports for easy access
5. **Set Maturity**: Use maturity levels (low, medium, high, production) to indicate stability

## Impact Analysis

When you change a metric, you can:

1. **Check Dependencies**: See all exposures that depend on the metric
2. **Notify Owners**: Contact exposure owners about the change
3. **Plan Migration**: Coordinate changes with downstream consumers
4. **Test Impact**: Verify downstream systems still work

## Example Workflow

1. **Create Metric**: Define a new metric in `metrics/revenue.yml`
2. **Use in Dashboard**: Add metric to a Tableau dashboard
3. **Document Exposure**: Add exposure in `exposures.yml` linking dashboard to metric
4. **Generate Docs**: Run `dbt docs generate` to see the connection
5. **Track Changes**: When metric changes, check exposures to see impact

## Integration with MetricFlow

Exposures work seamlessly with MetricFlow metrics:

- **Metric Dependencies**: Reference metrics directly in `depends_on`
- **Semantic Model Dependencies**: Reference semantic models
- **Lineage Tracking**: Full lineage from source → model → metric → exposure
- **Impact Analysis**: See what breaks when metrics change

## Summary

Exposures are essential for:
- ✅ **Documentation**: Catalog all metric usage
- ✅ **Governance**: Track ownership and usage
- ✅ **Impact Analysis**: Understand change impact
- ✅ **Lineage**: Complete data lineage tracking
- ✅ **Collaboration**: Share metric usage across teams

