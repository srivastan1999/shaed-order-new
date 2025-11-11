-- ============================================================================
-- Test Query: Verify Matching Logic Between Orders and Ford Tables
-- Simple query to test if unique codes match correctly
-- ============================================================================
-- UPDATE:
-- Line 19: Change orders table (db_orders_11_05_2025 or db_orders_11_07_2025)
-- Line 35: Change Ford date to test different dates
-- ============================================================================

WITH orders_data AS (
    SELECT 
        orderNo,
        bodyCode,
        modelYear,
        oem,
        customer,
        vin,
        CONCAT(
            COALESCE(CAST(orderNo AS STRING), ''),
            '||',
            COALESCE(CAST(bodyCode AS STRING), ''),
            '||',
            COALESCE(CAST(modelYear AS STRING), ''),
            '||',
            COALESCE(CAST(oem AS STRING), '')
        ) AS UniqueCode1
    FROM `arcane-transit-357411.shaed_elt.db_orders_11_07_2025`  -- UPDATE: Choose db_orders_11_05_2025 or db_orders_11_07_2025
    WHERE oem = 'Ford'
),

ford_data AS (
    SELECT 
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        CONCAT(
            COALESCE(CAST(Order_Number AS STRING), ''),
            '||',
            COALESCE(CAST(Body_Code AS STRING), ''),
            '||',
            COALESCE(CAST(Model_Year AS STRING), ''),
            '||',
            'Ford'
        ) AS UniqueCode2
    FROM `arcane-transit-357411.shaed_elt.ford_oem_orders`
    WHERE _source_file_date = '2025-11-07'  -- UPDATE: Change to test different dates (check diagnose_tables.sql for available dates)
)

SELECT 
    'MATCHED' AS match_status,
    o.orderNo AS Orders_orderNo,
    o.bodyCode AS Orders_bodyCode,
    o.modelYear AS Orders_modelYear,
    o.customer AS Orders_customer,
    f.Order_Number AS Ford_Order_Number,
    f.Body_Code AS Ford_Body_Code,
    f.Model_Year AS Ford_Model_Year,
    f.Customer_Name AS Ford_Customer_Name,
    o.UniqueCode1,
    f.UniqueCode2,
    CASE WHEN o.UniqueCode1 = f.UniqueCode2 THEN 'MATCH' ELSE 'NO_MATCH' END AS code_match
FROM orders_data o
INNER JOIN ford_data f
    ON o.UniqueCode1 = f.UniqueCode2

UNION ALL

SELECT 
    'ORDERS_ONLY' AS match_status,
    o.orderNo AS Orders_orderNo,
    o.bodyCode AS Orders_bodyCode,
    o.modelYear AS Orders_modelYear,
    o.customer AS Orders_customer,
    CAST(NULL AS STRING) AS Ford_Order_Number,
    CAST(NULL AS STRING) AS Ford_Body_Code,
    CAST(NULL AS STRING) AS Ford_Model_Year,
    CAST(NULL AS STRING) AS Ford_Customer_Name,
    o.UniqueCode1,
    CAST(NULL AS STRING) AS UniqueCode2,
    'NO_MATCH_IN_FORD' AS code_match
FROM orders_data o
LEFT JOIN ford_data f
    ON o.UniqueCode1 = f.UniqueCode2
WHERE f.UniqueCode2 IS NULL

UNION ALL

SELECT 
    'FORD_ONLY' AS match_status,
    CAST(NULL AS STRING) AS Orders_orderNo,
    CAST(NULL AS STRING) AS Orders_bodyCode,
    CAST(NULL AS STRING) AS Orders_modelYear,
    CAST(NULL AS STRING) AS Orders_customer,
    f.Order_Number AS Ford_Order_Number,
    f.Body_Code AS Ford_Body_Code,
    f.Model_Year AS Ford_Model_Year,
    f.Customer_Name AS Ford_Customer_Name,
    CAST(NULL AS STRING) AS UniqueCode1,
    f.UniqueCode2,
    'NO_MATCH_IN_ORDERS' AS code_match
FROM ford_data f
LEFT JOIN orders_data o
    ON f.UniqueCode2 = o.UniqueCode1
WHERE o.UniqueCode1 IS NULL

ORDER BY match_status, Orders_orderNo, Ford_Order_Number;

