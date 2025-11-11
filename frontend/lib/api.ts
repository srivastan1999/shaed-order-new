import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface FieldChangeRow {
  Order_Number: string;
  Body_Code: string;
  Model_Year: number;
  Customer_Name: string;
  VIN: string;
  Field_Name: string;
  Old_Value: string;
  New_Value: string;
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
    autoFetch: boolean = true
  ): Promise<FieldComparisonResponse> {
    const params: any = {
      old_date: oldDate,
      new_date: newDate,
      offset,
      auto_fetch: autoFetch,
    };
    if (limit) params.limit = limit;

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

