-- ============================================================================
-- Simple Join Query: Connect Orders and Ford Tables using Unique Codes
-- ============================================================================
-- Tables: db_orders_11_07_2025 and ford_oem_orders
-- UPDATE line 30: Choose Ford date (e.g., '2025-11-07')
-- ============================================================================

WITH orders_data AS (
    SELECT 
        *,
        CONCAT(
            COALESCE(CAST(orderNo AS STRING), ''),
            '||',
            COALESCE(CAST(bodyCode AS STRING), ''),
            '||',
            COALESCE(CAST(modelYear AS STRING), ''),
            '||',
            COALESCE(CAST(oem AS STRING), '')
        ) AS UniqueCode
    FROM `arcane-transit-357411.shaed_elt.db_orders_11_07_2025`
    WHERE oem = 'Ford'
),

ford_data AS (
    SELECT 
        *,
        CONCAT(
            COALESCE(CAST(Order_Number AS STRING), ''),
            '||',
            COALESCE(CAST(Body_Code AS STRING), ''),
            '||',
            COALESCE(CAST(Model_Year AS STRING), ''),
            '||',
            'Ford'
        ) AS UniqueCode
    FROM `arcane-transit-357411.shaed_elt.ford_oem_orders`
    WHERE _source_file_date = '2025-11-07'  -- UPDATE: Change to your desired Ford date
)

SELECT 
    o.*,
    f.*
FROM orders_data o
INNER JOIN ford_data f
    ON o.UniqueCode = f.UniqueCode
LIMIT 100;
