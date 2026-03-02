import type { Metadata } from "next";
import "./globals.css";
import { AdScript } from "@/components/AdScript";

export const metadata: Metadata = {
  title: "AImoon | AI-powered story worlds",
  description: "Discover AI-powered stories. Camp Zero: 30 episodes on the Moon — sci-fi writer, physicist, engineer & computer scientist at Shackleton Base.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="bg-void text-zinc-200 antialiased">
      <body className="min-h-screen font-sans">
        {children}
        <AdScript />
      </body>
    </html>
  );
}
