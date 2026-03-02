"use client";

import { clsx } from "clsx";

const AGENT_COLORS: Record<string, string> = {
  alice: "border-orange-500/60 bg-orange-500/10",
  chenwei: "border-sky-400/60 bg-sky-400/10",
  oldtom: "border-violet-400/60 bg-violet-400/10",
  elena: "border-fuchsia-400/60 bg-fuchsia-400/10",
};

/** Fallback when codeName not provided (e.g. legacy callers) */
const AGENT_LABELS: Record<string, string> = {
  alice: "比特先知",
  chenwei: "守恒者",
  oldtom: "月壤老兵",
  elena: "星云诗人",
};

interface AgentAvatarProps {
  roleId: string;
  name: string;
  title: string;
  /** 代号，由 API 按 lang 返回中/英文；传入时优先使用，不传则用内置中文 fallback */
  codeName?: string;
  active?: boolean;
  compact?: boolean;
}

export function AgentAvatar({ roleId, name, title, codeName: codeNameProp, active, compact }: AgentAvatarProps) {
  const style = AGENT_COLORS[roleId] || "border-zinc-500 bg-zinc-500/10";
  const codeName = codeNameProp ?? AGENT_LABELS[roleId] ?? roleId;

  if (compact) {
    return (
      <div
        className={clsx(
          "flex items-center gap-1.5 rounded-md border px-1.5 py-1 transition-all",
          style,
          active && "ring-2 ring-accent ring-offset-2 ring-offset-void animate-pulse-soft"
        )}
      >
        <div className={clsx("h-6 w-6 rounded-full border border-current flex-shrink-0", style)} />
        <span className="text-[10px] font-mono text-zinc-300 truncate max-w-[88px] leading-tight">
          {codeName}
        </span>
      </div>
    );
  }

  return (
    <div
      className={clsx(
        "rounded-xl border p-3 text-center transition-all",
        style,
        active && "ring-2 ring-accent ring-offset-2 ring-offset-void shadow-lg shadow-accent/20"
      )}
    >
      <div className={clsx("mx-auto h-14 w-14 rounded-full border-2 border-current", style)} />
      <p className="mt-2 text-sm font-medium text-zinc-200 truncate">{name}</p>
      <p className="text-xs text-muted font-mono">{codeName}</p>
      <p className="text-xs text-muted truncate">{title}</p>
    </div>
  );
}
