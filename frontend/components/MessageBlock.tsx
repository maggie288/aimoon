"use client";

import { useEffect, useRef, useState } from "react";

interface Block {
  type: string;
  content?: string;
  media_id?: string;
  description?: string;
}

function MathBlock({ content }: { content: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (typeof window === "undefined" || !content) return;
    import("katex").then((katex) => {
      if (!ref.current) return;
      try {
        katex.default.render(content, ref.current, {
          throwOnError: false,
          displayMode: true,
          output: "html",
        });
      } catch (_) {}
    });
  }, [content]);
  return <div ref={ref} className="my-2 overflow-x-auto" />;
}

function MermaidBlock({ content }: { content: string }) {
  const [svg, setSvg] = useState<string>("");
  const [err, setErr] = useState(false);

  useEffect(() => {
    if (!content || typeof window === "undefined") return;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    import("mermaid").then((mod: any) => {
      const m = mod?.default ?? mod;
      if (!m?.render) {
        setErr(true);
        return;
      }
      m.initialize?.({ startOnLoad: false, theme: "dark", securityLevel: "loose" });
      const id = "mermaid-" + Math.random().toString(36).slice(2);
      m.render(id, content).then((r: { svg: string }) => setSvg(r.svg)).catch(() => setErr(true));
    });
  }, [content]);

  if (err) return <pre className="text-xs text-muted overflow-x-auto p-2 rounded bg-surface">{content}</pre>;
  if (!svg) return <div className="rounded-lg bg-surface border border-border p-4 animate-pulse h-32" />;
  return <div className="my-2 rounded-lg bg-surface border border-border p-4 overflow-x-auto" dangerouslySetInnerHTML={{ __html: svg }} />;
}

export function MessageBlock({ block }: { block: Block }) {
  if (block.type === "paragraph") {
    return (
      <p className="text-zinc-300 leading-relaxed whitespace-pre-wrap">
        {block.content}
      </p>
    );
  }
  if (block.type === "math" && block.content) {
    return <MathBlock content={block.content} />;
  }
  if (block.type === "mermaid" && block.content) {
    return <MermaidBlock content={block.content} />;
  }
  if (block.type === "code" && block.content) {
    return (
      <pre className="my-2 rounded-lg bg-surface border border-border p-4 overflow-x-auto text-sm font-mono text-zinc-300">
        <code>{block.content}</code>
      </pre>
    );
  }
  if (block.type === "image") {
    const mediaId = block.media_id || "img";
    const label = block.description || mediaId;
    const src = `/api/media/image/${mediaId}?label=${encodeURIComponent(label.slice(0, 100))}`;
    return (
      <figure className="my-3 rounded-lg border border-border bg-surface overflow-hidden">
        <img
          src={src}
          alt={label}
          className="w-full aspect-video object-contain bg-surface border-b border-border"
        />
        {block.description && (
          <figcaption className="text-xs text-muted p-2">{block.description}</figcaption>
        )}
      </figure>
    );
  }
  if (block.type === "video") {
    const mediaId = block.media_id || "vid";
    const label = block.description || mediaId;
    const src = `/api/media/image/${mediaId}?label=${encodeURIComponent(label.slice(0, 100))}`;
    return (
      <figure className="my-3 rounded-lg border border-border bg-surface overflow-hidden">
        <img
          src={src}
          alt={label}
          className="w-full aspect-video object-contain bg-surface border-b border-border"
        />
        {block.description && (
          <figcaption className="text-xs text-muted p-2">{block.description}</figcaption>
        )}
      </figure>
    );
  }
  return null;
}
