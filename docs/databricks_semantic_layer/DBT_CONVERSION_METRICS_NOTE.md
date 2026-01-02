# dbt MetricFlow Conversion Metrics - Detailed Information

## Overview

dbt MetricFlow supports **true conversion metrics** with time windows and entity-based joins. This is a powerful feature that goes beyond simple ratio metrics.

## Key Capabilities

### ✅ What dbt MetricFlow Conversion Metrics Support

1. **Time-Windowed Conversions**
   - Define conversion windows (e.g., "7 days", "30 days")
   - Tracks conversions within specific time frames
   - Example: "Visits to purchases within 7 days"

2. **Entity-Based Joins**
   - Links base and conversion events via shared entity (e.g., `user_id`, `customer_id`)
   - Handles proper attribution without overcounting
   - Example: User visits → User purchases (linked by user_id)

3. **Base and Conversion Events**
   - Base event: Starting action (e.g., website visit)
   - Conversion event: Target action (e.g., purchase)
   - Can be from different tables/semantic models

4. **Calculation Types**
   - `conversion_rate`: Percentage (conversions / base opportunities)
   - `conversions`: Raw count of conversions

5. **Advanced Features**
   - Join to time spine for handling sparse data
   - Fill nulls with default values
   - Filter base or conversion events
   - Constant properties for additional join conditions

## Requirements

- **MetricFlow Version**: 0.204+ (for full conversion metric support)
- **Semantic Models**: Must define base and conversion measures in separate semantic models
- **Entities**: Must have shared entity (e.g., `user`, `customer`) linking events
- **Time Dimensions**: Must be configured with proper time grains (e.g., `day`)

## Example YAML Definition

```yaml
metrics:
  - name: visit_to_buy_conversion_rate_7d
    description: "Conversion rate from visiting to transaction in 7 days"
    type: conversion
    label: Visit to buy conversion rate (7 day window)
    type_params:
      conversion_type_params:
        entity: user  # Shared entity for joining events
        base_measure:
          name: visits
          fill_nulls_with: 0
          filter: "{{ Dimension('visits__referrer_id') }} = 'facebook'"
        conversion_measure:
          name: buys
          window: 7 days  # Time window for conversion
```

## How It Works

MetricFlow generates optimized SQL that:
1. Joins base and conversion tables on entity and time window
2. Uses window functions for proper attribution
3. Aggregates opportunities and successes
4. Computes conversion rate

## Comparison with Databricks

| Feature | dbt MetricFlow | Databricks Unity Catalog |
|---------|---------------|-------------------------|
| **Time Windows** | ✅ Supported (e.g., 7 days) | ❌ Not supported |
| **Entity-Based Joins** | ✅ Supported (links events) | ❌ Not supported |
| **Cross-Table Conversions** | ✅ Supported (different semantic models) | ❌ Single source only |
| **Simple Percentage Metrics** | ✅ Supported (via ratio metrics) | ✅ Supported (percentage measures) |
| **Setup Complexity** | ⚠️ More complex (requires semantic models) | ✅ Simpler (direct SQL) |

## Our POC Status

In our POC, we did NOT test true conversion metrics. Instead, we used:
- Ratio metrics as conversion-like metrics (e.g., `order_completion_rate`)
- Simple percentage calculations

This was due to:
1. Limited to single fact table (fct_orders)
2. No separate base/conversion event tables
3. Focus on simpler metric types

## When to Use

**Use dbt MetricFlow Conversion Metrics When:**
- You have separate base and conversion event tables
- You need time-windowed conversions (e.g., "visits within 7 days of purchase")
- You need proper entity-based attribution
- You're tracking complex funnels

**Use Databricks Percentage Measures When:**
- You have simple conversion calculations (e.g., completed orders / total orders)
- You don't need time windows
- You want simpler setup
- All data is in a single table

## References

- [dbt MetricFlow Documentation](https://docs.getdbt.com/docs/build/metrics)
- MetricFlow 0.204+ release notes
- Our implementation: `models/semantic/metrics/revenue.yml` (uses ratio metrics as workaround)

