"use client";

import { useEffect, useState, useRef } from "react";
import { Star } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

type TestimonialItem = {
  id?: string;
  quote: string;
  name: string;
  role: string;
};

const colorClasses = ["bg-purple-500", "bg-blue-500", "bg-emerald-500", "bg-amber-500"];

// Tidak ada fallback testimonial agar social proof tetap jujur.
// Section hanya tampilkan testimoni yang sudah approved dari backend.

function getInitials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");
}

export function TestimonialCarousel() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [testimonials, setTestimonials] = useState<TestimonialItem[]>([]);

  useEffect(() => {
    const loadTestimonials = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/testimonials`);
        if (!response.ok) {
          return;
        }
        const data = (await response.json()) as { items?: TestimonialItem[] };
        if (Array.isArray(data.items) && data.items.length > 0) {
          setTestimonials(data.items);
        }
      } catch {
        // Keep empty state when API is unavailable.
      }
    };

    void loadTestimonials();
  }, []);

  // Auto-scroll logic
  useEffect(() => {
    if (isHovered || testimonials.length === 0) return;

    const interval = setInterval(() => {
      if (scrollRef.current) {
        // Scroll right by 2px every 20ms
        scrollRef.current.scrollLeft += 1;

        // Reset to start if reached the end (approximate)
        if (scrollRef.current.scrollLeft >= scrollRef.current.scrollWidth - scrollRef.current.clientWidth - 5) {
          scrollRef.current.scrollLeft = 0;
        }
      }
    }, 20);

    return () => clearInterval(interval);
  }, [isHovered, testimonials.length]);

  if (testimonials.length === 0) {
    return (
      <div className="w-full py-8 px-4">
        <div className="max-w-3xl mx-auto rounded-2xl border border-white/10 bg-white/5 p-6 text-center">
          <p className="text-sm text-slate-300 font-medium">Belum ada testimoni publik yang disetujui.</p>
          <p className="text-xs text-slate-500 mt-2">Kami tampilkan testimoni setelah ada submission yang lolos review moderasi.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full py-12 relative overflow-hidden">
      <div className="absolute left-0 top-0 bottom-0 w-12 md:w-32 bg-gradient-to-r from-slate-950 to-transparent z-10 pointer-events-none"></div>
      <div className="absolute right-0 top-0 bottom-0 w-12 md:w-32 bg-gradient-to-l from-slate-950 to-transparent z-10 pointer-events-none"></div>
      
      <div 
        ref={scrollRef}
        className="flex gap-6 overflow-x-auto pb-8 pt-4 px-6 md:px-32 hide-scrollbar scroll-smooth"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {/* Double the array for infinite scrolling effect visually if the user scrolls manually */}
        {[...testimonials, ...testimonials].map((t, i) => (
          <div 
            key={`${t.id || t.name}-${i}`} 
            className="flex-none w-[320px] md:w-[400px] bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 md:p-8 flex flex-col gap-6 hover:bg-white/10 transition-colors duration-300 transform hover:-translate-y-1"
          >
            <div className="flex gap-1 text-yellow-500">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star key={star} className="w-4 h-4 fill-current" />
              ))}
            </div>
            
            <p className="text-slate-300 leading-relaxed italic flex-1">
              &quot;{t.quote}&quot;
            </p>
            
            <div className="flex items-center gap-4 mt-auto">
              <div className={`w-12 h-12 rounded-full ${colorClasses[i % colorClasses.length]} flex items-center justify-center text-white font-bold text-lg shadow-lg`}>
                {getInitials(t.name)}
              </div>
              <div>
                <h4 className="font-bold text-white text-sm">{t.name}</h4>
                <p className="text-xs text-slate-400 mt-0.5">{t.role}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
