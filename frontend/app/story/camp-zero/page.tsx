"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { AdSlot } from "@/components/AdSlot";

interface Topic {
  day: number;
  date: string;
  topic_title: string;
  phase: string;
}

const copy = {
  zh: {
    backToLibrary: "← 返回故事",
    headerSub: "30 集 · 圆桌播客",
    heroTitle: "人类从 0 到 1 在月球生活",
    heroDesc: "科幻作家、物理科学家、计算机科学家、机械师 —— 四位顾问在沙克尔顿基地的每日圆桌。每集约 1 小时，生存 → 稳定 → 扩张 → 文明。",
    episodesTotal: "共 30 集",
    episodeList: "剧集列表",
    perEpisode: "约 1 小时",
    footer: "零号营地",
    support: "支持我们",
  },
  en: {
    backToLibrary: "← Back to stories",
    headerSub: "30 episodes · roundtable",
    heroTitle: "From 0 to 1: Living on the Moon",
    heroDesc: "Sci‑fi writer, physicist, computer scientist, engineer — four advisors at Shackleton Base in a daily roundtable. ~1 hour per episode: survival → stability → expansion → civilization.",
    episodesTotal: "30 episodes",
    episodeList: "Episodes",
    perEpisode: "~1 hr",
    footer: "Camp Zero",
    support: "Support us",
  },
};

function CampZeroContent() {
  const searchParams = useSearchParams();
  const lang = searchParams.get("lang") === "zh" ? "zh" : "en";
  const t = copy[lang];

  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const url = lang === "zh" ? "/api/topics" : "/api/topics?lang=en";
    fetch(url)
      .then((r) => r.json())
      .then((data) => {
        setTopics(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [lang]);

  const href = (path: string) => (path.includes("?") ? path : `${path}${lang === "zh" ? "?lang=zh" : ""}`);

  return (
    <div className="min-h-screen bg-void text-zinc-200">
      <header className="border-b border-border/50 bg-void/95 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href={href("/")} className="text-muted text-sm hover:text-white transition-colors">
            {t.backToLibrary}
          </Link>
          <div className="flex items-center gap-3">
            <Link href={href("/support")} className="text-muted text-xs font-medium hover:text-podcast transition-colors">
              {t.support}
            </Link>
            <Link href={lang === "en" ? "/story/camp-zero?lang=zh" : "/story/camp-zero"} className="text-podcast text-xs font-medium hover:underline">
              {lang === "en" ? "中文" : "EN"}
            </Link>
          </div>
        </div>
      </header>

      <section className="max-w-3xl mx-auto px-4 pt-10 pb-8">
        <h1 className="text-2xl md:text-3xl font-semibold text-white mb-2 tracking-tight">
          {t.heroTitle}
        </h1>
        <p className="text-muted text-base leading-relaxed mb-6">
          {t.heroDesc}
        </p>
        <div className="flex flex-wrap items-center gap-3 text-sm text-muted">
          <span>2026.03.05 — 04.03</span>
          <span>·</span>
          <span className="text-podcast-muted">{t.episodesTotal}</span>
        </div>
      </section>

      <section className="max-w-3xl mx-auto px-4 pb-24">
        <h2 className="text-xs font-medium text-muted uppercase tracking-widest mb-5">
          {t.episodeList}
        </h2>
        {loading ? (
          <div className="space-y-2">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-16 rounded-xl bg-surface/60 border border-border/50 animate-pulse" />
            ))}
          </div>
        ) : (
          <ul className="space-y-2">
            {topics.map((topic) => (
              <li key={topic.date}>
                <Link
                  href={href(`/day/${topic.date}`)}
                  className="flex items-center gap-4 rounded-xl border border-border/50 bg-surface/40 px-4 py-3.5 hover:bg-surface/70 hover:border-podcast/20 transition-colors group"
                >
                  <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-podcast/10 text-podcast text-sm font-medium group-hover:bg-podcast/20">
                    {topic.day}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-zinc-200 group-hover:text-white transition-colors line-clamp-1 font-medium">
                      {topic.topic_title}
                    </p>
                    <p className="text-muted text-xs mt-0.5">{topic.date} · {topic.phase}</p>
                  </div>
                  <span className="text-muted text-xs flex-shrink-0">{t.perEpisode}</span>
                  <span className="text-muted text-lg group-hover:text-podcast transition-colors flex-shrink-0" aria-hidden>→</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <aside className="max-w-3xl mx-auto px-4 py-4 flex justify-center">
        <AdSlot format="rectangle" />
      </aside>
      <footer className="border-t border-border/50 py-6 text-center text-muted text-xs">
        <span>{t.footer}</span>
        <span className="mx-2">·</span>
        <Link href={href("/support")} className="hover:text-podcast transition-colors">
          {t.support}
        </Link>
      </footer>
    </div>
  );
}

export default function CampZeroPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-void text-zinc-200 flex items-center justify-center"><span className="text-muted">Loading…</span></div>}>
      <CampZeroContent />
    </Suspense>
  );
}
