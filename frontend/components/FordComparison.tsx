'use client';

import { useState, useMemo } from 'react';
import { apiClient } from '@/lib/api';

export default function FordComparison() {
  const [oldDate, setOldDate] = useState('2025-11-07');
  const [newDate, setNewDate] = useState('2025-11-10');
  const [limit, setLimit] = useState(100);
  const [offset, setOffset] = useState(0);
  const [autoFetch, setAutoFetch] = useState(true);
  const [selectedField, setSelectedField] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Use field_comparison query type for regular Ford Comparison
      const response = await apiClient.getFieldComparison(
        oldDate,
        newDate,
        limit,
        offset,
        autoFetch,
        'field_comparison' // Use field comparison query for Ford Comparison tab
      );

      setData(response.data);
      setTotal(response.total);
      setOffset(response.offset);
    } catch (err: any) {
      let errorMessage = 'Failed to load data';
      
      if (err.response) {
        errorMessage = err.response.data?.detail || err.response.data?.message || `Server error: ${err.response.status}`;
      } else if (err.request) {
        errorMessage = err.message || 'No response from server. Please check if the backend is running.';
      } else {
        errorMessage = err.message || 'Failed to make request';
      }
      
      setError(errorMessage);
      console.error('Error loading Ford comparison:', err);
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

  // Filter data based on selected field and search term
  const filteredData = useMemo(() => {
    let filtered = data;

    // Filter by field name
    if (selectedField !== 'all') {
      filtered = filtered.filter(row => row.Field_Name === selectedField);
    }

    // Filter by search term
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(row =>
        row.Order_Number?.toLowerCase().includes(searchLower) ||
        row.VIN?.toLowerCase().includes(searchLower) ||
        row.Customer_Name?.toLowerCase().includes(searchLower) ||
        row.Field_Name?.toLowerCase().includes(searchLower) ||
        row.Old_Value?.toLowerCase().includes(searchLower) ||
        row.New_Value?.toLowerCase().includes(searchLower)
      );
    }

    return filtered;
  }, [data, selectedField, searchTerm]);

  // Get unique field names for filter dropdown
  const uniqueFields = useMemo(() => {
    const fields = new Set(data.map(row => row.Field_Name).filter(Boolean));
    return Array.from(fields).sort();
  }, [data]);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-4 pb-2 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">Ford Comparison</h2>
        <p className="text-sm text-gray-600 mt-1">
          Compare Ford orders between two dates
        </p>
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
            New Date
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
        </div>
      </div>

      {/* Auto-fetch toggle */}
      <div className="mb-4 flex items-center gap-2">
        <input
          type="checkbox"
          id="autoFetchFord"
          checked={autoFetch}
          onChange={(e) => setAutoFetch(e.target.checked)}
          className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        <label htmlFor="autoFetchFord" className="text-sm text-gray-700">
          Automatically download and process missing dates
        </label>
      </div>

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
              Search (Order, VIN, Customer, Field, Values)
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search orders, VINs, customers, fields, values..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      )}

      {/* Results count */}
      {data.length > 0 && (
        <div className="mb-2 text-sm text-gray-600">
          Showing {filteredData.length} of {data.length} results
          {selectedField !== 'all' && (
            <span className="ml-2">
              (filtered by <span className="font-semibold">{selectedField}</span>)
            </span>
          )}
          {searchTerm && (
            <span className="ml-2">
              (search: <span className="font-semibold">"{searchTerm}"</span>)
            </span>
          )}
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

      {/* Table */}
      {data.length > 0 && (
        <>
          <div className="overflow-x-auto shadow-sm rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
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
                    Field Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Old Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    New Value
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredData.length > 0 ? (
                  filteredData.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 transition-colors">
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
                      {row.Field_Name || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate" title={row.Old_Value || ''}>
                      <span className="inline-flex items-center px-2 py-1 rounded bg-red-50 text-red-700">
                        {row.Old_Value || '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title={row.New_Value || ''}>
                      <span className="inline-flex items-center px-2 py-1 rounded bg-green-50 text-green-700">
                        {row.New_Value || '-'}
                      </span>
                    </td>
                  </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="px-6 py-8 text-center text-gray-500">
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
            Select dates and click &quot;Load Data&quot; to compare Ford orders.
          </p>
          <div className="text-sm text-gray-400">
            <p>Default dates: {oldDate} → {newDate}</p>
          </div>
        </div>
      )}
    </div>
  );
}

