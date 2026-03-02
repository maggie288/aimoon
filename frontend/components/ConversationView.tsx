"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { AgentAvatar } from "./AgentAvatar";
import { MessageBlock } from "./MessageBlock";

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

interface Message {
  role_id: string;
  timestamp: string;
  content_blocks: ContentBlock[];
  audio_url?: string;
}

interface ConversationViewProps {
  agents: Agent[];
  messages: Message[];
  topicTitle: string;
  topicDescription: string;
  date: string;
  day: number;
  phase: string;
  lang?: "zh" | "en";
  /** 返回上一章链接 */
  prevChapterHref?: string;
  prevChapterLabel?: string;
  /** 进入下一章链接，传入后显示在吸顶区内 */
  nextChapterHref?: string;
  nextChapterLabel?: string;
  /** 单集信息条：是否在吸顶区内显示（日期、阶段、标题、阅读文稿等） */
  showEpisodeBar?: boolean;
  durationLabel?: string;
  readTranscriptLabel?: string;
}

function getMessageText(msg: Message): string {
  const parts: string[] = [];
  for (const b of msg.content_blocks || []) {
    if (b.type === "paragraph" && b.content) parts.push(b.content.trim());
  }
  return parts.join(" ");
}

const labels = {
  zh: { play: "播放本集（跟随对话流）", pause: "暂停", playing: "正在播放" },
  en: { play: "Play episode (follow along)", pause: "Pause", playing: "Playing" },
};

export function ConversationView({
  agents,
  messages,
  topicTitle,
  topicDescription,
  date,
  day,
  phase,
  lang = "zh",
  prevChapterHref,
  prevChapterLabel,
  nextChapterHref,
  nextChapterLabel,
  showEpisodeBar = true,
  durationLabel,
  readTranscriptLabel,
}: ConversationViewProps) {
  const t = labels[lang] ?? labels.zh;
  const agentMap = Object.fromEntries(agents.map((a) => [a.id, a]));
  const [activeRole, setActiveRole] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentPlayIndex, setCurrentPlayIndex] = useState(-1);
  const [stickyExpanded, setStickyExpanded] = useState(true);
  const messageRefs = useRef<(HTMLElement | null)[]>([]);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const playbackAudioRef = useRef<HTMLAudioElement | null>(null);

  // 跟随对话流播放：优先 MiniMax TTS，失败则浏览器朗读
  useEffect(() => {
    if (!isPlaying || currentPlayIndex < 0 || currentPlayIndex >= messages.length) {
      if (currentPlayIndex >= messages.length && messages.length > 0) setIsPlaying(false);
      return;
    }
    const msg = messages[currentPlayIndex];
    const text = getMessageText(msg);
    if (!text.trim()) {
      setCurrentPlayIndex((i) => i + 1);
      return;
    }

    let cancelled = false;

    const onDone = () => { if (!cancelled) setCurrentPlayIndex((i) => i + 1); };
    const bindAudio = (audio: HTMLAudioElement, objectUrl?: string) => {
      playbackAudioRef.current = audio;
      const cleanup = () => { playbackAudioRef.current = null; if (objectUrl) URL.revokeObjectURL(objectUrl); onDone(); };
      audio.onended = cleanup;
      audio.onerror = cleanup;
    };

    (async () => {
      // 1) 优先预生成语音（本机 edge-tts 等）
      try {
        const audioUrl = lang === "en" ? `/api/media/audio/${date}/${currentPlayIndex}?lang=en` : `/api/media/audio/${date}/${currentPlayIndex}`;
        const r = await fetch(audioUrl);
        if (r.ok && !cancelled) {
          const blob = await r.blob();
          const url = URL.createObjectURL(blob);
          const audio = new Audio(url);
          bindAudio(audio, url);
          audio.play().catch(() => { URL.revokeObjectURL(url); onDone(); });
          return;
        }
      } catch (_) {}

      // 2) 尝试 MiniMax TTS
      try {
        const r = await fetch("/api/tts/synthesize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, voice_id: msg.role_id }),
        });
        if (r.ok && !cancelled) {
          const blob = await r.blob();
          const url = URL.createObjectURL(blob);
          const audio = new Audio(url);
          bindAudio(audio, url);
          audio.play().catch(() => { URL.revokeObjectURL(url); onDone(); });
          return;
        }
      } catch (_) {}

      // 3) 回退：浏览器语音
      if (cancelled) return;
      const u = new SpeechSynthesisUtterance(text);
      u.lang = "zh-CN";
      u.rate = 0.95;
      const voices = speechSynthesis.getVoices().filter((v) => v.lang.includes("zh") || v.lang.includes("CN") || v.lang === "cmn-Hans-CN");
      if (voices.length > 0) {
        const roleOrder = ["alice", "chenwei", "oldtom", "elena"];
        u.voice = voices[roleOrder.indexOf(msg.role_id) % voices.length] ?? voices[0];
      }
      u.onend = () => { if (!cancelled) setCurrentPlayIndex((i) => i + 1); };
      u.onerror = () => { if (!cancelled) setCurrentPlayIndex((i) => i + 1); };
      speechSynthesis.speak(u);
    })();

    return () => {
      cancelled = true;
      playbackAudioRef.current?.pause();
      playbackAudioRef.current = null;
      speechSynthesis.cancel();
    };
  }, [isPlaying, currentPlayIndex, messages, date, lang]);

  useEffect(() => {
    if (currentPlayIndex < 0 || !messageRefs.current[currentPlayIndex]) return;
    messageRefs.current[currentPlayIndex]?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [currentPlayIndex]);

  const startPlay = () => {
    speechSynthesis.cancel();
    setCurrentPlayIndex(0);
    setIsPlaying(true);
  };
  const stopPlay = () => {
    playbackAudioRef.current?.pause();
    playbackAudioRef.current = null;
    speechSynthesis.cancel();
    setIsPlaying(false);
    setCurrentPlayIndex(-1);
  };

  // 从指定位置播放或暂停：点击进度条或某条消息
  const seekTo = (index: number) => {
    const i = Math.max(0, Math.min(index, messages.length - 1));
    setCurrentPlayIndex(i);
    if (!isPlaying) setIsPlaying(true);
  };
  const toggleAt = (index: number) => {
    if (currentPlayIndex === index && isPlaying) {
      stopPlay();
    } else {
      seekTo(index);
    }
  };

  const progressRef = useRef<HTMLDivElement>(null);
  const onProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const el = progressRef.current;
    if (!el || messages.length === 0) return;
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const pct = Math.max(0, Math.min(1, x / rect.width));
    const index = Math.floor(pct * messages.length);
    toggleAt(index);
  };

  return (
    <div className="flex-1 flex min-h-0 relative">
      {/* 右侧竖向进度条：与播放进度同步 */}
      {messages.length > 0 && (
        <div className="absolute right-0 top-0 bottom-0 w-1.5 bg-surface/80 rounded-l z-[1] pointer-events-none">
          <div
            className="w-full bg-podcast/70 rounded-l transition-[height] duration-200"
            style={{
              height: `${((currentPlayIndex + 1) / messages.length) * 100}%`,
              minHeight: "2px",
            }}
          />
        </div>
      )}
      <div ref={scrollContainerRef} className="flex-1 flex flex-col min-h-0 overflow-y-auto pr-1">
        {/* 吸顶：单集信息 + 展开/收起 + 嘉宾 strip + 播放/下一章 + 进度条 */}
        <div className="sticky top-0 z-10 flex-shrink-0 border-b border-border/50 bg-void backdrop-blur-md">
          {showEpisodeBar && (
            <div className="px-3 sm:px-4 py-2 border-b border-border/50 bg-surface/30 flex flex-wrap items-center gap-2 sm:gap-3">
              <div className="max-w-2xl mx-auto flex flex-wrap items-center gap-2 sm:gap-3 min-w-0 flex-1">
                <span className="flex h-7 w-7 sm:h-8 sm:w-8 flex-shrink-0 items-center justify-center rounded-full bg-podcast/15 text-podcast text-[10px] sm:text-xs font-medium">
                  {day}
                </span>
                <div className="min-w-0 flex-1 basis-0">
                  <p className="text-[10px] text-muted">{date} · {phase}</p>
                  <p className="text-xs font-medium text-white truncate">{topicTitle}</p>
                </div>
                {(durationLabel != null || readTranscriptLabel != null) && stickyExpanded && (
                  <div className="flex-shrink-0 text-right hidden sm:block">
                    {durationLabel != null && (
                      <p className="text-[10px] text-muted">{durationLabel}</p>
                    )}
                    {readTranscriptLabel != null && (
                      <p className="text-[10px] text-muted mt-0.5">{readTranscriptLabel}</p>
                    )}
                  </div>
                )}
              </div>
              <button
                type="button"
                onClick={() => setStickyExpanded((e) => !e)}
                className="flex-shrink-0 rounded-lg border border-border bg-surface/80 px-2 sm:px-2.5 py-1.5 min-h-[44px] sm:min-h-0 text-[10px] text-muted hover:text-white hover:bg-surface transition-colors flex items-center gap-1 touch-manipulation"
                aria-expanded={stickyExpanded}
                title={stickyExpanded ? (lang === "en" ? "Collapse" : "收起") : (lang === "en" ? "Expand" : "展开")}
              >
                <span aria-hidden>{stickyExpanded ? "▲" : "▼"}</span>
                <span>{stickyExpanded ? (lang === "en" ? "Collapse" : "收起") : (lang === "en" ? "Expand" : "展开")}</span>
              </button>
            </div>
          )}
          {stickyExpanded && (
          <>
          <div className="flex items-center justify-center gap-2 py-2 px-3 sm:px-4 overflow-x-auto overflow-y-hidden [-webkit-overflow-scrolling:touch]">
            {agents.map((a) => (
              <button
                key={a.id}
                type="button"
                onClick={() => { if (!isPlaying) setActiveRole(activeRole === a.id ? null : a.id); }}
                className="flex-shrink-0"
              >
                <AgentAvatar
                  roleId={a.id}
                  name={a.name}
                  title={a.title}
                  codeName={a.code_name}
                  active={activeRole === null || activeRole === a.id}
                  compact
                />
              </button>
            ))}
          </div>
          <p className="px-3 sm:px-4 pb-2 text-center text-muted text-xs max-w-2xl mx-auto line-clamp-2 sm:line-clamp-none">
            {topicDescription}
          </p>
          {/* 一排：左侧返回上一章 + 播放，右侧进入下一章 */}
          <div className="px-3 sm:px-4 pb-2 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 max-w-2xl mx-auto">
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 min-h-[44px] sm:min-h-0">
              {prevChapterHref != null && (
                <Link
                  href={prevChapterHref}
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-surface border border-border text-zinc-300 px-3 py-2.5 sm:px-4 text-sm font-medium hover:bg-surface/80 transition-colors flex-shrink-0 min-h-[44px] sm:min-h-0 touch-manipulation"
                >
                  {prevChapterLabel ?? (lang === "en" ? "← Previous episode" : "← 返回上一章")}
                </Link>
              )}
              {!isPlaying ? (
                <button
                  type="button"
                  onClick={startPlay}
                  className="inline-flex items-center gap-2 rounded-lg bg-podcast/20 text-podcast px-3 py-2.5 sm:px-4 py-2 text-sm font-medium hover:bg-podcast/30 transition-colors min-h-[44px] sm:min-h-0 touch-manipulation"
                >
                  <span className="text-lg" aria-hidden>▶</span>
                  {t.play}
                </button>
              ) : (
                <button
                  type="button"
                  onClick={stopPlay}
                  className="inline-flex items-center gap-2 rounded-lg bg-surface border border-border text-zinc-300 px-3 py-2.5 sm:px-4 py-2 text-sm font-medium hover:bg-surface/80 transition-colors min-h-[44px] sm:min-h-0 touch-manipulation"
                >
                  <span className="text-lg" aria-hidden>⏸</span>
                  {t.pause}
                </button>
              )}
              {isPlaying && (
                <span className="text-muted text-xs tabular-nums">
                  {t.playing} {currentPlayIndex + 1} / {messages.length}
                </span>
              )}
            </div>
            {nextChapterHref != null && (
              <Link
                href={nextChapterHref}
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-podcast/20 text-podcast px-3 py-2.5 sm:px-4 py-2 text-sm font-medium hover:bg-podcast/30 transition-colors flex-shrink-0 min-h-[44px] sm:min-h-0 touch-manipulation"
              >
                {nextChapterLabel ?? (lang === "en" ? "Next episode →" : "进入下一章 →")}
              </Link>
            )}
          </div>
          {/* 可点击进度条：与当前条同步 */}
          {messages.length > 0 && (
            <div className="px-3 sm:px-4 pb-3">
              <div
                ref={progressRef}
                role="slider"
                aria-label={lang === "en" ? "Playback position" : "播放进度"}
                aria-valuenow={currentPlayIndex + 1}
                aria-valuemin={1}
                aria-valuemax={messages.length}
                tabIndex={0}
                onClick={onProgressClick}
                className="h-2.5 sm:h-2 w-full max-w-2xl mx-auto rounded-full bg-surface border border-border cursor-pointer overflow-hidden flex items-center touch-manipulation"
              >
                <div
                  className="h-full bg-podcast/60 rounded-l-full transition-[width] duration-150"
                  style={{ width: `${((currentPlayIndex + 1) / messages.length) * 100}%` }}
                />
              </div>
            </div>
          )}
          <p className="px-3 sm:px-4 pb-2 text-center">
            <Link
              href={lang === "zh" ? "/support?lang=zh" : "/support"}
              className="text-muted text-xs hover:text-podcast transition-colors"
            >
              {lang === "zh" ? "喜欢的话，请我们喝杯咖啡 →" : "Enjoying the show? Support us →"}
            </Link>
          </p>
          </>
          )}
        </div>

        {/* 对话流：可滚动，点击某条跳转播放/暂停；滚动与进度条同步 */}
        <div className="flex-1 min-h-0">
          <div className="max-w-2xl mx-auto px-3 sm:px-4 py-6 sm:py-8 space-y-6 sm:space-y-8 pb-[env(safe-area-inset-bottom,0)]">
          {messages.map((msg, idx) => {
            if (activeRole !== null && msg.role_id !== activeRole) return null;
            const agent = agentMap[msg.role_id];
            if (!agent) return null;
            const isCurrent = isPlaying && idx === currentPlayIndex;
            return (
              <article
                key={idx}
                ref={(el) => { messageRefs.current[idx] = el; }}
                role="button"
                tabIndex={0}
                onClick={() => toggleAt(idx)}
                onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggleAt(idx); } }}
                className={`group flex gap-3 sm:gap-4 transition-colors cursor-pointer rounded-lg sm:rounded-xl p-2 sm:p-0 -mx-2 sm:mx-0 touch-manipulation ${isCurrent ? "ring-2 ring-podcast/50 ring-offset-2 ring-offset-void bg-surface/60" : "hover:bg-surface/40 active:bg-surface/50"}`}
              >
                <div className="flex-shrink-0 pt-0.5">
                  <AgentAvatar
                    roleId={agent.id}
                    name={agent.name}
                    title={agent.title}
                    codeName={agent.code_name}
                    compact
                  />
                </div>
                <div className="flex-1 min-w-0 overflow-hidden">
                  <div className="flex items-baseline gap-2 flex-wrap">
                    <span className="font-medium text-white text-sm sm:text-base">{agent.name}</span>
                    <span className="text-muted text-[10px] sm:text-xs">{agent.code_name}</span>
                    <span className="text-podcast-muted text-[10px] sm:text-xs font-mono tabular-nums">{msg.timestamp}</span>
                    {isCurrent && <span className="text-podcast text-xs">{t.playing}</span>}
                  </div>
                  <div className="mt-1.5 sm:mt-2 space-y-2 text-zinc-300 leading-relaxed text-sm sm:text-base">
                    {msg.content_blocks.map((block, bi) => (
                      <MessageBlock key={bi} block={block} />
                    ))}
                  </div>
                </div>
              </article>
            );
          })}
          </div>
        </div>
      </div>
    </div>
  );
}
