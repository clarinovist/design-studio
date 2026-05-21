import { describe, expect, it } from "vitest";

import { buildPromoCanvasStateFromJob } from "./handoff";

describe("buildPromoCanvasStateFromJob", () => {
  it("builds editable text layers from generated job text", () => {
    const result = buildPromoCanvasStateFromJob({
      resultUrl: "https://cdn.example.com/design.png",
      aspectRatio: "9:16",
      visualPrompt: "clean promo background",
      jobStatus: {
        headline: "DISKON 50%",
        sub_headline: "Khusus akhir pekan",
        cta: "Belanja Sekarang",
        quantum_layout: null,
      },
      brief: {
        headlineOverride: "",
        subHeadlineOverride: "",
        ctaOverride: "",
        productName: "Kopi Susu",
        offerText: "Promo akhir pekan",
      },
    });

    expect(result.backgroundUrl).toBe("https://cdn.example.com/design.png");
    expect(result.elements).toHaveLength(3);
    expect(result.elements.map((item) => item.text)).toEqual([
      "DISKON 50%",
      "Khusus akhir pekan",
      "Belanja Sekarang",
    ]);
  });

  it("falls back to brief copy when generated text is incomplete", () => {
    const result = buildPromoCanvasStateFromJob({
      resultUrl: "https://cdn.example.com/design.png",
      aspectRatio: "1:1",
      visualPrompt: "editorial promo visual",
      jobStatus: {
        headline: "",
        sub_headline: null,
        cta: null,
        quantum_layout: null,
      },
      brief: {
        headlineOverride: "PROMO STUDIO FOTO",
        subHeadlineOverride: "Paket wisuda dan keluarga",
        ctaOverride: "Booking Sekarang",
        productName: "Studio Foto",
        offerText: "Diskon soft opening",
      },
    });

    expect(result.elements).toHaveLength(3);
    expect(result.elements.map((item) => item.text)).toEqual([
      "PROMO STUDIO FOTO",
      "Paket wisuda dan keluarga",
      "Booking Sekarang",
    ]);
  });
});
