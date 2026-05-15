export type ExportFormat = "png" | "jpeg" | "pdf";

export interface ExportEventPayload {
  export_format: "png" | "jpg" | "pdf";
  job_id: null;
  target_platform: null;
  source: "editor";
}

export function buildExportEventPayload(format: ExportFormat): ExportEventPayload {
  return {
    export_format: format === "jpeg" ? "jpg" : format,
    job_id: null,
    target_platform: null,
    source: "editor",
  };
}

export async function sendExportEvent(
  fetcher: typeof fetch,
  warn: (...args: unknown[]) => void,
  url: string,
  headers: Record<string, string>,
  payload: ExportEventPayload,
): Promise<void> {
  try {
    const response = await fetcher(url, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      warn("Export event logging failed", {
        status: response.status,
        statusText: response.statusText,
      });
    }
  } catch (error) {
    warn("Export event logging failed", error);
  }
}
