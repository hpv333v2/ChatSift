interface ApiErrorResponse {
  message: string;
  field?: string;
}

export interface DrfErrorResult {
  fieldErrors: Record<string, string>;
  message: string;
}

/**
 * Parse DRF (Django REST Framework) error responses
 * Handles both field-keyed errors and non-field errors
 * Backend returns: {"field": ["error msg"], ...} or {"non_field_errors": ["msg"]}
 */
export const parseDrfError = (error: unknown): DrfErrorResult => {
  const defaultMessage = 'An unexpected error occurred';
  const fieldErrors: Record<string, string> = {};
  let message = defaultMessage;

  // Check if error is an axios error with response
  if (
    error &&
    typeof error === 'object' &&
    'response' in error &&
    error.response &&
    typeof error.response === 'object' &&
    'data' in error.response
  ) {
    const data = error.response.data as any;

    // Handle wrapped error format: {status: "error", message: "...", data: {...}}
    if (data && typeof data === 'object' && 'status' in data && data.status === 'error') {
      if ('message' in data && typeof data.message === 'string') {
        message = data.message;
      }
      // Check for field errors in data property
      if ('data' in data && data.data && typeof data.data === 'object') {
        Object.keys(data.data).forEach((key) => {
          const value = data.data[key];
          if (Array.isArray(value) && value.length > 0) {
            fieldErrors[key] = String(value[0]);
          }
        });
      }
      return { fieldErrors, message };
    }

    // Handle DRF default format: {field: ["error"], ...}
    if (data && typeof data === 'object') {
      const keys = Object.keys(data);
      
      // Check for non_field_errors first
      if ('non_field_errors' in data && Array.isArray(data.non_field_errors)) {
        message = String(data.non_field_errors[0]);
      }
      
      // Parse field errors
      keys.forEach((key) => {
        const value = data[key];
        if (Array.isArray(value) && value.length > 0) {
          if (key === 'non_field_errors') {
            // Already handled above
            if (!message || message === defaultMessage) {
              message = String(value[0]);
            }
          } else {
            fieldErrors[key] = String(value[0]);
          }
        }
      });

      // If we have field errors but no message, use first field error as message
      if (Object.keys(fieldErrors).length > 0 && message === defaultMessage) {
        const firstKey = Object.keys(fieldErrors)[0];
        message = fieldErrors[firstKey];
      }

      return { fieldErrors, message };
    }

    // Handle simple {detail: string} format (403, 404, etc.)
    if (data && typeof data === 'object' && 'detail' in data) {
      message = String(data.detail);
      return { fieldErrors, message };
    }
  }

  // If we have an error message property
  if (
    error &&
    typeof error === 'object' &&
    'message' in error &&
    typeof error.message === 'string'
  ) {
    message = error.message;
  }

  return { fieldErrors, message };
};

// Legacy function for backward compatibility
export const parseApiError = (error: unknown): ApiErrorResponse => {
  const result = parseDrfError(error);
  const firstFieldKey = Object.keys(result.fieldErrors)[0];
  
  return {
    message: result.message,
    field: firstFieldKey,
  };
};

// Made with Bob
