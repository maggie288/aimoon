"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

const copy = {
  zh: {
    siteName: "AImoon",
    tagline: "AI 驱动的叙事世界",
    discover: "发现故事",
    campZero: "零号基地",
    campZeroDesc: "30 集 · 月球生存圆桌。科幻作家、物理学家、工程师与计算机科学家在沙克尔顿基地的每日对谈。",
    comingSoon: "敬请期待",
    support: "支持我们",
    langSwitch: "中文",
  },
  en: {
    siteName: "AImoon",
    tagline: "AI-powered story worlds",
    discover: "Discover stories",
    campZero: "Camp Zero",
    campZeroDesc: "30 episodes · Lunar survival roundtable. Sci‑fi writer, physicist, engineer & computer scientist at Shackleton Base.",
    comingSoon: "Coming soon",
    support: "Support us",
    langSwitch: "中文",
  },
};

function HomeContent() {
  const searchParams = useSearchParams();
  const lang = searchParams.get("lang") === "zh" ? "zh" : "en";
  const t = copy[lang];
  const href = (path: string) => (path.includes("?") ? path : `${path}${lang === "zh" ? "?lang=zh" : ""}`);

  return (
    <div className="min-h-screen bg-void text-zinc-200 overflow-hidden">
      {/* Subtle grid background */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03]" style={{ backgroundImage: "linear-gradient(#e4e4e7 1px, transparent 1px), linear-gradient(90deg, #e4e4e7 1px, transparent 1px)", backgroundSize: "48px 48px" }} />

      <header className="relative border-b border-white/5 bg-void/80 backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <Link href={href("/")} className="text-white font-semibold tracking-tight text-lg">
            {t.siteName}
          </Link>
          <div className="flex items-center gap-4">
            <Link href={href("/support")} className="text-zinc-400 text-sm hover:text-podcast transition-colors">
              {t.support}
            </Link>
            <Link
              href={lang === "en" ? "/?lang=zh" : "/"}
              className="text-podcast text-sm font-medium hover:underline"
            >
              {lang === "en" ? "中文" : "EN"}
            </Link>
          </div>
        </div>
      </header>

      <main className="relative max-w-5xl mx-auto px-4 sm:px-6 pt-12 sm:pt-16 pb-24">
        <section className="mb-14 sm:mb-18">
          <p className="text-podcast/90 text-xs font-medium uppercase tracking-widest mb-2">
            {t.tagline}
          </p>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white tracking-tight mb-3">
            {t.discover}
          </h1>
          <p className="text-zinc-400 text-base sm:text-lg max-w-xl">
            {lang === "zh" ? "选择故事，进入剧集目录或收听圆桌对谈。" : "Pick a story and browse episodes or listen to the roundtable."}
          </p>
        </section>

        <section className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {/* Camp Zero — clickable */}
          <Link
            href={href("/story/camp-zero")}
            className="group relative rounded-2xl border border-white/10 bg-surface/50 overflow-hidden hover:border-podcast/30 hover:bg-surface/70 transition-all duration-300"
          >
            <div className="aspect-[16/10] relative bg-zinc-900">
              <img
                src="/images-api/cover-camp-zero"
                alt={t.campZero}
                className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-void via-transparent to-transparent opacity-80" />
              <span className="absolute bottom-3 left-3 right-3 text-white font-semibold text-lg drop-shadow-lg">
                {t.campZero}
              </span>
            </div>
            <div className="p-4">
              <p className="text-zinc-400 text-sm line-clamp-2">
                {t.campZeroDesc}
              </p>
              <span className="inline-block mt-2 text-podcast text-sm font-medium group-hover:underline">
                {lang === "zh" ? "进入剧集 →" : "View episodes →"}
              </span>
            </div>
          </Link>

          {/* Placeholder cards — coming soon */}
          {[1, 2].map((i) => (
            <div
              key={i}
              className="rounded-2xl border border-white/5 bg-surface/30 overflow-hidden opacity-75"
              aria-hidden
            >
              <div className="aspect-[16/10] bg-zinc-800/80 flex items-center justify-center">
                <span className="text-zinc-500 text-sm font-medium">{t.comingSoon}</span>
              </div>
              <div className="p-4">
                <p className="text-zinc-500 text-sm">{t.comingSoon}</p>
              </div>
            </div>
          ))}
        </section>
      </main>

      <footer className="relative border-t border-white/5 py-6 text-center text-zinc-500 text-sm">
        AImoon
      </footer>
    </div>
  );
}

export default function HomePage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-void text-zinc-200 flex items-center justify-center"><span className="text-muted">Loading…</span></div>}>
      <HomeContent />
    </Suspense>
  );
}
