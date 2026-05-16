"use client";

import { useState } from "react";
import { Sparkles, Image as ImageIcon, LayoutTemplate, Layers } from "lucide-react";
import Image from "next/image";

// Demo internal untuk menunjukkan alur workflow beta (bukan hasil customer)
const galleryItems = [
  {
    id: 1,
    category: "Makanan & Minuman",
    image: "/images/showcase/sate_ayam.png",
    title: "Promo Sate Ayam Nusantara",
    inputBrief: "Diskon akhir pekan 20%, tone hangat, fokus menu paket keluarga",
    channel: "Instagram Feed",
    exportFormat: "1080x1080 PNG",
    tags: ["Input foto", "Brief singkat", "Siap upload"],
    aspectRatio: "aspect-square"
  },
  {
    id: 2,
    category: "Fashion",
    image: "/images/showcase/batik_model.png",
    title: "Katalog Batik Modern",
    inputBrief: "Highlight detail motif, tampil premium, target pembeli marketplace",
    channel: "Shopee Katalog",
    exportFormat: "1200x1200 JPG",
    tags: ["Input foto", "Auto styling", "Siap katalog"],
    aspectRatio: "aspect-[16/9]"
  },
  {
    id: 3,
    category: "Aksesoris & Lainnya",
    image: "/images/showcase/tas_anyaman.png",
    title: "Promo Tas Anyaman",
    inputBrief: "Produk handmade, nuansa natural, CTA untuk pre-order",
    channel: "WhatsApp Status",
    exportFormat: "1080x1920 PNG",
    tags: ["Input foto", "Caption siap edit", "Siap posting"],
    aspectRatio: "aspect-[4/5]"
  },
  {
    id: 4,
    category: "Makanan & Minuman",
    image: "/images/showcase/es_kopi_susu.png",
    title: "Menu Baru Es Kopi Susu",
    inputBrief: "Launching menu baru, tone clean, ajak order via chat",
    channel: "Instagram Story",
    exportFormat: "1080x1920 JPG",
    tags: ["Input foto", "Headline siap pakai", "Siap promosi"],
    aspectRatio: "aspect-square"
  },
  {
    id: 5,
    category: "Fashion",
    image: "/images/showcase/hijab_fashion.png",
    title: "Campaign Hijab Harian",
    inputBrief: "Koleksi harian, gaya modest, fokus konversi cepat",
    channel: "Tokopedia Feed",
    exportFormat: "1080x1080 PNG",
    tags: ["Input foto", "Brand konsisten", "Siap upload"],
    aspectRatio: "aspect-[9/16]"
  },
  {
    id: 6,
    category: "Aksesoris & Lainnya",
    image: "/images/showcase/skincare_alami.png",
    title: "Skincare Natural Launch",
    inputBrief: "Produk natural, tampil premium, edukasi manfaat utama",
    channel: "Facebook Ads",
    exportFormat: "1200x1500 JPG",
    tags: ["Input foto", "Brief terarah", "Siap iklan"],
    aspectRatio: "aspect-square"
  }
];

const categories = ["Semua", "Makanan & Minuman", "Fashion", "Aksesoris & Lainnya"];

export function ResultGallery() {
  const [activeCategory, setActiveCategory] = useState("Semua");

  const filteredItems = activeCategory === "Semua" 
    ? galleryItems 
    : galleryItems.filter(item => item.category === activeCategory);

  return (
    <div className="w-full py-16 flex flex-col items-center">
      <div className="text-center mb-10">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Contoh Workflow Beta dari Aset Demo Internal</h2>
        <p className="text-slate-400 max-w-2xl mx-auto">
          Ini adalah simulasi alur kerja (bukan hasil customer): input foto produk + brief singkat -&gt; output desain yang siap disesuaikan untuk channel jualan.
        </p>
        <p className="text-xs text-slate-500 mt-3">
          Label: Demo internal untuk validasi workflow beta, bukan testimoni hasil pengguna.
        </p>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap justify-center gap-3 mb-12">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-5 py-2.5 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${
              activeCategory === cat 
                ? "bg-purple-600 text-white shadow-[0_0_15px_rgba(108,43,238,0.4)]" 
                : "bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white border border-white/5"
            }`}
          >
            {cat === "Semua" && <Layers className="w-4 h-4" />}
            {cat === "Makanan & Minuman" && <ImageIcon className="w-4 h-4" />}
            {cat === "Fashion" && <LayoutTemplate className="w-4 h-4" />}
            {cat === "Aksesoris & Lainnya" && <Sparkles className="w-4 h-4" />}
            {cat}
          </button>
        ))}
      </div>

      {/* Workflow Proof Grid */}
      <div className="columns-1 md:columns-2 lg:columns-3 gap-6 w-full max-w-6xl px-4 space-y-6">
        {filteredItems.map((item) => (
          <div key={item.id} className="relative group rounded-3xl overflow-hidden border border-white/10 bg-slate-900 break-inside-avoid">
            <div className={`w-full ${item.aspectRatio} relative overflow-hidden bg-slate-800`}>
              <Image
                src={item.image}
                alt={item.title}
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/35 to-transparent" />
            </div>

            <div className="absolute bottom-0 left-0 w-full p-5">
              <h3 className="text-white font-bold text-lg mb-1">{item.title}</h3>
              <p className="text-slate-200/90 text-xs mb-2 leading-relaxed">{item.inputBrief}</p>
              <div className="flex flex-wrap gap-2 mb-2">
                <span className="bg-blue-500/20 border border-blue-500/30 text-blue-200 text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded-md">
                  {item.channel}
                </span>
                <span className="bg-emerald-500/20 border border-emerald-500/30 text-emerald-200 text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded-md">
                  {item.exportFormat}
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {item.tags.map((tag, idx) => (
                  <span key={idx} className="bg-purple-500/20 border border-purple-500/30 text-purple-300 text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded-md">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Workflow proof legend */}
      <div className="w-full max-w-6xl px-4 mt-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-slate-300">
            <span className="text-purple-300 font-semibold">Step 1:</span> Input foto produk + brief singkat
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-slate-300">
            <span className="text-blue-300 font-semibold">Step 2:</span> Pilih channel output (IG/Shopee/WA/dll)
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-slate-300">
            <span className="text-emerald-300 font-semibold">Step 3:</span> Export format siap upload
          </div>
        </div>
      </div>
    </div>
  );
}
