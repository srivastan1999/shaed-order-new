import axios, { AxiosError } from 'axios';

// Use Next.js proxy in browser, direct URL in server-side or if proxy not available
const getApiBaseUrl = () => {
  // Check if explicit API URL is set (for local development)
  const explicitUrl = process.env.NEXT_PUBLIC_API_URL;
  
  // If explicit URL is set and it's a full URL (not relative), use it directly
  if (explicitUrl && (explicitUrl.startsWith('http://') || explicitUrl.startsWith('https://'))) {
    return explicitUrl;
  }
  
  // In browser, use relative URLs to leverage Next.js rewrites (avoids CORS)
  if (typeof window !== 'undefined') {
    // Check if we should use proxy (default: true for development and production)
    const useProxy = process.env.NEXT_PUBLIC_USE_PROXY !== 'false';
    if (useProxy && !explicitUrl) {
      // Use relative URLs - Next.js/Vercel will proxy to backend
      // In production on Vercel, this will route to /api/* serverless function
      return '/api';
    }
  }
  // Fallback to direct URL (for server-side rendering or explicit URL)
  return explicitUrl || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes timeout for long-running queries
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] Making ${config.method?.toUpperCase()} request to: ${config.url}`);
    console.log(`[API] Full URL: ${config.baseURL}${config.url}`);
    console.log(`[API] Params:`, config.params);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response received from: ${response.config.url}`, response.status);
    return response;
  },
  (error: AxiosError) => {
    console.error('[API] Response error:', {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      responseData: error.response?.data,
    });
    
    // Handle network errors
    if (!error.response) {
      if (error.code === 'ECONNREFUSED') {
        error.message = `Cannot connect to backend server at ${API_BASE_URL}. Please ensure the backend is running. Check: 1) Backend is started (run ./start_backend.sh), 2) Backend is listening on port 8000, 3) No firewall blocking the connection.`;
      } else if (error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
        error.message = `Request timeout. The backend server at ${API_BASE_URL} took too long to respond (over 5 minutes). The query may be too complex or the server may be overloaded.`;
      } else if (error.message.includes('Network Error') || error.message.includes('ERR_NETWORK')) {
        error.message = `Network error: Cannot reach backend server at ${API_BASE_URL}. Possible causes: 1) Backend is not running, 2) CORS issue (check backend CORS settings), 3) Network connectivity problem. Error code: ${error.code || 'N/A'}`;
      } else if (error.code === 'ERR_CORS') {
        error.message = `CORS error: The backend at ${API_BASE_URL} is blocking requests from this origin. Check backend CORS configuration.`;
      } else {
        error.message = `Network error: ${error.message || 'Unknown network error'}. Backend URL: ${API_BASE_URL}. Error code: ${error.code || 'N/A'}`;
      }
    } else {
      // Server responded with error status
      const status = error.response.status;
      const detail = (error.response.data as any)?.detail || error.response.statusText;
      error.message = `Server error (${status}): ${detail}`;
    }
    // Re-throw the error so it can be handled by the calling code
    return Promise.reject(error);
  }
);

export interface FieldChangeRow {
  Order_Number: string;
  Body_Code: string;
  Model_Year: number;
  Customer_Name: string;
  VIN: string;
  Field_Name?: string;  // For regular comparison
  Ford_Field_Name?: string;  // For DB comparison
  Old_Value?: string;  // For regular comparison
  Ford_Old_Value?: string;  // For DB comparison
  New_Value?: string;  // For regular comparison
  Ford_New_Value?: string;  // For DB comparison
  DB_Orders_Value?: string;  // For DB comparison
  DB_Orders_Field_Name?: string;  // For DB comparison
  Sync_Status?: string;  // For DB comparison: MATCH, MISMATCH, NO_MAPPING
  UniqueCode?: string;  // For DB comparison
  old_date: string;
  new_date: string;
}

export interface FieldComparisonResponse {
  data: FieldChangeRow[];
  total: number;
  limit?: number;
  offset: number;
  old_date: string;
  new_date: string;
  auto_fetched_dates?: string[];
  fetch_results?: Record<string, any>;
}

export interface FieldComparisonStats {
  total_changes: number;
  unique_orders_affected: number;
  unique_fields_changed: number;
  field_statistics: Array<{
    field_name: string;
    change_count: number;
  }>;
  old_date: string;
  new_date: string;
}

export const apiClient = {
  // Health check
  async healthCheck(): Promise<{ status: string; bigquery?: string }> {
    const response = await api.get('/health');
    return response.data;
  },

  // Get field comparison
  async getFieldComparison(
    oldDate: string,
    newDate: string,
    limit?: number,
    offset: number = 0,
    autoFetch: boolean = true,
    queryType: 'db_comparison' | 'field_comparison' = 'db_comparison',
    dbOrdersDate?: string
  ): Promise<FieldComparisonResponse> {
    const params: any = {
      old_date: oldDate,
      new_date: newDate,
      offset,
      auto_fetch: autoFetch,
      query_type: queryType,
    };
    if (limit) params.limit = limit;
    if (dbOrdersDate) params.db_orders_date = dbOrdersDate;

    const response = await api.get<FieldComparisonResponse>(
      '/api/ford-field-comparison',
      { params }
    );
    return response.data;
  },

  // Get statistics
  async getFieldComparisonStats(
    oldDate: string,
    newDate: string
  ): Promise<FieldComparisonStats> {
    const response = await api.get<FieldComparisonStats>(
      '/api/ford-field-comparison/stats',
      {
        params: {
          old_date: oldDate,
          new_date: newDate,
        },
      }
    );
    return response.data;
  },

  // Process and upload date
  async processDate(
    date: string,
    returnData: boolean = true,
    limit?: number
  ): Promise<any> {
    const params: any = {
      date,
      return_data: returnData,
    };
    if (limit) params.limit = limit;

    const response = await api.get('/api/ford-process-date', { params });
    return response.data;
  },
};

