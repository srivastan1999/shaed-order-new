'use client';

import { useState, useMemo } from 'react';
import { apiClient, FieldChangeRow, FieldComparisonStats } from '@/lib/api';

export default function FordDBComparison() {
  const [oldDate, setOldDate] = useState('2025-11-07');
  const [newDate, setNewDate] = useState('2025-11-10');
  const [dbOrdersDate, setDbOrdersDate] = useState('2025-11-10'); // Separate date for db_orders table
  const [limit, setLimit] = useState(100);
  const [offset, setOffset] = useState(0);
  const [autoFetch, setAutoFetch] = useState(true);
  const [selectedField, setSelectedField] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const [data, setData] = useState<FieldChangeRow[]>([]);
  const [stats, setStats] = useState<FieldComparisonStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [fetchInfo, setFetchInfo] = useState<any>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    setFetchInfo(null);

    try {
      const response = await apiClient.getFieldComparison(
        oldDate,
        newDate,
        limit,
        offset,
        autoFetch,
        'db_comparison', // Use DB comparison query for Ford DB Comparison tab
        dbOrdersDate // Pass separate date for db_orders table
      );

      setData(response.data);
      setTotal(response.total);
      setOffset(response.offset);

      if (response.auto_fetched_dates && response.auto_fetched_dates.length > 0) {
        setFetchInfo({
          dates: response.auto_fetched_dates,
          results: response.fetch_results,
        });
      }
    } catch (err: any) {
      // Handle different types of errors
      let errorMessage = 'Failed to load data';
      
      if (err.response) {
        // Server responded with error status
        errorMessage = err.response.data?.detail || err.response.data?.message || `Server error: ${err.response.status} ${err.response.statusText}`;
      } else if (err.request) {
        // Request was made but no response received
        errorMessage = err.message || 'No response from server. Please check if the backend is running.';
      } else {
        // Error setting up the request
        errorMessage = err.message || 'Failed to make request';
      }
      
      setError(errorMessage);
      console.error('Error loading field comparison:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    setLoading(true);
    setError(null);

    try {
      const statsData = await apiClient.getFieldComparisonStats(oldDate, newDate);
      setStats(statsData);
    } catch (err: any) {
      // Handle different types of errors
      let errorMessage = 'Failed to load stats';
      
      if (err.response) {
        // Server responded with error status
        errorMessage = err.response.data?.detail || err.response.data?.message || `Server error: ${err.response.status} ${err.response.statusText}`;
      } else if (err.request) {
        // Request was made but no response received
        errorMessage = err.message || 'No response from server. Please check if the backend is running.';
      } else {
        // Error setting up the request
        errorMessage = err.message || 'Failed to make request';
      }
      
      setError(errorMessage);
      console.error('Error loading stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePrevious = () => {
    if (offset > 0) {
      const newOffset = Math.max(0, offset - limit);
      setOffset(newOffset);
      loadData();
    }
  };

  const handleNext = () => {
    if (offset + limit < total) {
      setOffset(offset + limit);
      loadData();
    }
  };

  // Check if this is DB comparison (has DB_Orders_Value)
  const isDbComparison = useMemo(() => {
    return data.length > 0 && data.some(row => row.DB_Orders_Value !== undefined);
  }, [data]);

  // Filter data based on selected field and search term
  const filteredData = useMemo(() => {
    let filtered = data;

    // Filter by field name
    if (selectedField !== 'all') {
      const fieldName = isDbComparison ? 'Ford_Field_Name' : 'Field_Name';
      filtered = filtered.filter(row => row[fieldName as keyof typeof row] === selectedField);
    }

    // Filter by search term
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      
      // Check for sync_status filter
      const syncStatusMatch = searchTerm.match(/sync_status:(\w+)/i);
      const syncStatusFilter = syncStatusMatch ? syncStatusMatch[1].toUpperCase() : null;
      const searchWithoutSync = searchTerm.replace(/sync_status:\w+/gi, '').trim();
      
      filtered = filtered.filter(row => {
        // Apply sync status filter if specified
        if (syncStatusFilter) {
          const rowSyncStatus = row.Sync_Status?.toUpperCase();
          if (rowSyncStatus !== syncStatusFilter) {
            return false;
          }
        }
        
        // If there's remaining search text, filter by it
        if (searchWithoutSync) {
          const searchLower = searchWithoutSync.toLowerCase();
          return (
            row.Order_Number?.toLowerCase().includes(searchLower) ||
            row.VIN?.toLowerCase().includes(searchLower) ||
            row.Customer_Name?.toLowerCase().includes(searchLower) ||
            (row.Field_Name || row.Ford_Field_Name)?.toLowerCase().includes(searchLower) ||
            (row.Old_Value || row.Ford_Old_Value)?.toLowerCase().includes(searchLower) ||
            (row.New_Value || row.Ford_New_Value)?.toLowerCase().includes(searchLower) ||
            row.DB_Orders_Value?.toLowerCase().includes(searchLower) ||
            row.DB_Orders_Field_Name?.toLowerCase().includes(searchLower) ||
            row.Sync_Status?.toLowerCase().includes(searchLower)
          );
        }
        
        // If only sync status filter, return true (already filtered above)
        return true;
      });
    }

    return filtered;
  }, [data, selectedField, searchTerm, isDbComparison]);

  // Get unique field names for filter dropdown
  const uniqueFields = useMemo(() => {
    const fieldName = isDbComparison ? 'Ford_Field_Name' : 'Field_Name';
    const fields = new Set(data.map(row => row[fieldName as keyof typeof row]).filter(Boolean));
    return Array.from(fields).sort();
  }, [data, isDbComparison]);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-4 pb-2 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Ford DB Comparison</h2>
            <p className="text-sm text-gray-600 mt-1">
              Cross-verification: Compares <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">ford_oem_orders</code> with <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">db_orders</code> table
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-200 rounded-md">
            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
            <span className="text-xs font-semibold text-blue-700">BigQuery DB</span>
          </div>
        </div>
      </div>
      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Old Date
          </label>
          <input
            type="date"
            value={oldDate}
            onChange={(e) => setOldDate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            New Date (Ford OEM Orders)
          </label>
          <input
            type="date"
            value={newDate}
            onChange={(e) => setNewDate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            DB Orders Date
            <span className="text-xs text-gray-500 ml-1">(for db_orders table)</span>
          </label>
          <input
            type="date"
            value={dbOrdersDate}
            onChange={(e) => setDbOrdersDate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            title="Select the date for the db_orders table (e.g., db_orders_11_10_2025)"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Limit
          </label>
          <select
            value={limit}
            onChange={(e) => {
              setLimit(Number(e.target.value));
              setOffset(0);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={200}>200</option>
            <option value={500}>500</option>
          </select>
        </div>
        <div className="flex items-end gap-2">
          <button
            onClick={loadData}
            disabled={loading}
            className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Loading...' : 'Load Data'}
          </button>
          <button
            onClick={loadStats}
            disabled={loading}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Stats
          </button>
        </div>
      </div>

      {/* Auto-fetch toggle */}
      <div className="mb-4 flex items-center gap-2">
        <input
          type="checkbox"
          id="autoFetch"
          checked={autoFetch}
          onChange={(e) => setAutoFetch(e.target.checked)}
          className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        <label htmlFor="autoFetch" className="text-sm text-gray-700">
          Automatically download and process missing dates
        </label>
      </div>

      {/* Fetch Info */}
      {fetchInfo && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <h3 className="font-semibold text-green-800 mb-2">
            ✓ Auto-fetched {fetchInfo.dates.length} date(s)
          </h3>
          {Object.entries(fetchInfo.results).map(([date, result]: [string, any]) => (
            <div key={date} className="text-sm text-green-700">
              <strong>{date}:</strong> {result.message}
            </div>
          ))}
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <div className="flex items-center gap-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <div className="text-blue-700">
              <strong>Loading data...</strong>
              <p className="text-sm text-blue-600 mt-1">
                This may take 10-30 seconds for large queries. Please wait...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Data Source Info */}
      {data.length > 0 && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <div className="flex items-center gap-2 text-sm text-blue-800">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>
              <strong>Data Source:</strong> BigQuery Database
              {isDbComparison ? (
                <>
                  {' - '}
                  <code className="text-xs">ford_oem_orders</code> vs <code className="text-xs">db_orders</code>
                  {' (Cross-verification enabled)'}
                </>
              ) : (
                <>
                  {' - '}
                  <code className="text-xs">arcane-transit-357411.shaed_elt.ford_oem_orders</code>
                </>
              )}
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      {stats && (
        <>
          <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border-l-4 border-primary-500 shadow-sm">
              <div className="text-sm text-gray-600 uppercase mb-1 font-semibold">Total Changes</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_changes.toLocaleString()}</div>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border-l-4 border-blue-500 shadow-sm">
              <div className="text-sm text-gray-600 uppercase mb-1 font-semibold">Unique Orders</div>
              <div className="text-3xl font-bold text-gray-900">
                {stats.unique_orders_affected.toLocaleString()}
              </div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border-l-4 border-purple-500 shadow-sm">
              <div className="text-sm text-gray-600 uppercase mb-1 font-semibold">Fields Changed</div>
              <div className="text-3xl font-bold text-gray-900">
                {stats.unique_fields_changed}
              </div>
            </div>
          </div>

          {/* Field Statistics */}
          {stats.field_statistics && stats.field_statistics.length > 0 && (
            <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Field Change Statistics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-64 overflow-y-auto">
                {stats.field_statistics.map((fieldStat, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
                  >
                    <span className="text-sm font-medium text-gray-700 truncate flex-1">
                      {fieldStat.field_name}
                    </span>
                    <span className="ml-2 px-2 py-1 bg-primary-100 text-primary-800 text-xs font-semibold rounded">
                      {fieldStat.change_count}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Filters */}
      {data.length > 0 && (
        <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Field
            </label>
            <select
              value={selectedField}
              onChange={(e) => setSelectedField(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Fields</option>
              {uniqueFields.map((field) => (
                <option key={field} value={field}>
                  {field}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {isDbComparison 
                ? "Search (Order, VIN, Customer, Field, Ford Values, DB Values, Sync Status)"
                : "Search (Order, VIN, Customer, Field, Values)"}
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={isDbComparison ? "Search Ford/DB values, sync status..." : "Search..."}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      )}
      
      {/* Sync Status Filter (only for DB comparison) */}
      {data.length > 0 && isDbComparison && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Filter by Sync Status
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => {
                const currentFilter = searchTerm.includes('sync_status:') 
                  ? searchTerm.replace(/sync_status:\w+/g, '').trim()
                  : searchTerm;
                setSearchTerm(currentFilter ? `${currentFilter} sync_status:MATCH` : 'sync_status:MATCH');
              }}
              className="px-3 py-1 text-xs font-medium rounded-md bg-green-100 text-green-800 hover:bg-green-200 transition-colors"
            >
              ✓ MATCH
            </button>
            <button
              onClick={() => {
                const currentFilter = searchTerm.includes('sync_status:') 
                  ? searchTerm.replace(/sync_status:\w+/g, '').trim()
                  : searchTerm;
                setSearchTerm(currentFilter ? `${currentFilter} sync_status:MISMATCH` : 'sync_status:MISMATCH');
              }}
              className="px-3 py-1 text-xs font-medium rounded-md bg-red-100 text-red-800 hover:bg-red-200 transition-colors"
            >
              ✗ MISMATCH
            </button>
            <button
              onClick={() => {
                const currentFilter = searchTerm.includes('sync_status:') 
                  ? searchTerm.replace(/sync_status:\w+/g, '').trim()
                  : searchTerm;
                setSearchTerm(currentFilter ? `${currentFilter} sync_status:NO_MAPPING` : 'sync_status:NO_MAPPING');
              }}
              className="px-3 py-1 text-xs font-medium rounded-md bg-gray-100 text-gray-800 hover:bg-gray-200 transition-colors"
            >
              — NO MAPPING
            </button>
            <button
              onClick={() => {
                setSearchTerm(searchTerm.replace(/sync_status:\w+/g, '').trim());
              }}
              className="px-3 py-1 text-xs font-medium rounded-md bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
            >
              Clear Status Filter
            </button>
          </div>
        </div>
      )}

      {/* Table */}
      {data.length > 0 && (
        <>
          <div className="mb-2 text-sm text-gray-600">
            Showing {filteredData.length} of {data.length} results
            {selectedField !== 'all' && (
              <span className="ml-2">
                (filtered by <span className="font-semibold">{selectedField}</span>)
              </span>
            )}
            {searchTerm && (
              <span className="ml-2">
                (search: <span className="font-semibold">"{searchTerm.replace(/sync_status:\w+/gi, '').trim() || 'sync status filter'}"</span>)
              </span>
            )}
            {isDbComparison && searchTerm.includes('sync_status:') && (
              <span className="ml-2 px-2 py-0.5 rounded bg-blue-100 text-blue-800 text-xs">
                Status: {searchTerm.match(/sync_status:(\w+)/i)?.[1]?.toUpperCase()}
              </span>
            )}
          </div>
          <div className="overflow-x-auto shadow-sm rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unique Code
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Order Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Body Code
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Model Year
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    VIN
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {isDbComparison ? 'Ford Field Name' : 'Field Name'}
                  </th>
                  {isDbComparison && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      DB Orders Field Name
                    </th>
                  )}
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {isDbComparison ? 'Ford Old Value' : 'Old Value'}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {isDbComparison ? 'Ford New Value' : 'New Value'}
                  </th>
                  {isDbComparison && (
                    <>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        DB Orders Value
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Sync Status
                      </th>
                    </>
                  )}
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Old Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    New Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredData.length > 0 ? (
                  filteredData.map((row, idx) => {
                    const fieldName = row.Ford_Field_Name || row.Field_Name || '-';
                    const oldValue = row.Ford_Old_Value || row.Old_Value || '-';
                    const newValue = row.Ford_New_Value || row.New_Value || '-';
                    const dbValue = row.DB_Orders_Value;
                    const syncStatus = row.Sync_Status;
                    
                    // Determine sync status badge color
                    const getSyncStatusBadge = (status?: string) => {
                      if (!status) return null;
                      const statusLower = status.toLowerCase();
                      if (statusLower === 'match') {
                        return <span className="inline-flex items-center px-2 py-1 rounded bg-green-100 text-green-800 text-xs font-semibold">✓ MATCH</span>;
                      } else if (statusLower === 'mismatch') {
                        return <span className="inline-flex items-center px-2 py-1 rounded bg-red-100 text-red-800 text-xs font-semibold">✗ MISMATCH</span>;
                      } else if (statusLower === 'no_mapping') {
                        return <span className="inline-flex items-center px-2 py-1 rounded bg-gray-100 text-gray-800 text-xs font-semibold">— NO MAPPING</span>;
                      }
                      return <span className="inline-flex items-center px-2 py-1 rounded bg-yellow-100 text-yellow-800 text-xs font-semibold">{status}</span>;
                    };
                    
                    return (
                      <tr key={idx} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-700">
                          {row.UniqueCode || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {row.Order_Number || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.Body_Code || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.Model_Year || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title={row.Customer_Name || ''}>
                          {row.Customer_Name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-700">
                          {row.VIN || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-primary-700">
                          {fieldName}
                        </td>
                        {isDbComparison && (
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-700">
                            {row.DB_Orders_Field_Name || '-'}
                          </td>
                        )}
                        <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate" title={oldValue}>
                          <span className="inline-flex items-center px-2 py-1 rounded bg-red-50 text-red-700">
                            {oldValue}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title={newValue}>
                          <span className="inline-flex items-center px-2 py-1 rounded bg-green-50 text-green-700">
                            {newValue}
                          </span>
                        </td>
                        {isDbComparison && (
                          <>
                            <td className="px-6 py-4 text-sm text-gray-700 max-w-xs truncate" title={dbValue || ''}>
                              {dbValue ? (
                                <span className="inline-flex items-center px-2 py-1 rounded bg-blue-50 text-blue-700">
                                  {dbValue}
                                </span>
                              ) : (
                                <span className="text-gray-400">-</span>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              {getSyncStatusBadge(syncStatus)}
                            </td>
                          </>
                        )}
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {row.old_date || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {row.new_date || '-'}
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={isDbComparison ? 13 : 11} className="px-6 py-8 text-center text-gray-500">
                      No results match your filters. Try adjusting your search or field filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="mt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-sm text-gray-700">
              Showing {offset + 1} to {Math.min(offset + limit, total)} of {total.toLocaleString()} results
              {filteredData.length !== data.length && (
                <span className="ml-2 text-gray-500">
                  ({filteredData.length} visible after filtering)
                </span>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={handlePrevious}
                disabled={offset === 0 || loading}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
              >
                ← Previous
              </button>
              <button
                onClick={handleNext}
                disabled={offset + limit >= total || loading}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
              >
                Next →
              </button>
            </div>
          </div>
        </>
      )}

      {/* Empty state */}
      {!loading && data.length === 0 && !error && (
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No data loaded</h3>
          <p className="text-gray-500 mb-4">
            Select dates and click &quot;Load Data&quot; to compare field changes.
          </p>
          <div className="text-sm text-gray-400">
            <p>Default dates: {oldDate} → {newDate}</p>
          </div>
        </div>
      )}
    </div>
  );
}

