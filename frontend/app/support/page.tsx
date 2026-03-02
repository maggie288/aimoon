"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { AdSlot } from "@/components/AdSlot";

const copy = {
  zh: {
    title: "支持我们",
    intro:
      "本站为独立开发项目，服务器与内容制作均有成本。若你喜欢四角色圆桌与月球生存故事，欢迎通过比特币或 TRON（TRX / USDT-TRC20）支持后续剧集与功能更新。感谢。",
    bitcoin: "比特币 (BTC)",
    bitcoinDesc: "可直接向以下地址转账 BTC，无需经过第三方平台。",
    tron: "TRON (TRX / USDT-TRC20)",
    tronDesc: "你的 TRON 钱包地址，支持者可直接转 TRX 或 USDT（TRC20）到此地址。",
    copyAddress: "复制地址",
    copied: "已复制",
    backToCamp: "← 返回首页",
  },
  en: {
    title: "Support us",
    intro:
      "This site is independently built. Hosting and content have real costs. If you enjoy the four-voice roundtable and the lunar survival story, you can support future episodes and updates with Bitcoin or TRON (TRX / USDT-TRC20). Thank you.",
    bitcoin: "Bitcoin (BTC)",
    bitcoinDesc: "Send BTC directly to the address below. No third-party platform.",
    tron: "TRON (TRX / USDT-TRC20)",
    tronDesc: "Your TRON wallet address. Supporters can send TRX or USDT (TRC20) to this address.",
    copyAddress: "Copy address",
    copied: "Copied",
    backToCamp: "← Back to home",
  },
};

function CopyableAddress({
  address,
  copyLabel,
  copiedLabel,
}: {
  address: string;
  copyLabel: string;
  copiedLabel: string;
}) {
  const [copied, setCopied] = useState(false);
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(address);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback: select and hope user copies
      const el = document.createElement("input");
      el.value = address;
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };
  return (
    <div className="flex flex-wrap items-center gap-2">
      <code className="flex-1 min-w-0 text-xs sm:text-sm text-podcast-muted bg-surface/80 border border-border rounded-lg px-3 py-2 break-all font-mono">
        {address}
      </code>
      <button
        type="button"
        onClick={handleCopy}
        className="flex-shrink-0 rounded-lg bg-podcast/20 text-podcast px-4 py-2 text-sm font-medium hover:bg-podcast/30 transition-colors"
      >
        {copied ? copiedLabel : copyLabel}
      </button>
    </div>
  );
}

function SupportPageContent() {
  const searchParams = useSearchParams();
  const lang = searchParams.get("lang") === "zh" ? "zh" : "en";
  const t = copy[lang];
  const href = (path: string) =>
    path + (lang === "zh" ? "?lang=zh" : "");
  const btcAddress = process.env.NEXT_PUBLIC_BTC_ADDRESS?.trim() || "";
  const tronAddress = process.env.NEXT_PUBLIC_TRON_ADDRESS?.trim() || "";

  return (
    <div className="min-h-screen bg-void text-zinc-200">
      <header className="border-b border-border/50 bg-void/95 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link
            href={href("/")}
            className="text-muted text-sm hover:text-white transition-colors"
          >
            {t.backToCamp}
          </Link>
          <Link
            href={lang === "en" ? "/support?lang=zh" : "/support"}
            className="text-podcast text-xs font-medium hover:underline"
          >
            {lang === "en" ? "中文" : "EN"}
          </Link>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-12">
        <h1 className="text-2xl font-semibold text-white tracking-tight mb-8">
          {t.title}
        </h1>
        <aside className="mb-8 flex justify-center">
          <AdSlot provider="carbon" format="rectangle" />
        </aside>
        <p className="text-zinc-300 leading-relaxed mb-10">{t.intro}</p>

        {btcAddress ? (
          <section>
            <h2 className="text-sm font-medium text-white mb-1">{t.bitcoin}</h2>
            <p className="text-muted text-sm mb-4">{t.bitcoinDesc}</p>
            <div className="flex flex-col sm:flex-row gap-6 items-start">
              <div className="flex-shrink-0 w-44 h-44 rounded-xl bg-white p-2">
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=168x168&data=${encodeURIComponent("bitcoin:" + btcAddress)}`}
                  alt="Bitcoin QR"
                  width={168}
                  height={168}
                  className="w-full h-full"
                />
              </div>
              <div className="flex-1 min-w-0 w-full">
                <CopyableAddress address={btcAddress} copyLabel={t.copyAddress} copiedLabel={t.copied} />
              </div>
            </div>
          </section>
        ) : null}

        {tronAddress ? (
          <section className={btcAddress ? "mt-10 pt-8 border-t border-border/50" : ""}>
            <h2 className="text-sm font-medium text-white mb-1">{t.tron}</h2>
            <p className="text-muted text-sm mb-4">{t.tronDesc}</p>
            <div className="flex flex-col sm:flex-row gap-6 items-start">
              <div className="flex-shrink-0 w-44 h-44 rounded-xl bg-white p-2">
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=168x168&data=${encodeURIComponent(tronAddress)}`}
                  alt="TRON address QR"
                  width={168}
                  height={168}
                  className="w-full h-full"
                />
              </div>
              <div className="flex-1 min-w-0 w-full">
                <CopyableAddress address={tronAddress} copyLabel={t.copyAddress} copiedLabel={t.copied} />
              </div>
            </div>
          </section>
        ) : null}
      </main>
    </div>
  );
}

export default function SupportPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-void text-zinc-200 flex items-center justify-center"><span className="text-muted">Loading…</span></div>}>
      <SupportPageContent />
    </Suspense>
  );
}
