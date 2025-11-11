'use client';

import { useState } from 'react';
import FieldComparison from '@/components/FieldComparison';

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          SHAED Order ELT
        </h1>
        <p className="text-gray-600 mb-8">
          Ford Order Field Comparison Tool
        </p>
        <FieldComparison />
      </div>
    </main>
  );
}

