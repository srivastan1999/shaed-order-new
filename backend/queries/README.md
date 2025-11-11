# SQL Queries

This directory contains SQL query files used by the backend services.

## Files

### `ford_orders_field_comparison_parameterized.sql`
- **Purpose**: Compares Ford order fields between two dates using BigQuery parameters
- **Parameters**: `@old_date`, `@new_date` (DATE type)
- **Usage**: Used by `BigQueryService.get_ford_field_comparison()` API endpoint
- **Status**: ✅ Active (primary file)

### `ford_orders_field_comparison.sql`
- **Purpose**: Original Ford order field comparison query (hardcoded dates)
- **Usage**: Fallback file if parameterized version is not found
- **Status**: ⚠️ Legacy (fallback only)

## Usage

The backend automatically loads the parameterized version first. If it doesn't exist, it falls back to the original file.

## Adding New Queries

1. Place new SQL files in this directory
2. Update `backend/services/bigquery_service.py` to load the new query
3. Use parameterized queries (`@param_name`) for dynamic values

