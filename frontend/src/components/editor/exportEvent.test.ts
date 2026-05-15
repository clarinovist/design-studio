import { describe, expect, it, vi } from "vitest";

import { buildExportEventPayload, sendExportEvent } from "./exportEvent";

describe("exportEvent helpers", () => {
  it("normalizes jpeg format to jpg payload", () => {
    expect(buildExportEventPayload("jpeg")).toEqual({
      export_format: "jpg",
      job_id: null,
      target_platform: null,
      source: "editor",
    });
  });

  it("warns when response is non-2xx", async () => {
    const warn = vi.fn();
    const fetcher = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      statusText: "Bad Request",
    });

    await sendExportEvent(
      fetcher as unknown as typeof fetch,
      warn,
      "https://example.com/api/designs/123/export-event",
      { Authorization: "Bearer token" },
      buildExportEventPayload("png"),
    );

    expect(warn).toHaveBeenCalledWith("Export event logging failed", {
      status: 400,
      statusText: "Bad Request",
    });
  });

  it("warns when fetch throws network error", async () => {
    const warn = vi.fn();
    const error = new Error("network error");
    const fetcher = vi.fn().mockRejectedValue(error);

    await sendExportEvent(
      fetcher as unknown as typeof fetch,
      warn,
      "https://example.com/api/designs/123/export-event",
      {},
      buildExportEventPayload("png"),
    );

    expect(warn).toHaveBeenCalledWith("Export event logging failed", error);
  });
});
