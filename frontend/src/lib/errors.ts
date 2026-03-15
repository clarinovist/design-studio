import { toast } from 'sonner';

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
  request_id?: string;
}

export class APIError extends Error {
  public code: string;
  public details?: Record<string, any>;
  public requestId?: string;
  public statusCode?: number;

  constructor(response: ErrorResponse, statusCode?: number) {
    super(response.message);
    this.name = 'APIError';
    this.code = response.error;
    this.details = response.details;
    this.requestId = response.request_id;
    this.statusCode = statusCode;
  }
}

const ERROR_MESSAGES: Record<string, string> = {
  NOT_FOUND: 'Data tidak ditemukan.',
  FORBIDDEN: 'Anda tidak memiliki akses.',
  CONFLICT: 'Terjadi konflik data.',
  RATE_LIMIT: 'Anda mengirim terlalu banyak permintaan. Silakan tunggu beberapa saat.',
  EXTERNAL_SERVICE_ERROR: 'Layanan eksternal sedang bermasalah. Silakan coba lagi nanti.',
  INSUFFICIENT_CREDITS: 'Kredit Anda tidak mencukupi untuk melakukan tindakan ini.',
  STORAGE_LIMIT: 'Batas penyimpanan telah tercapai.',
  VALIDATION_ERROR: 'Data yang dimasukkan tidak valid.',
  BAD_REQUEST: 'Permintaan tidak valid.',
  INTERNAL_ERROR: 'Terjadi kesalahan sistem. Tim kami sedang menanganinya.',
};

export function parseAPIError(error: any): ErrorResponse {
  if (error instanceof APIError) {
    return {
      error: error.code,
      message: error.message,
      details: error.details,
      request_id: error.requestId,
    };
  }

  // Handle fetch Response object or simple JSON
  if (error?.error && error?.message) {
    return error as ErrorResponse;
  }

  return {
    error: 'UNKNOWN_ERROR',
    message: error?.message || 'Terjadi kesalahan yang tidak terduga.',
  };
}

export function getUserFriendlyMessage(errorResponse: ErrorResponse): string {
  if (ERROR_MESSAGES[errorResponse.error]) {
    return ERROR_MESSAGES[errorResponse.error];
  }
  return errorResponse.message || 'Terjadi kesalahan yang tidak terduga.';
}

export function handleAPIError(error: any, fallbackMessage: string = 'Terjadi kesalahan') {
  console.error('[API Error]:', error);
  const parsedError = parseAPIError(error);
  const message = getUserFriendlyMessage(parsedError);

  toast.error(message, {
    description: parsedError.request_id ? `Request ID: ${parsedError.request_id}` : undefined,
    duration: 5000,
  });
}
