"use client";

import { useEffect, useRef } from "react";
import Script from "next/script";

type AdFormat = "rectangle" | "banner" | "auto";
type AdProvider = "google" | "carbon" | "custom";

interface AdSlotProps {
  /** Which ad network to use. Default "google". Use "carbon" for Carbon Ads, "custom" for script URL. */
  provider?: AdProvider;
  /** Ad slot ID (Google only). Falls back to NEXT_PUBLIC_ADSENSE_SLOT. */
  slotId?: string;
  /** Format: rectangle (336x280), banner (728x90 or responsive), auto (responsive). Google only. */
  format?: AdFormat;
  /** Optional className for the wrapper */
  className?: string;
}

const clientId = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID?.trim();
const defaultSlotId = process.env.NEXT_PUBLIC_ADSENSE_SLOT?.trim();
const carbonServe = process.env.NEXT_PUBLIC_CARBON_SERVE?.trim();
const carbonPlacement = process.env.NEXT_PUBLIC_CARBON_PLACEMENT?.trim();
const customScriptUrl = process.env.NEXT_PUBLIC_ALT_AD_SCRIPT_URL?.trim();

function Placeholder({ format, className }: { format: AdFormat; className: string }) {
  const style: React.CSSProperties =
    format === "banner" ? { width: "100%", maxWidth: 728, height: 90 } : format === "rectangle" ? { width: 336, height: 280 } : { width: "100%", minHeight: 100 };
  return (
    <div className={`ad-slot-wrapper ${className}`}>
      <div
        className="rounded-lg border border-border/50 bg-surface/40 flex items-center justify-center text-muted text-xs"
        style={style}
        role="presentation"
        aria-hidden
      >
        Ad
      </div>
    </div>
  );
}

export function AdSlot({
  provider = "google",
  slotId = defaultSlotId,
  format = "rectangle",
  className = "",
}: AdSlotProps) {
  const googleRef = useRef<HTMLModElement>(null);

  useEffect(() => {
    if (provider !== "google" || !clientId || !slotId || !googleRef.current) return;
    try {
      const w = window as unknown as { adsbygoogle: unknown[] };
      w.adsbygoogle = w.adsbygoogle || [];
      w.adsbygoogle.push({});
    } catch {
      // ignore
    }
  }, [provider, slotId]);

  // Google AdSense
  if (provider === "google" && clientId && slotId) {
    const style: React.CSSProperties =
      format === "banner" ? { minWidth: "728px", minHeight: "90px" } : format === "rectangle" ? { minWidth: "336px", minHeight: "280px" } : { display: "block" };
    return (
      <div className={`ad-slot-wrapper ${className}`}>
        <ins
          ref={googleRef}
          className="adsbygoogle"
          style={style}
          data-ad-client={clientId}
          data-ad-slot={slotId}
          data-ad-format={format === "auto" ? "auto" : undefined}
          data-full-width-responsive={format === "auto" ? "true" : undefined}
        />
      </div>
    );
  }

  // Carbon Ads (developer-focused, privacy-friendly). Apply at carbonads.net
  if (provider === "carbon" && carbonServe && carbonPlacement) {
    const scriptSrc = `https://cdn.carbonads.com/carbon.js?serve=${encodeURIComponent(carbonServe)}&placement=${encodeURIComponent(carbonPlacement)}`;
    return (
      <div className={`ad-slot-wrapper ${className}`}>
        <div id="carbonads" className="min-h-[130px] rounded-lg border border-border/50 bg-surface/40 overflow-hidden" />
        <Script src={scriptSrc} id="_carbonads_js" strategy="lazyOnload" />
      </div>
    );
  }

  // Custom: load any ad script by URL (e.g. Ethical Ads, Media.net). Container id = alt-ad-slot for targeting.
  if (provider === "custom" && customScriptUrl) {
    return (
      <div className={`ad-slot-wrapper ${className}`}>
        <div id="alt-ad-slot" className="min-h-[100px] rounded-lg border border-border/50 bg-surface/40" />
        <Script src={customScriptUrl} strategy="lazyOnload" />
      </div>
    );
  }

  return <Placeholder format={format} className={className} />;
}
