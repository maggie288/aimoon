"use client";

import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import { ConversationView } from "@/components/ConversationView";

interface Agent {
  id: string;
  name: string;
  title: string;
  code_name: string;
  animal: string;
  color: string;
}

interface ContentBlock {
  type: string;
  content?: string;
  media_id?: string;
  description?: string;
}

interface Conversation {
  date: string;
  day: number;
  topic_title: string;
  topic_description: string;
  phase: string;
  messages: Array<{
    role_id: string;
    timestamp: string;
    content_blocks: ContentBlock[];
  }>;
}

export default function DayPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const date = params.date as string;
  const lang = searchParams.get("lang") === "zh" ? "zh" : "en";
  const [agents, setAgents] = useState<Agent[]>([]);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!date) return;
    const isEn = lang === "en";
    const url = isEn ? `/api/conversations/${date}?lang=en` : `/api/conversations/${date}`;
    const agentsUrl = isEn ? "/api/agents?lang=en" : "/api/agents";
    Promise.all([
      fetch(agentsUrl, { cache: "no-store" }).then((r) => r.json()),
      fetch(url, { cache: "no-store" }).then((r) => {
        if (!r.ok) throw new Error(isEn ? "Conversation not found" : "对话未找到");
        return r.json();
      }),
    ])
      .then(([a, c]) => {
        setAgents(a);
        setConversation(c);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [date, lang]);

  if (loading) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center">
        <div className="text-muted font-mono flex items-center gap-2">
          <span className="h-4 w-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
          {lang === "zh" ? "加载对话…" : "Loading…"}
        </div>
      </div>
    );
  }

  if (error || !conversation) {
    return (
      <div className="min-h-screen bg-void flex flex-col items-center justify-center gap-4 px-4">
        <p className="text-red-400 font-mono">{error || (lang === "zh" ? "对话不存在" : "Conversation not found")}</p>
        <Link href={lang === "zh" ? "/story/camp-zero?lang=zh" : "/story/camp-zero"} className="text-accent hover:underline font-mono text-sm">
          ← {lang === "zh" ? "返回剧集列表" : "Back to episodes"}
        </Link>
      </div>
    );
  }

  const nextDate =
    conversation.day < 30
      ? (() => {
          const d = new Date(date + "T12:00:00");
          d.setDate(d.getDate() + 1);
          return d.toISOString().slice(0, 10);
        })()
      : null;
  const nextHref = nextDate
    ? `/day/${nextDate}${lang === "zh" ? "?lang=zh" : ""}`
    : (lang === "zh" ? "/story/camp-zero?lang=zh" : "/story/camp-zero");

  const prevDate =
    conversation.day > 1
      ? (() => {
          const d = new Date(date + "T12:00:00");
          d.setDate(d.getDate() - 1);
          return d.toISOString().slice(0, 10);
        })()
      : null;
  const prevHref = prevDate
    ? `/day/${prevDate}${lang === "zh" ? "?lang=zh" : ""}`
    : (lang === "zh" ? "/story/camp-zero?lang=zh" : "/story/camp-zero");

  return (
    <div className="h-screen min-h-0 bg-void flex flex-col overflow-hidden">
      <header className="flex-shrink-0 border-b border-border/50 bg-void/95 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Link href={lang === "zh" ? "/story/camp-zero?lang=zh" : "/story/camp-zero"} className="text-muted text-sm hover:text-white transition-colors">
              ← {lang === "zh" ? "零号基地" : "Camp Zero"}
            </Link>
            <Link
              href={lang === "zh" ? "/support?lang=zh" : "/support"}
              className="text-xs text-muted hover:text-podcast"
            >
              {lang === "zh" ? "支持我们" : "Support"}
            </Link>
            <Link
              href={lang === "zh" ? `/day/${date}` : `/day/${date}?lang=zh`}
              className="text-xs text-muted hover:text-podcast"
            >
              {lang === "zh" ? "EN" : "中文"}
            </Link>
          </div>
          <span className="text-muted text-xs">Episode {conversation.day}</span>
        </div>
      </header>

      <main className="flex-1 flex flex-col min-h-0" key={`${date}-${(lang || "").toLowerCase() === "en" ? "en" : "zh"}`}>
        <ConversationView
          agents={agents}
          messages={conversation.messages}
          topicTitle={conversation.topic_title}
          topicDescription={conversation.topic_description}
          date={conversation.date}
          day={conversation.day}
          phase={conversation.phase}
          lang={lang}
          prevChapterHref={prevHref}
          prevChapterLabel={prevDate ? (lang === "zh" ? "← 返回上一章" : "← Previous episode") : (lang === "zh" ? "← 返回剧集列表" : "← Back to episodes")}
          nextChapterHref={nextHref}
          nextChapterLabel={nextDate ? (lang === "zh" ? "进入下一章 →" : "Next episode →") : (lang === "zh" ? "返回剧集列表" : "Back to episodes")}
          showEpisodeBar
          durationLabel={lang === "zh" ? "约 1 小时" : "~1 hr"}
          readTranscriptLabel={lang === "zh" ? "阅读文稿" : "Read transcript"}
        />
      </main>
    </div>
  );
}
