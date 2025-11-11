'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            SHAED Order ELT
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Ford Order Comparison Tools
          </p>
          <p className="text-sm text-gray-500 max-w-2xl mx-auto">
            Compare Ford order fields between two dates to identify changes in order status, locations, dates, and other attributes.
          </p>
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Ford Comparison Card */}
          <Link
            href="/ford-comparison"
            className="group block bg-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 p-8 border-2 border-transparent hover:border-primary-500"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                Ford Comparison
              </h2>
            </div>
            <p className="text-gray-600 mb-4">
              Compare Ford orders between two dates to identify field changes. View old and new values for each changed field.
            </p>
            <div className="flex items-center text-primary-600 font-medium group-hover:text-primary-700">
              <span>Open Comparison</span>
              <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </Link>

          {/* Ford DB Comparison Card */}
          <Link
            href="/ford-db-comparison"
            className="group block bg-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 p-8 border-2 border-transparent hover:border-primary-500"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                Ford DB Comparison
              </h2>
            </div>
            <p className="text-gray-600 mb-4">
              Cross-verify Ford orders with db_orders table. Compare Ford values with DB values and check sync status (MATCH, MISMATCH, NO_MAPPING).
            </p>
            <div className="flex items-center text-primary-600 font-medium group-hover:text-primary-700">
              <span>Open DB Comparison</span>
              <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </Link>
        </div>

        {/* Features Section */}
        <div className="mt-12 bg-white rounded-lg shadow-md p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <div>
                <p className="font-medium text-gray-900">Field-level Comparison</p>
                <p className="text-sm text-gray-600">See exactly which fields changed between dates</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <div>
                <p className="font-medium text-gray-900">Advanced Filtering</p>
                <p className="text-sm text-gray-600">Filter by field name and search across all columns</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <div>
                <p className="font-medium text-gray-900">DB Cross-Verification</p>
                <p className="text-sm text-gray-600">Compare Ford data with db_orders table</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <div>
                <p className="font-medium text-gray-900">Sync Status Tracking</p>
                <p className="text-sm text-gray-600">Identify MATCH, MISMATCH, or NO_MAPPING status</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

