import type { DesignJobStatusResponse } from "@/lib/api/types";
import { generateCanvasElementsFromTemplate, type AIParsedData } from "@/lib/templateEngine";
import type { DesignBriefSessionState } from "@/lib/design-brief-session";
import type { PersistedCanvasState } from "@/lib/canvasPersistence";

interface PromoHandoffInput {
  resultUrl: string;
  aspectRatio?: string;
  visualPrompt?: string | null;
  jobStatus: Pick<DesignJobStatusResponse, "headline" | "sub_headline" | "cta" | "quantum_layout">;
  brief: Pick<DesignBriefSessionState, "headlineOverride" | "subHeadlineOverride" | "ctaOverride" | "productName" | "offerText">;
}

function normalizeOptionalText(value: string | null | undefined): string | undefined {
  const normalized = value?.trim();
  return normalized ? normalized : undefined;
}

function buildFallbackCopy(brief: PromoHandoffInput["brief"]): Required<Pick<AIParsedData, "headline" | "sub_headline" | "cta">> {
  const headline = normalizeOptionalText(brief.headlineOverride)
    ?? normalizeOptionalText(brief.productName)
    ?? "PROMO SPESIAL";
  const subHeadline = normalizeOptionalText(brief.subHeadlineOverride)
    ?? normalizeOptionalText(brief.offerText)
    ?? "Penawaran terbaik untuk pelanggan Anda";
  const cta = normalizeOptionalText(brief.ctaOverride) ?? "Hubungi Sekarang";

  return {
    headline,
    sub_headline: subHeadline,
    cta,
  };
}

function safeParseQuantumLayout(value: string | null | undefined): unknown {
  if (!value) return undefined;
  try {
    return JSON.parse(value);
  } catch {
    return undefined;
  }
}

export function buildPromoCanvasStateFromJob(input: PromoHandoffInput): PersistedCanvasState {
  const fallbackCopy = buildFallbackCopy(input.brief);
  const parsedData: AIParsedData = {
    headline: normalizeOptionalText(input.jobStatus.headline) ?? fallbackCopy.headline,
    sub_headline: normalizeOptionalText(input.jobStatus.sub_headline) ?? fallbackCopy.sub_headline,
    cta: normalizeOptionalText(input.jobStatus.cta) ?? fallbackCopy.cta,
  };

  return {
    backgroundUrl: input.resultUrl,
    backgroundColor: "#ffffff",
    originalPrompt: input.visualPrompt ?? null,
    elements: generateCanvasElementsFromTemplate(
      parsedData,
      [],
      1024,
      1024,
      safeParseQuantumLayout(input.jobStatus.quantum_layout),
      0,
    ),
    workflow: {
      sourceTool: "design-brief",
      entryMode: "brief_preview",
      hydratedAt: new Date().toISOString(),
    },
    aspectRatio: input.aspectRatio ?? "1:1",
  };
}
