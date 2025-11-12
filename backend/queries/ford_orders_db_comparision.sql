-- ============================================================================
-- Ford Field Changes Query with DB Orders Cross-Verification - BigQuery (PARAMETERIZED)
-- Compares two versions of ford_oem_orders table based on _source_file_date
-- Returns ONLY records where field values have changed (ignores unchanged/new/deleted)
-- Uses composite key WITH VIN: Order_Number + Body_Code + Model_Year + Customer_Name + VIN
-- 
-- NEW FEATURE: Cross-verifies field changes with db_orders table
-- 1. Identifies field changes between two Ford dates (Old_Value vs New_Value)
-- 2. Creates unique code: Order_Number + Body_Code + Model_Year + "ford"
-- 3. Matches with db_orders using unique code: orderNo + bodyCode + modelYear + oem
-- 4. Maps Ford field names to corresponding db_orders field names
-- 5. Shows side-by-side comparison: Ford_Old_Value, Ford_New_Value, DB_Orders_Value
-- 6. Indicates sync status: MATCH, MISMATCH, or NO_MAPPING
-- ============================================================================
-- 
-- USAGE IN BIGQUERY:
-- 1. In BigQuery UI, click "More" > "Query settings"
-- 2. Under "Query parameters", add parameters:
--    - Parameter name: old_date, Type: DATE, Value: 2025-11-07
--    - Parameter name: new_date, Type: DATE, Value: 2025-11-10
-- 3. The db_orders table name will be automatically replaced based on db_orders_date
--    (format: db_orders_MM_DD_YYYY, e.g., db_orders_11_10_2025 for 2025-11-10)
-- ============================================================================

WITH old_data AS (
    SELECT *
    FROM `arcane-transit-357411.shaed_elt.ford_oem_orders`
    WHERE _source_file_date = @old_date
),

new_data AS (
    SELECT *
    FROM `arcane-transit-357411.shaed_elt.ford_oem_orders`
    WHERE _source_file_date = @new_date
),

-- Find records that exist in both dates with same composite key (WITH VIN)
common_records AS (
    SELECT DISTINCT
        o.Order_Number,
        o.Body_Code,
        o.Model_Year,
        o.Customer_Name,
        o.VIN
    FROM old_data o
    INNER JOIN new_data n
        ON COALESCE(CAST(o.Order_Number AS STRING), '') = COALESCE(CAST(n.Order_Number AS STRING), '')
        AND COALESCE(CAST(o.Body_Code AS STRING), '') = COALESCE(CAST(n.Body_Code AS STRING), '')
        AND COALESCE(CAST(o.Model_Year AS STRING), '') = COALESCE(CAST(n.Model_Year AS STRING), '')
        AND COALESCE(CAST(o.Customer_Name AS STRING), '') = COALESCE(CAST(n.Customer_Name AS STRING), '')
        AND COALESCE(CAST(o.VIN AS STRING), '') = COALESCE(CAST(n.VIN AS STRING), '')
),

-- Get all column names except metadata and composite key fields
-- This query will compare all business fields
field_changes AS (
    SELECT
        c.Order_Number,
        c.Body_Code,
        c.Model_Year,
        c.Customer_Name,
        c.VIN,
        -- Order_Number
        CASE 
            WHEN COALESCE(CAST(o.Order_Number AS STRING), 'NULL') != COALESCE(CAST(n.Order_Number AS STRING), 'NULL')
            THEN 'Order_Number'
            ELSE NULL
        END AS field_name_1,
        CAST(o.Order_Number AS STRING) AS old_value_1,
        CAST(n.Order_Number AS STRING) AS new_value_1,
        -- Model_Year
        CASE 
            WHEN COALESCE(CAST(o.Model_Year AS STRING), 'NULL') != COALESCE(CAST(n.Model_Year AS STRING), 'NULL')
            THEN 'Model_Year'
            ELSE NULL
        END AS field_name_2,
        CAST(o.Model_Year AS STRING) AS old_value_2,
        CAST(n.Model_Year AS STRING) AS new_value_2,
        -- Vehicle_Line
        CASE 
            WHEN COALESCE(CAST(o.Vehicle_Line AS STRING), 'NULL') != COALESCE(CAST(n.Vehicle_Line AS STRING), 'NULL')
            THEN 'Vehicle_Line'
            ELSE NULL
        END AS field_name_3,
        CAST(o.Vehicle_Line AS STRING) AS old_value_3,
        CAST(n.Vehicle_Line AS STRING) AS new_value_3,
        -- Body_Code
        CASE 
            WHEN COALESCE(CAST(o.Body_Code AS STRING), 'NULL') != COALESCE(CAST(n.Body_Code AS STRING), 'NULL')
            THEN 'Body_Code'
            ELSE NULL
        END AS field_name_4,
        CAST(o.Body_Code AS STRING) AS old_value_4,
        CAST(n.Body_Code AS STRING) AS new_value_4,
        -- Body_Code_Description
        CASE 
            WHEN COALESCE(CAST(o.Body_Code_Description AS STRING), 'NULL') != COALESCE(CAST(n.Body_Code_Description AS STRING), 'NULL')
            THEN 'Body_Code_Description'
            ELSE NULL
        END AS field_name_5,
        CAST(o.Body_Code_Description AS STRING) AS old_value_5,
        CAST(n.Body_Code_Description AS STRING) AS new_value_5,
        -- VIN
        CASE 
            WHEN COALESCE(CAST(o.VIN AS STRING), 'NULL') != COALESCE(CAST(n.VIN AS STRING), 'NULL')
            THEN 'VIN'
            ELSE NULL
        END AS field_name_6,
        CAST(o.VIN AS STRING) AS old_value_6,
        CAST(n.VIN AS STRING) AS new_value_6,
        -- Last_Updated
        CASE 
            WHEN COALESCE(CAST(o.Last_Updated AS STRING), 'NULL') != COALESCE(CAST(n.Last_Updated AS STRING), 'NULL')
            THEN 'Last_Updated'
            ELSE NULL
        END AS field_name_7,
        CAST(o.Last_Updated AS STRING) AS old_value_7,
        CAST(n.Last_Updated AS STRING) AS new_value_7,
        -- Status_Last_Updated
        CASE 
            WHEN COALESCE(CAST(o.Status_Last_Updated AS STRING), 'NULL') != COALESCE(CAST(n.Status_Last_Updated AS STRING), 'NULL')
            THEN 'Status_Last_Updated'
            ELSE NULL
        END AS field_name_8,
        CAST(o.Status_Last_Updated AS STRING) AS old_value_8,
        CAST(n.Status_Last_Updated AS STRING) AS new_value_8,
        -- Primary_Status
        CASE 
            WHEN COALESCE(CAST(o.Primary_Status AS STRING), 'NULL') != COALESCE(CAST(n.Primary_Status AS STRING), 'NULL')
            THEN 'Primary_Status'
            ELSE NULL
        END AS field_name_9,
        CAST(o.Primary_Status AS STRING) AS old_value_9,
        CAST(n.Primary_Status AS STRING) AS new_value_9,
        -- Secondary_Status
        CASE 
            WHEN COALESCE(CAST(o.Secondary_Status AS STRING), 'NULL') != COALESCE(CAST(n.Secondary_Status AS STRING), 'NULL')
            THEN 'Secondary_Status'
            ELSE NULL
        END AS field_name_10,
        CAST(o.Secondary_Status AS STRING) AS old_value_10,
        CAST(n.Secondary_Status AS STRING) AS new_value_10,
        -- Estimated_Arrival_Week
        CASE 
            WHEN COALESCE(CAST(o.Estimated_Arrival_Week AS STRING), 'NULL') != COALESCE(CAST(n.Estimated_Arrival_Week AS STRING), 'NULL')
            THEN 'Estimated_Arrival_Week'
            ELSE NULL
        END AS field_name_11,
        CAST(o.Estimated_Arrival_Week AS STRING) AS old_value_11,
        CAST(n.Estimated_Arrival_Week AS STRING) AS new_value_11,
        -- Last_Location
        CASE 
            WHEN COALESCE(CAST(o.Last_Location AS STRING), 'NULL') != COALESCE(CAST(n.Last_Location AS STRING), 'NULL')
            THEN 'Last_Location'
            ELSE NULL
        END AS field_name_12,
        CAST(o.Last_Location AS STRING) AS old_value_12,
        CAST(n.Last_Location AS STRING) AS new_value_12,
        -- Last_Location_Name
        CASE 
            WHEN COALESCE(CAST(o.Last_Location_Name AS STRING), 'NULL') != COALESCE(CAST(n.Last_Location_Name AS STRING), 'NULL')
            THEN 'Last_Location_Name'
            ELSE NULL
        END AS field_name_13,
        CAST(o.Last_Location_Name AS STRING) AS old_value_13,
        CAST(n.Last_Location_Name AS STRING) AS new_value_13,
        -- Last_Location_Code
        CASE 
            WHEN COALESCE(CAST(o.Last_Location_Code AS STRING), 'NULL') != COALESCE(CAST(n.Last_Location_Code AS STRING), 'NULL')
            THEN 'Last_Location_Code'
            ELSE NULL
        END AS field_name_14,
        CAST(o.Last_Location_Code AS STRING) AS old_value_14,
        CAST(n.Last_Location_Code AS STRING) AS new_value_14,
        -- Last_Location_Address
        CASE 
            WHEN COALESCE(CAST(o.Last_Location_Address AS STRING), 'NULL') != COALESCE(CAST(n.Last_Location_Address AS STRING), 'NULL')
            THEN 'Last_Location_Address'
            ELSE NULL
        END AS field_name_15,
        CAST(o.Last_Location_Address AS STRING) AS old_value_15,
        CAST(n.Last_Location_Address AS STRING) AS new_value_15,
        -- Last_Location_Date
        CASE 
            WHEN COALESCE(CAST(o.Last_Location_Date AS STRING), 'NULL') != COALESCE(CAST(n.Last_Location_Date AS STRING), 'NULL')
            THEN 'Last_Location_Date'
            ELSE NULL
        END AS field_name_16,
        CAST(o.Last_Location_Date AS STRING) AS old_value_16,
        CAST(n.Last_Location_Date AS STRING) AS new_value_16,
        -- Conveyance
        CASE 
            WHEN COALESCE(CAST(o.Conveyance AS STRING), 'NULL') != COALESCE(CAST(n.Conveyance AS STRING), 'NULL')
            THEN 'Conveyance'
            ELSE NULL
        END AS field_name_17,
        CAST(o.Conveyance AS STRING) AS old_value_17,
        CAST(n.Conveyance AS STRING) AS new_value_17,
        -- Ordering_Fin_Name
        CASE 
            WHEN COALESCE(CAST(o.Ordering_Fin_Name AS STRING), 'NULL') != COALESCE(CAST(n.Ordering_Fin_Name AS STRING), 'NULL')
            THEN 'Ordering_Fin_Name'
            ELSE NULL
        END AS field_name_18,
        CAST(o.Ordering_Fin_Name AS STRING) AS old_value_18,
        CAST(n.Ordering_Fin_Name AS STRING) AS new_value_18,
        -- Ordering_FIN
        CASE 
            WHEN COALESCE(CAST(o.Ordering_FIN AS STRING), 'NULL') != COALESCE(CAST(n.Ordering_FIN AS STRING), 'NULL')
            THEN 'Ordering_FIN'
            ELSE NULL
        END AS field_name_19,
        CAST(o.Ordering_FIN AS STRING) AS old_value_19,
        CAST(n.Ordering_FIN AS STRING) AS new_value_19,
        -- End_User_Fin_Name
        CASE 
            WHEN COALESCE(CAST(o.End_User_Fin_Name AS STRING), 'NULL') != COALESCE(CAST(n.End_User_Fin_Name AS STRING), 'NULL')
            THEN 'End_User_Fin_Name'
            ELSE NULL
        END AS field_name_20,
        CAST(o.End_User_Fin_Name AS STRING) AS old_value_20,
        CAST(n.End_User_Fin_Name AS STRING) AS new_value_20,
        -- End_User_FIN
        CASE 
            WHEN COALESCE(CAST(o.End_User_FIN AS STRING), 'NULL') != COALESCE(CAST(n.End_User_FIN AS STRING), 'NULL')
            THEN 'End_User_FIN'
            ELSE NULL
        END AS field_name_21,
        CAST(o.End_User_FIN AS STRING) AS old_value_21,
        CAST(n.End_User_FIN AS STRING) AS new_value_21,
        -- Customer_Name
        CASE 
            WHEN COALESCE(CAST(o.Customer_Name AS STRING), 'NULL') != COALESCE(CAST(n.Customer_Name AS STRING), 'NULL')
            THEN 'Customer_Name'
            ELSE NULL
        END AS field_name_22,
        CAST(o.Customer_Name AS STRING) AS old_value_22,
        CAST(n.Customer_Name AS STRING) AS new_value_22,
        -- Customer_First_Initial
        CASE 
            WHEN COALESCE(CAST(o.Customer_First_Initial AS STRING), 'NULL') != COALESCE(CAST(n.Customer_First_Initial AS STRING), 'NULL')
            THEN 'Customer_First_Initial'
            ELSE NULL
        END AS field_name_23,
        CAST(o.Customer_First_Initial AS STRING) AS old_value_23,
        CAST(n.Customer_First_Initial AS STRING) AS new_value_23,
        -- Purchase_Order_Number
        CASE 
            WHEN COALESCE(CAST(o.Purchase_Order_Number AS STRING), 'NULL') != COALESCE(CAST(n.Purchase_Order_Number AS STRING), 'NULL')
            THEN 'Purchase_Order_Number'
            ELSE NULL
        END AS field_name_24,
        CAST(o.Purchase_Order_Number AS STRING) AS old_value_24,
        CAST(n.Purchase_Order_Number AS STRING) AS new_value_24,
        -- Special_Order_Number
        CASE 
            WHEN COALESCE(CAST(o.Special_Order_Number AS STRING), 'NULL') != COALESCE(CAST(n.Special_Order_Number AS STRING), 'NULL')
            THEN 'Special_Order_Number'
            ELSE NULL
        END AS field_name_25,
        CAST(o.Special_Order_Number AS STRING) AS old_value_25,
        CAST(n.Special_Order_Number AS STRING) AS new_value_25,
        -- Order_Type_Code
        CASE 
            WHEN COALESCE(CAST(o.Order_Type_Code AS STRING), 'NULL') != COALESCE(CAST(n.Order_Type_Code AS STRING), 'NULL')
            THEN 'Order_Type_Code'
            ELSE NULL
        END AS field_name_26,
        CAST(o.Order_Type_Code AS STRING) AS old_value_26,
        CAST(n.Order_Type_Code AS STRING) AS new_value_26,
        -- Fleet_Incentive_Program
        CASE 
            WHEN COALESCE(CAST(o.Fleet_Incentive_Program AS STRING), 'NULL') != COALESCE(CAST(n.Fleet_Incentive_Program AS STRING), 'NULL')
            THEN 'Fleet_Incentive_Program'
            ELSE NULL
        END AS field_name_27,
        CAST(o.Fleet_Incentive_Program AS STRING) AS old_value_27,
        CAST(n.Fleet_Incentive_Program AS STRING) AS new_value_27,
        -- PEP_TCO_Code
        CASE 
            WHEN COALESCE(CAST(o.PEP_TCO_Code AS STRING), 'NULL') != COALESCE(CAST(n.PEP_TCO_Code AS STRING), 'NULL')
            THEN 'PEP_TCO_Code'
            ELSE NULL
        END AS field_name_28,
        CAST(o.PEP_TCO_Code AS STRING) AS old_value_28,
        CAST(n.PEP_TCO_Code AS STRING) AS new_value_28,
        -- Ship_Thru_Location
        CASE 
            WHEN COALESCE(CAST(o.Ship_Thru_Location AS STRING), 'NULL') != COALESCE(CAST(n.Ship_Thru_Location AS STRING), 'NULL')
            THEN 'Ship_Thru_Location'
            ELSE NULL
        END AS field_name_29,
        CAST(o.Ship_Thru_Location AS STRING) AS old_value_29,
        CAST(n.Ship_Thru_Location AS STRING) AS new_value_29,
        -- Ship_Thru_Plant
        CASE 
            WHEN COALESCE(CAST(o.Ship_Thru_Plant AS STRING), 'NULL') != COALESCE(CAST(n.Ship_Thru_Plant AS STRING), 'NULL')
            THEN 'Ship_Thru_Plant'
            ELSE NULL
        END AS field_name_30,
        CAST(o.Ship_Thru_Plant AS STRING) AS old_value_30,
        CAST(n.Ship_Thru_Plant AS STRING) AS new_value_30,
        -- Final_Ramp
        CASE 
            WHEN COALESCE(CAST(o.Final_Ramp AS STRING), 'NULL') != COALESCE(CAST(n.Final_Ramp AS STRING), 'NULL')
            THEN 'Final_Ramp'
            ELSE NULL
        END AS field_name_31,
        CAST(o.Final_Ramp AS STRING) AS old_value_31,
        CAST(n.Final_Ramp AS STRING) AS new_value_31,
        -- Order_Received
        CASE 
            WHEN COALESCE(CAST(o.Order_Received AS STRING), 'NULL') != COALESCE(CAST(n.Order_Received AS STRING), 'NULL')
            THEN 'Order_Received'
            ELSE NULL
        END AS field_name_32,
        CAST(o.Order_Received AS STRING) AS old_value_32,
        CAST(n.Order_Received AS STRING) AS new_value_32,
        -- Priority_Code
        CASE 
            WHEN COALESCE(CAST(o.Priority_Code AS STRING), 'NULL') != COALESCE(CAST(n.Priority_Code AS STRING), 'NULL')
            THEN 'Priority_Code'
            ELSE NULL
        END AS field_name_33,
        CAST(o.Priority_Code AS STRING) AS old_value_33,
        CAST(n.Priority_Code AS STRING) AS new_value_33,
        -- Fleet_Numeric_Priority_Code
        CASE 
            WHEN COALESCE(CAST(o.Fleet_Numeric_Priority_Code AS STRING), 'NULL') != COALESCE(CAST(n.Fleet_Numeric_Priority_Code AS STRING), 'NULL')
            THEN 'Fleet_Numeric_Priority_Code'
            ELSE NULL
        END AS field_name_34,
        CAST(o.Fleet_Numeric_Priority_Code AS STRING) AS old_value_34,
        CAST(n.Fleet_Numeric_Priority_Code AS STRING) AS new_value_34,
        -- Scheduled_Date
        CASE 
            WHEN COALESCE(CAST(o.Scheduled_Date AS STRING), 'NULL') != COALESCE(CAST(n.Scheduled_Date AS STRING), 'NULL')
            THEN 'Scheduled_Date'
            ELSE NULL
        END AS field_name_35,
        CAST(o.Scheduled_Date AS STRING) AS old_value_35,
        CAST(n.Scheduled_Date AS STRING) AS new_value_35,
        -- Last_Updated_Estimated_Build_Date
        CASE 
            WHEN COALESCE(CAST(o.Last_Updated_Estimated_Build_Date AS STRING), 'NULL') != COALESCE(CAST(n.Last_Updated_Estimated_Build_Date AS STRING), 'NULL')
            THEN 'Last_Updated_Estimated_Build_Date'
            ELSE NULL
        END AS field_name_36,
        CAST(o.Last_Updated_Estimated_Build_Date AS STRING) AS old_value_36,
        CAST(n.Last_Updated_Estimated_Build_Date AS STRING) AS new_value_36,
        -- Estimated_Build_Date
        CASE 
            WHEN COALESCE(CAST(o.Estimated_Build_Date AS STRING), 'NULL') != COALESCE(CAST(n.Estimated_Build_Date AS STRING), 'NULL')
            THEN 'Estimated_Build_Date'
            ELSE NULL
        END AS field_name_37,
        CAST(o.Estimated_Build_Date AS STRING) AS old_value_37,
        CAST(n.Estimated_Build_Date AS STRING) AS new_value_37,
        -- Plant_Date
        CASE 
            WHEN COALESCE(CAST(o.Plant_Date AS STRING), 'NULL') != COALESCE(CAST(n.Plant_Date AS STRING), 'NULL')
            THEN 'Plant_Date'
            ELSE NULL
        END AS field_name_38,
        CAST(o.Plant_Date AS STRING) AS old_value_38,
        CAST(n.Plant_Date AS STRING) AS new_value_38,
        -- Produced_Date
        CASE 
            WHEN COALESCE(CAST(o.Produced_Date AS STRING), 'NULL') != COALESCE(CAST(n.Produced_Date AS STRING), 'NULL')
            THEN 'Produced_Date'
            ELSE NULL
        END AS field_name_39,
        CAST(o.Produced_Date AS STRING) AS old_value_39,
        CAST(n.Produced_Date AS STRING) AS new_value_39,
        -- Released_Date
        CASE 
            WHEN COALESCE(CAST(o.Released_Date AS STRING), 'NULL') != COALESCE(CAST(n.Released_Date AS STRING), 'NULL')
            THEN 'Released_Date'
            ELSE NULL
        END AS field_name_40,
        CAST(o.Released_Date AS STRING) AS old_value_40,
        CAST(n.Released_Date AS STRING) AS new_value_40,
        -- Shipped_Date
        CASE 
            WHEN COALESCE(CAST(o.Shipped_Date AS STRING), 'NULL') != COALESCE(CAST(n.Shipped_Date AS STRING), 'NULL')
            THEN 'Shipped_Date'
            ELSE NULL
        END AS field_name_41,
        CAST(o.Shipped_Date AS STRING) AS old_value_41,
        CAST(n.Shipped_Date AS STRING) AS new_value_41,
        -- Ship_Through_Received_Date
        CASE 
            WHEN COALESCE(CAST(o.Ship_Through_Received_Date AS STRING), 'NULL') != COALESCE(CAST(n.Ship_Through_Received_Date AS STRING), 'NULL')
            THEN 'Ship_Through_Received_Date'
            ELSE NULL
        END AS field_name_42,
        CAST(o.Ship_Through_Received_Date AS STRING) AS old_value_42,
        CAST(n.Ship_Through_Received_Date AS STRING) AS new_value_42,
        -- Ship_Through_Started_Date
        CASE 
            WHEN COALESCE(CAST(o.Ship_Through_Started_Date AS STRING), 'NULL') != COALESCE(CAST(n.Ship_Through_Started_Date AS STRING), 'NULL')
            THEN 'Ship_Through_Started_Date'
            ELSE NULL
        END AS field_name_43,
        CAST(o.Ship_Through_Started_Date AS STRING) AS old_value_43,
        CAST(n.Ship_Through_Started_Date AS STRING) AS new_value_43,
        -- Ship_Through_Completed_Date
        CASE 
            WHEN COALESCE(CAST(o.Ship_Through_Completed_Date AS STRING), 'NULL') != COALESCE(CAST(n.Ship_Through_Completed_Date AS STRING), 'NULL')
            THEN 'Ship_Through_Completed_Date'
            ELSE NULL
        END AS field_name_44,
        CAST(o.Ship_Through_Completed_Date AS STRING) AS old_value_44,
        CAST(n.Ship_Through_Completed_Date AS STRING) AS new_value_44,
        -- Delivered_Date
        CASE 
            WHEN COALESCE(CAST(o.Delivered_Date AS STRING), 'NULL') != COALESCE(CAST(n.Delivered_Date AS STRING), 'NULL')
            THEN 'Delivered_Date'
            ELSE NULL
        END AS field_name_45,
        CAST(o.Delivered_Date AS STRING) AS old_value_45,
        CAST(n.Delivered_Date AS STRING) AS new_value_45,
        -- Upfitter_Estimated_Start_Date
        CASE 
            WHEN COALESCE(CAST(o.Upfitter_Estimated_Start_Date AS STRING), 'NULL') != COALESCE(CAST(n.Upfitter_Estimated_Start_Date AS STRING), 'NULL')
            THEN 'Upfitter_Estimated_Start_Date'
            ELSE NULL
        END AS field_name_46,
        CAST(o.Upfitter_Estimated_Start_Date AS STRING) AS old_value_46,
        CAST(n.Upfitter_Estimated_Start_Date AS STRING) AS new_value_46,
        -- Upfitter_Estimated_Completion_Date
        CASE 
            WHEN COALESCE(CAST(o.Upfitter_Estimated_Completion_Date AS STRING), 'NULL') != COALESCE(CAST(n.Upfitter_Estimated_Completion_Date AS STRING), 'NULL')
            THEN 'Upfitter_Estimated_Completion_Date'
            ELSE NULL
        END AS field_name_47,
        CAST(o.Upfitter_Estimated_Completion_Date AS STRING) AS old_value_47,
        CAST(n.Upfitter_Estimated_Completion_Date AS STRING) AS new_value_47,
        -- Post_Delivered_Upfitting
        CASE 
            WHEN COALESCE(CAST(o.Post_Delivered_Upfitting AS STRING), 'NULL') != COALESCE(CAST(n.Post_Delivered_Upfitting AS STRING), 'NULL')
            THEN 'Post_Delivered_Upfitting'
            ELSE NULL
        END AS field_name_48,
        CAST(o.Post_Delivered_Upfitting AS STRING) AS old_value_48,
        CAST(n.Post_Delivered_Upfitting AS STRING) AS new_value_48,
        -- Post_Delivered_Upfitting_Last_Updated
        CASE 
            WHEN COALESCE(CAST(o.Post_Delivered_Upfitting_Last_Updated AS STRING), 'NULL') != COALESCE(CAST(n.Post_Delivered_Upfitting_Last_Updated AS STRING), 'NULL')
            THEN 'Post_Delivered_Upfitting_Last_Updated'
            ELSE NULL
        END AS field_name_49,
        CAST(o.Post_Delivered_Upfitting_Last_Updated AS STRING) AS old_value_49,
        CAST(n.Post_Delivered_Upfitting_Last_Updated AS STRING) AS new_value_49,
        -- Ordering_Dealer_Code
        CASE 
            WHEN COALESCE(CAST(o.Ordering_Dealer_Code AS STRING), 'NULL') != COALESCE(CAST(n.Ordering_Dealer_Code AS STRING), 'NULL')
            THEN 'Ordering_Dealer_Code'
            ELSE NULL
        END AS field_name_50,
        CAST(o.Ordering_Dealer_Code AS STRING) AS old_value_50,
        CAST(n.Ordering_Dealer_Code AS STRING) AS new_value_50,
        -- Ordering_Dealer_Name
        CASE 
            WHEN COALESCE(CAST(o.Ordering_Dealer_Name AS STRING), 'NULL') != COALESCE(CAST(n.Ordering_Dealer_Name AS STRING), 'NULL')
            THEN 'Ordering_Dealer_Name'
            ELSE NULL
        END AS field_name_51,
        CAST(o.Ordering_Dealer_Name AS STRING) AS old_value_51,
        CAST(n.Ordering_Dealer_Name AS STRING) AS new_value_51
    FROM common_records c
    INNER JOIN old_data o
        ON COALESCE(CAST(c.Order_Number AS STRING), '') = COALESCE(CAST(o.Order_Number AS STRING), '')
        AND COALESCE(CAST(c.Body_Code AS STRING), '') = COALESCE(CAST(o.Body_Code AS STRING), '')
        AND COALESCE(CAST(c.Model_Year AS STRING), '') = COALESCE(CAST(o.Model_Year AS STRING), '')
        AND COALESCE(CAST(c.Customer_Name AS STRING), '') = COALESCE(CAST(o.Customer_Name AS STRING), '')
        AND COALESCE(CAST(c.VIN AS STRING), '') = COALESCE(CAST(o.VIN AS STRING), '')
        AND o._source_file_date = @old_date
    INNER JOIN new_data n
        ON COALESCE(CAST(c.Order_Number AS STRING), '') = COALESCE(CAST(n.Order_Number AS STRING), '')
        AND COALESCE(CAST(c.Body_Code AS STRING), '') = COALESCE(CAST(n.Body_Code AS STRING), '')
        AND COALESCE(CAST(c.Model_Year AS STRING), '') = COALESCE(CAST(n.Model_Year AS STRING), '')
        AND COALESCE(CAST(c.Customer_Name AS STRING), '') = COALESCE(CAST(n.Customer_Name AS STRING), '')
        AND COALESCE(CAST(c.VIN AS STRING), '') = COALESCE(CAST(n.VIN AS STRING), '')
        AND n._source_file_date = @new_date
),

-- Unpivot all field changes into rows using UNION ALL (BigQuery compatible)
unpivoted_changes AS (
    -- Order_Number
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_1 AS Field_Name,
        old_value_1 AS Old_Value,
        new_value_1 AS New_Value
    FROM field_changes
    WHERE field_name_1 IS NOT NULL
    
    UNION ALL
    
    -- Model_Year
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_2 AS Field_Name,
        old_value_2 AS Old_Value,
        new_value_2 AS New_Value
    FROM field_changes
    WHERE field_name_2 IS NOT NULL
    
    UNION ALL
    
    -- Vehicle_Line
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_3 AS Field_Name,
        old_value_3 AS Old_Value,
        new_value_3 AS New_Value
    FROM field_changes
    WHERE field_name_3 IS NOT NULL
    
    UNION ALL
    
    -- Body_Code
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_4 AS Field_Name,
        old_value_4 AS Old_Value,
        new_value_4 AS New_Value
    FROM field_changes
    WHERE field_name_4 IS NOT NULL
    
    UNION ALL
    
    -- Body_Code_Description
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_5 AS Field_Name,
        old_value_5 AS Old_Value,
        new_value_5 AS New_Value
    FROM field_changes
    WHERE field_name_5 IS NOT NULL
    
    UNION ALL
    
    -- VIN
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_6 AS Field_Name,
        old_value_6 AS Old_Value,
        new_value_6 AS New_Value
    FROM field_changes
    WHERE field_name_6 IS NOT NULL
    
    UNION ALL
    
    -- Last_Updated
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_7 AS Field_Name,
        old_value_7 AS Old_Value,
        new_value_7 AS New_Value
    FROM field_changes
    WHERE field_name_7 IS NOT NULL
    
    UNION ALL
    
    -- Status_Last_Updated
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_8 AS Field_Name,
        old_value_8 AS Old_Value,
        new_value_8 AS New_Value
    FROM field_changes
    WHERE field_name_8 IS NOT NULL
    
    UNION ALL
    
    -- Primary_Status
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_9 AS Field_Name,
        old_value_9 AS Old_Value,
        new_value_9 AS New_Value
    FROM field_changes
    WHERE field_name_9 IS NOT NULL
    
    UNION ALL
    
    -- Secondary_Status
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_10 AS Field_Name,
        old_value_10 AS Old_Value,
        new_value_10 AS New_Value
    FROM field_changes
    WHERE field_name_10 IS NOT NULL
    
    UNION ALL
    
    -- Estimated_Arrival_Week
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_11 AS Field_Name,
        old_value_11 AS Old_Value,
        new_value_11 AS New_Value
    FROM field_changes
    WHERE field_name_11 IS NOT NULL
    
    UNION ALL
    
    -- Last_Location
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_12 AS Field_Name,
        old_value_12 AS Old_Value,
        new_value_12 AS New_Value
    FROM field_changes
    WHERE field_name_12 IS NOT NULL
    
    UNION ALL
    
    -- Last_Location_Name
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_13 AS Field_Name,
        old_value_13 AS Old_Value,
        new_value_13 AS New_Value
    FROM field_changes
    WHERE field_name_13 IS NOT NULL
    
    UNION ALL
    
    -- Last_Location_Code
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_14 AS Field_Name,
        old_value_14 AS Old_Value,
        new_value_14 AS New_Value
    FROM field_changes
    WHERE field_name_14 IS NOT NULL
    
    UNION ALL
    
    -- Last_Location_Address
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_15 AS Field_Name,
        old_value_15 AS Old_Value,
        new_value_15 AS New_Value
    FROM field_changes
    WHERE field_name_15 IS NOT NULL
    
    UNION ALL
    
    -- Last_Location_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_16 AS Field_Name,
        old_value_16 AS Old_Value,
        new_value_16 AS New_Value
    FROM field_changes
    WHERE field_name_16 IS NOT NULL
    
    UNION ALL
    
    -- Conveyance
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_17 AS Field_Name,
        old_value_17 AS Old_Value,
        new_value_17 AS New_Value
    FROM field_changes
    WHERE field_name_17 IS NOT NULL
    
    UNION ALL
    
    -- Ordering_Fin_Name
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_18 AS Field_Name,
        old_value_18 AS Old_Value,
        new_value_18 AS New_Value
    FROM field_changes
    WHERE field_name_18 IS NOT NULL
    
    UNION ALL
    
    -- Ordering_FIN
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_19 AS Field_Name,
        old_value_19 AS Old_Value,
        new_value_19 AS New_Value
    FROM field_changes
    WHERE field_name_19 IS NOT NULL
    
    UNION ALL
    
    -- End_User_Fin_Name
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_20 AS Field_Name,
        old_value_20 AS Old_Value,
        new_value_20 AS New_Value
    FROM field_changes
    WHERE field_name_20 IS NOT NULL
    
    UNION ALL
    
    -- End_User_FIN
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_21 AS Field_Name,
        old_value_21 AS Old_Value,
        new_value_21 AS New_Value
    FROM field_changes
    WHERE field_name_21 IS NOT NULL
    
    UNION ALL
    
    -- Customer_Name
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_22 AS Field_Name,
        old_value_22 AS Old_Value,
        new_value_22 AS New_Value
    FROM field_changes
    WHERE field_name_22 IS NOT NULL
    
    UNION ALL
    
    -- Customer_First_Initial
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_23 AS Field_Name,
        old_value_23 AS Old_Value,
        new_value_23 AS New_Value
    FROM field_changes
    WHERE field_name_23 IS NOT NULL
    
    UNION ALL
    
    -- Purchase_Order_Number
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_24 AS Field_Name,
        old_value_24 AS Old_Value,
        new_value_24 AS New_Value
    FROM field_changes
    WHERE field_name_24 IS NOT NULL
    
    UNION ALL
    
    -- Special_Order_Number
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_25 AS Field_Name,
        old_value_25 AS Old_Value,
        new_value_25 AS New_Value
    FROM field_changes
    WHERE field_name_25 IS NOT NULL
    
    UNION ALL
    
    -- Order_Type_Code
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_26 AS Field_Name,
        old_value_26 AS Old_Value,
        new_value_26 AS New_Value
    FROM field_changes
    WHERE field_name_26 IS NOT NULL
    
    UNION ALL
    
    -- Fleet_Incentive_Program
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_27 AS Field_Name,
        old_value_27 AS Old_Value,
        new_value_27 AS New_Value
    FROM field_changes
    WHERE field_name_27 IS NOT NULL
    
    UNION ALL
    
    -- PEP_TCO_Code
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_28 AS Field_Name,
        old_value_28 AS Old_Value,
        new_value_28 AS New_Value
    FROM field_changes
    WHERE field_name_28 IS NOT NULL
    
    UNION ALL
    
    -- Ship_Thru_Location
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_29 AS Field_Name,
        old_value_29 AS Old_Value,
        new_value_29 AS New_Value
    FROM field_changes
    WHERE field_name_29 IS NOT NULL
    
    UNION ALL
    
    -- Ship_Thru_Plant
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_30 AS Field_Name,
        old_value_30 AS Old_Value,
        new_value_30 AS New_Value
    FROM field_changes
    WHERE field_name_30 IS NOT NULL
    
    UNION ALL
    
    -- Final_Ramp
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_31 AS Field_Name,
        old_value_31 AS Old_Value,
        new_value_31 AS New_Value
    FROM field_changes
    WHERE field_name_31 IS NOT NULL
    
    UNION ALL
    
    -- Order_Received
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_32 AS Field_Name,
        old_value_32 AS Old_Value,
        new_value_32 AS New_Value
    FROM field_changes
    WHERE field_name_32 IS NOT NULL
    
    UNION ALL
    
    -- Priority_Code
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_33 AS Field_Name,
        old_value_33 AS Old_Value,
        new_value_33 AS New_Value
    FROM field_changes
    WHERE field_name_33 IS NOT NULL
    
    UNION ALL
    
    -- Fleet_Numeric_Priority_Code
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_34 AS Field_Name,
        old_value_34 AS Old_Value,
        new_value_34 AS New_Value
    FROM field_changes
    WHERE field_name_34 IS NOT NULL
    
    UNION ALL
    
    -- Scheduled_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_35 AS Field_Name,
        old_value_35 AS Old_Value,
        new_value_35 AS New_Value
    FROM field_changes
    WHERE field_name_35 IS NOT NULL
    
    UNION ALL
    
    -- Last_Updated_Estimated_Build_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_36 AS Field_Name,
        old_value_36 AS Old_Value,
        new_value_36 AS New_Value
    FROM field_changes
    WHERE field_name_36 IS NOT NULL
    
    UNION ALL
    
    -- Estimated_Build_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_37 AS Field_Name,
        old_value_37 AS Old_Value,
        new_value_37 AS New_Value
    FROM field_changes
    WHERE field_name_37 IS NOT NULL
    
    UNION ALL
    
    -- Plant_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_38 AS Field_Name,
        old_value_38 AS Old_Value,
        new_value_38 AS New_Value
    FROM field_changes
    WHERE field_name_38 IS NOT NULL
    
    UNION ALL
    
    -- Produced_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_39 AS Field_Name,
        old_value_39 AS Old_Value,
        new_value_39 AS New_Value
    FROM field_changes
    WHERE field_name_39 IS NOT NULL
    
    UNION ALL
    
    -- Released_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_40 AS Field_Name,
        old_value_40 AS Old_Value,
        new_value_40 AS New_Value
    FROM field_changes
    WHERE field_name_40 IS NOT NULL
    
    UNION ALL
    
    -- Shipped_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_41 AS Field_Name,
        old_value_41 AS Old_Value,
        new_value_41 AS New_Value
    FROM field_changes
    WHERE field_name_41 IS NOT NULL
    
    UNION ALL
    
    -- Ship_Through_Received_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_42 AS Field_Name,
        old_value_42 AS Old_Value,
        new_value_42 AS New_Value
    FROM field_changes
    WHERE field_name_42 IS NOT NULL
    
    UNION ALL
    
    -- Ship_Through_Started_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_43 AS Field_Name,
        old_value_43 AS Old_Value,
        new_value_43 AS New_Value
    FROM field_changes
    WHERE field_name_43 IS NOT NULL
    
    UNION ALL
    
    -- Ship_Through_Completed_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_44 AS Field_Name,
        old_value_44 AS Old_Value,
        new_value_44 AS New_Value
    FROM field_changes
    WHERE field_name_44 IS NOT NULL
    
    UNION ALL
    
    -- Delivered_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_45 AS Field_Name,
        old_value_45 AS Old_Value,
        new_value_45 AS New_Value
    FROM field_changes
    WHERE field_name_45 IS NOT NULL
    
    UNION ALL
    
    -- Upfitter_Estimated_Start_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_46 AS Field_Name,
        old_value_46 AS Old_Value,
        new_value_46 AS New_Value
    FROM field_changes
    WHERE field_name_46 IS NOT NULL
    
    UNION ALL
    
    -- Upfitter_Estimated_Completion_Date
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_47 AS Field_Name,
        old_value_47 AS Old_Value,
        new_value_47 AS New_Value
    FROM field_changes
    WHERE field_name_47 IS NOT NULL
    
    UNION ALL
    
    -- Post_Delivered_Upfitting
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_48 AS Field_Name,
        old_value_48 AS Old_Value,
        new_value_48 AS New_Value
    FROM field_changes
    WHERE field_name_48 IS NOT NULL
    
    UNION ALL
    
    -- Post_Delivered_Upfitting_Last_Updated
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_49 AS Field_Name,
        old_value_49 AS Old_Value,
        new_value_49 AS New_Value
    FROM field_changes
    WHERE field_name_49 IS NOT NULL
    
    UNION ALL
    
    -- Ordering_Dealer_Code
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_50 AS Field_Name,
        old_value_50 AS Old_Value,
        new_value_50 AS New_Value
    FROM field_changes
    WHERE field_name_50 IS NOT NULL
    
    UNION ALL
    
    -- Ordering_Dealer_Name
    SELECT
        Order_Number,
        Body_Code,
        Model_Year,
        Customer_Name,
        VIN,
        field_name_51 AS Field_Name,
        old_value_51 AS Old_Value,
        new_value_51 AS New_Value
    FROM field_changes
    WHERE field_name_51 IS NOT NULL
),
ford_changes_with_code AS (
SELECT
    Order_Number,
    Body_Code,
    Model_Year,
    Customer_Name,
    VIN,
    Field_Name,
    Old_Value,
    New_Value,
    CAST(@old_date AS STRING) AS old_date,
    CAST(@new_date AS STRING) AS new_date,
        -- Create unique code: Order_Number + Body_Code + Model_Year + "ford"
        CONCAT(
            COALESCE(CAST(Order_Number AS STRING), ''),
            '||',
            COALESCE(CAST(Body_Code AS STRING), ''),
            '||',
            COALESCE(CAST(Model_Year AS STRING), ''),
            '||',
            'ford'
        ) AS UniqueCode
FROM unpivoted_changes
),
-- Get db_orders data with unique code
db_orders_data AS (
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
    FROM `arcane-transit-357411.shaed_elt.DB_ORDERS_TABLE_PLACEHOLDER`  -- Will be replaced with actual table name (format: db_orders_MM_DD_YYYY)
    WHERE oem = 'Ford' OR oem = 'ford'
),
-- Map Ford field names to db_orders field names and get corresponding values
field_mapping AS (
    SELECT
        fc.Order_Number,
        fc.Body_Code,
        fc.Model_Year,
        fc.Customer_Name,
        fc.VIN,
        fc.Field_Name AS Ford_Field_Name,
        fc.Old_Value AS Ford_Old_Value,
        fc.New_Value AS Ford_New_Value,
        fc.UniqueCode,
        fc.old_date,
        fc.new_date,
        -- Map Ford fields to db_orders fields using standardized mapping document
        -- Format: Ford Field (PascalCase_With_Underscores) -> standardized field
        CASE fc.Field_Name
            -- CORE IDENTIFIERS
            WHEN 'VIN' THEN CAST(do.vin AS STRING)
            WHEN 'Customer_Name' THEN CAST(do.customer AS STRING)
            WHEN 'Order_Number' THEN CAST(do.orderNo AS STRING)
            -- VEHICLE INFORMATION
            WHEN 'Vehicle_Line' THEN CAST(do.model AS STRING)
            WHEN 'Model_Year' THEN CAST(do.modelYear AS STRING)
            WHEN 'Body_Code' THEN CAST(do.bodyCode AS STRING)
            WHEN 'Body_Code_Description' THEN NULL  -- 'description' field doesn't exist in db_orders
            WHEN 'Paint' THEN CAST(do.color AS STRING)  -- Maps to color field
            -- ORDER INFORMATION
            WHEN 'Order_Received' THEN CAST(do.orderDate AS STRING)
            WHEN 'Purchase_Order_Number' THEN CAST(do.po AS STRING)
            -- STATUS FIELDS - These standardized fields don't exist in db_orders, return NULL
            WHEN 'Primary_Status' THEN NULL  -- 'primaryStatus' field doesn't exist in db_orders
            WHEN 'Secondary_Status' THEN CAST(do.stage AS STRING)  -- Map to 'stage' as closest match
            WHEN 'Status_Last_Updated' THEN NULL  -- 'statusDateTime' field doesn't exist in db_orders
            WHEN 'Last_Updated' THEN NULL  -- 'lastUpdatedAt' field doesn't exist in db_orders
            -- DATE/ETA FIELDS - All map to chassisEta
            WHEN 'Estimated_Build_Date' THEN CAST(do.chassisEta AS STRING)
            WHEN 'End_Date' THEN CAST(do.chassisEta AS STRING)  -- Maps to chassisEta
            WHEN 'Estimated_Arrival_Week' THEN CAST(do.chassisEta AS STRING)
            WHEN 'Scheduled_Date' THEN CAST(do.chassisEta AS STRING)
            WHEN 'Plant_Date' THEN CAST(do.chassisEta AS STRING)
            WHEN 'Produced_Date' THEN CAST(do.chassisEta AS STRING)
            WHEN 'Released_Date' THEN CAST(do.chassisEta AS STRING)
            WHEN 'Last_Updated_Estimated_Build_Date' THEN CAST(do.chassisEta AS STRING)
            -- DATE/ETA FIELDS - Map to finalEta
            WHEN 'Delivered_Date' THEN CAST(do.finalEta AS STRING)
            WHEN 'Shipped_Date' THEN CAST(do.finalEta AS STRING)
            -- LOCATION/SHIPPING FIELDS
            WHEN 'Ship_Thru_Location' THEN CAST(do.shipThruLocation AS STRING)
            WHEN 'Last_Location_Code' THEN NULL  -- No mapping available (per mapping table)
            WHEN 'Ship_To_Dealer_Code' THEN CAST(do.shipToLocation AS STRING)  -- Maps to shipToLocation
            -- DEALER INFORMATION
            WHEN 'Ordering_Dealer_Name' THEN NULL  -- 'orderingDealerName' field doesn't exist in db_orders
            -- FIN (Fleet Identification Number) FIELDS
            WHEN 'End_User_Fin_Name' THEN CAST(do.customer AS STRING)
            WHEN 'Ordering_Fin_Name' THEN CAST(do.customer AS STRING)
            WHEN 'OEM' THEN CAST(do.oem AS STRING)  -- Maps to oem field
            -- Additional fields from verification list
            WHEN 'Fleet_Numeric_Priority_Code' THEN NULL  -- 'fleetNumericPriorityCode' field doesn't exist in db_orders
            WHEN 'Conveyance' THEN NULL  -- No mapping available (per mapping table)
            WHEN 'Upfitter_Estimated_Start_Date' THEN NULL  -- No mapping available (per mapping table)
            WHEN 'Upfitter_Estimated_Completion_Date' THEN NULL  -- No mapping available (per mapping table)
            -- Fields with no mapping - explicitly set to NULL
            WHEN 'Post_Delivered_Upfitting' THEN NULL  -- No mapping available
            WHEN 'Post_Delivered_Upfitting_Last_Updated' THEN NULL  -- No mapping available
            WHEN 'Last_Location_Name' THEN NULL  -- No mapping available
            WHEN 'Last_Location_Date' THEN NULL  -- No mapping available
            WHEN 'Last_Location_Address' THEN NULL  -- No mapping available
            WHEN 'Last_Location' THEN NULL  -- No mapping available
            ELSE NULL
        END AS DB_Orders_Value,
        -- Also get the db_orders field name for reference (using standardized mapping)
        CASE fc.Field_Name
            -- CORE IDENTIFIERS
            WHEN 'VIN' THEN 'vin'
            WHEN 'Customer_Name' THEN 'customer'
            WHEN 'Order_Number' THEN 'orderNo'
            -- VEHICLE INFORMATION
            WHEN 'Vehicle_Line' THEN 'model'
            WHEN 'Model_Year' THEN 'modelYear'
            WHEN 'Body_Code' THEN 'bodyCode'
            WHEN 'Body_Code_Description' THEN NULL  -- 'description' field doesn't exist
            WHEN 'Paint' THEN 'color'
            -- ORDER INFORMATION
            WHEN 'Order_Received' THEN 'orderDate'
            WHEN 'Purchase_Order_Number' THEN 'po'
            -- STATUS FIELDS
            WHEN 'Primary_Status' THEN NULL  -- 'primaryStatus' field doesn't exist
            WHEN 'Secondary_Status' THEN 'stage'  -- Map to 'stage' as closest match
            WHEN 'Status_Last_Updated' THEN NULL  -- 'statusDateTime' field doesn't exist
            WHEN 'Last_Updated' THEN NULL  -- 'lastUpdatedAt' field doesn't exist
            -- DATE/ETA FIELDS - All map to chassisEta
            WHEN 'Estimated_Build_Date' THEN 'chassisEta'
            WHEN 'End_Date' THEN 'chassisEta'
            WHEN 'Estimated_Arrival_Week' THEN 'chassisEta'
            WHEN 'Scheduled_Date' THEN 'chassisEta'
            WHEN 'Plant_Date' THEN 'chassisEta'
            WHEN 'Produced_Date' THEN 'chassisEta'
            WHEN 'Released_Date' THEN 'chassisEta'
            WHEN 'Last_Updated_Estimated_Build_Date' THEN 'chassisEta'
            -- DATE/ETA FIELDS - Map to finalEta
            WHEN 'Delivered_Date' THEN 'finalEta'
            WHEN 'Shipped_Date' THEN 'finalEta'
            -- LOCATION/SHIPPING FIELDS
            WHEN 'Ship_Thru_Location' THEN 'shipThruLocation'
            WHEN 'Last_Location_Code' THEN NULL  -- No mapping available (per mapping table)
            WHEN 'Ship_To_Dealer_Code' THEN 'shipToLocation'
            -- DEALER INFORMATION
            WHEN 'Ordering_Dealer_Name' THEN NULL  -- 'orderingDealerName' field doesn't exist
            -- FIN (Fleet Identification Number) FIELDS
            WHEN 'End_User_Fin_Name' THEN 'customer'
            WHEN 'Ordering_Fin_Name' THEN 'customer'
            WHEN 'OEM' THEN 'oem'
            -- Additional fields from verification list
            WHEN 'Fleet_Numeric_Priority_Code' THEN NULL  -- 'fleetNumericPriorityCode' field doesn't exist
            WHEN 'Conveyance' THEN NULL  -- No mapping available (per mapping table)
            WHEN 'Upfitter_Estimated_Start_Date' THEN NULL  -- No mapping available (per mapping table)
            WHEN 'Upfitter_Estimated_Completion_Date' THEN NULL  -- No mapping available (per mapping table)
            -- Fields with no mapping - explicitly set to NULL
            WHEN 'Post_Delivered_Upfitting' THEN NULL  -- No mapping available
            WHEN 'Post_Delivered_Upfitting_Last_Updated' THEN NULL  -- No mapping available
            WHEN 'Last_Location_Name' THEN NULL  -- No mapping available
            WHEN 'Last_Location_Date' THEN NULL  -- No mapping available
            WHEN 'Last_Location_Address' THEN NULL  -- No mapping available
            WHEN 'Last_Location' THEN NULL  -- No mapping available
            ELSE NULL
        END AS DB_Orders_Field_Name
    FROM ford_changes_with_code fc
    LEFT JOIN db_orders_data do
        ON fc.UniqueCode = do.UniqueCode
)

-- Final result: Field changes with db_orders cross-verification
SELECT
    UniqueCode,
    Order_Number,
    Body_Code,
    Model_Year,
    Customer_Name,
    VIN,
    Ford_Field_Name,
    DB_Orders_Field_Name,
    Ford_Old_Value,
    Ford_New_Value,
    DB_Orders_Value,
    -- Check if db_orders value matches Ford new value
    -- Handle date/timestamp format differences by normalizing to DATE format
    CASE 
        WHEN DB_Orders_Value IS NULL THEN 'NO_MAPPING'
        -- Helper: Parse date from various formats (MM/DD/YYYY, YYYY-MM-DD, or timestamp)
        -- Try MM/DD/YYYY format first (common in Ford data)
        WHEN REGEXP_CONTAINS(Ford_New_Value, r'^\d{1,2}/\d{1,2}/\d{4}$')
             AND REGEXP_CONTAINS(DB_Orders_Value, r'^\d{1,2}/\d{1,2}/\d{4}$')
             AND PARSE_DATE('%m/%d/%Y', Ford_New_Value) = PARSE_DATE('%m/%d/%Y', DB_Orders_Value)
        THEN 'MATCH'
        -- Try MM/DD/YYYY vs YYYY-MM-DD or timestamp
        WHEN REGEXP_CONTAINS(Ford_New_Value, r'^\d{1,2}/\d{1,2}/\d{4}$')
             AND (SAFE_CAST(DB_Orders_Value AS DATE) IS NOT NULL 
                  OR SAFE_CAST(DB_Orders_Value AS TIMESTAMP) IS NOT NULL)
             AND PARSE_DATE('%m/%d/%Y', Ford_New_Value) = COALESCE(
                 SAFE_CAST(DB_Orders_Value AS DATE),
                 DATE(SAFE_CAST(DB_Orders_Value AS TIMESTAMP))
             )
        THEN 'MATCH'
        -- Try YYYY-MM-DD or timestamp vs MM/DD/YYYY
        WHEN REGEXP_CONTAINS(DB_Orders_Value, r'^\d{1,2}/\d{1,2}/\d{4}$')
             AND (SAFE_CAST(Ford_New_Value AS DATE) IS NOT NULL 
                  OR SAFE_CAST(Ford_New_Value AS TIMESTAMP) IS NOT NULL)
             AND PARSE_DATE('%m/%d/%Y', DB_Orders_Value) = COALESCE(
                 SAFE_CAST(Ford_New_Value AS DATE),
                 DATE(SAFE_CAST(Ford_New_Value AS TIMESTAMP))
             )
        THEN 'MATCH'
        -- Try to parse as dates and compare (standard formats)
        WHEN SAFE_CAST(Ford_New_Value AS DATE) IS NOT NULL 
             AND SAFE_CAST(DB_Orders_Value AS DATE) IS NOT NULL
             AND SAFE_CAST(Ford_New_Value AS DATE) = SAFE_CAST(DB_Orders_Value AS DATE)
        THEN 'MATCH'
        -- Try to parse as timestamps and compare dates
        WHEN SAFE_CAST(Ford_New_Value AS TIMESTAMP) IS NOT NULL 
             AND SAFE_CAST(DB_Orders_Value AS TIMESTAMP) IS NOT NULL
             AND DATE(SAFE_CAST(Ford_New_Value AS TIMESTAMP)) = DATE(SAFE_CAST(DB_Orders_Value AS TIMESTAMP))
        THEN 'MATCH'
        -- Fallback to exact string comparison
        WHEN COALESCE(CAST(Ford_New_Value AS STRING), 'NULL') = COALESCE(CAST(DB_Orders_Value AS STRING), 'NULL') 
        THEN 'MATCH'
        ELSE 'MISMATCH'
    END AS Sync_Status,
    old_date,
    new_date
FROM field_mapping
ORDER BY Order_Number, Body_Code, Model_Year, Ford_Field_Name;

