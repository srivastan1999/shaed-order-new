'use client';

import Link from 'next/link';
import FordDBComparison from '@/components/FordDBComparison';

export default function FordDBComparisonPage() {
  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        {/* Navigation */}
        <div className="mb-6 flex items-center justify-between">
          <Link
            href="/"
            className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </Link>
          <Link
            href="/ford-comparison"
            className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-2"
          >
            Go to Ford Comparison
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </Link>
        </div>

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Ford DB Comparison
          </h1>
          <p className="text-lg text-gray-600 mb-2">
            Cross-verification with DB Orders
          </p>
          <p className="text-sm text-gray-500">
            Compare Ford orders between two dates and cross-verify with db_orders table to identify sync status and mismatches.
          </p>
        </div>
        <FordDBComparison />
      </div>
    </main>
  );
}

