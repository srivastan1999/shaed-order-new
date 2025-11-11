'use client';

import { useState } from 'react';
import { apiClient, FieldChangeRow, FieldComparisonStats } from '@/lib/api';

export default function FieldComparison() {
  const [oldDate, setOldDate] = useState('2025-11-07');
  const [newDate, setNewDate] = useState('2025-11-10');
  const [limit, setLimit] = useState(100);
  const [offset, setOffset] = useState(0);
  const [autoFetch, setAutoFetch] = useState(true);

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
        autoFetch
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
      setError(err.response?.data?.detail || err.message || 'Failed to load data');
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
      setError(err.response?.data?.detail || err.message || 'Failed to load stats');
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

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
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

      {/* Error */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
          {error}
        </div>
      )}

      {/* Stats */}
      {stats && (
        <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 p-4 rounded-md border-l-4 border-primary-500">
            <div className="text-sm text-gray-600 uppercase mb-1">Total Changes</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_changes}</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-md border-l-4 border-blue-500">
            <div className="text-sm text-gray-600 uppercase mb-1">Unique Orders</div>
            <div className="text-2xl font-bold text-gray-900">
              {stats.unique_orders_affected}
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-md border-l-4 border-purple-500">
            <div className="text-sm text-gray-600 uppercase mb-1">Fields Changed</div>
            <div className="text-2xl font-bold text-gray-900">
              {stats.unique_fields_changed}
            </div>
          </div>
        </div>
      )}

      {/* Table */}
      {data.length > 0 && (
        <>
          <div className="overflow-x-auto">
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
                {data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {row.Order_Number || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {row.Body_Code || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {row.Model_Year || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {row.Customer_Name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {row.VIN || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {row.Field_Name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {row.Old_Value || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {row.New_Value || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {offset + 1} to {Math.min(offset + limit, total)} of {total} results
            </div>
            <div className="flex gap-2">
              <button
                onClick={handlePrevious}
                disabled={offset === 0 || loading}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={handleNext}
                disabled={offset + limit >= total || loading}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}

      {/* Empty state */}
      {!loading && data.length === 0 && !error && (
        <div className="text-center py-12 text-gray-500">
          No data found. Select dates and click "Load Data" to get started.
        </div>
      )}
    </div>
  );
}

