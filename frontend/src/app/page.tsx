import type { Metadata } from "next";
import { Suspense } from "react";

import LandingPageClient from "./LandingPageClient";

export const metadata: Metadata = {
  title: "SmartDesign Studio — Desain AI untuk UMKM | Ajukan Akses Beta + 100 Kredit",
  description:
    "Upload foto produk, jawab brief singkat, lalu dapat desain siap upload. Ajukan akses beta bertahap untuk seller UMKM dan dapat 100 kredit saat akun beta aktif.",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "SmartDesign Studio — Desain AI untuk UMKM | Ajukan Akses Beta + 100 Kredit",
    description:
      "Upload foto produk, jawab brief singkat, lalu dapat desain siap upload. Ajukan akses beta bertahap dan dapat 100 kredit saat akun beta aktif + bonus PDF ide konten UMKM.",
    url: "/",
    siteName: "SmartDesign Studio",
    locale: "id_ID",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "SmartDesign Studio — Desain AI untuk UMKM | Ajukan Akses Beta + 100 Kredit",
    description:
      "Ajukan akses beta SmartDesign untuk seller UMKM. Saat akun beta aktif, dapat 100 kredit awal. Cocok untuk Shopee, Tokopedia, Instagram.",
  },
};

export default function LandingPage() {
  return (
    <Suspense fallback={null}>
      <LandingPageClient />
    </Suspense>
  );
}
