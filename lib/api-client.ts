import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { ApiError } from './types/api';

// All API requests use the same-origin Next.js proxy.
export function getApiBaseUrl(): string {
  return '';
}

const apiClient: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// No API key is exposed to the browser.
// The Next.js server-side proxy adds the backend API key.
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const apiError: ApiError = {
      error: 'Request failed',
      message: error.message,
      statusCode: error.response?.status,
      details: error.response?.data,
    };

    if (error.response) {
      const data = error.response.data as any;

      apiError.error = data?.error || 'Server error';
      apiError.message = data?.message || error.message;
      apiError.details = data?.details || data;

      if (error.response.status === 401) {
        apiError.error = 'Authentication required';
        apiError.message = 'The backend rejected the request.';
      }

      if (error.response.status === 403) {
        apiError.error = 'Access forbidden';
        apiError.message = 'You do not have permission to access this resource.';
      }

      if (error.response.status === 404) {
        apiError.error = 'Resource not found';
        apiError.message = 'The requested resource was not found.';
      }

      if (error.response.status >= 500) {
        apiError.error = 'Server error';
        apiError.message = 'The server encountered an error. Please try again later.';
      }
    } else if (error.request) {
      apiError.error = 'Network error';
      apiError.message = 'Unable to reach the server. Please check your connection.';
    }

    return Promise.reject(apiError);
  }
);

export async function apiRequest<T>(
  config: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.request<T>(config);
  return response.data;
}

export async function apiGet<T>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiRequest<T>({ ...config, method: 'GET', url });
}

export async function apiPost<T>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiRequest<T>({ ...config, method: 'POST', url, data });
}

export async function apiPut<T>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiRequest<T>({ ...config, method: 'PUT', url, data });
}

export async function apiDelete<T>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiRequest<T>({ ...config, method: 'DELETE', url });
}

export default apiClient;
