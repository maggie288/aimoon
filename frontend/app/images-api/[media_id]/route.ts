import { NextRequest, NextResponse } from "next/server";
import path from "path";
import fs from "fs";

const MANIFEST_PATH = path.join(process.cwd(), "public", "images", "manifest.json");

export function GET(
  _request: NextRequest,
  { params }: { params: { media_id: string } }
) {
  const mediaId = (params?.media_id || "").replace(/[^a-z0-9-_]/gi, "");
  if (!mediaId) {
    return NextResponse.redirect(new URL("/images/placeholder.svg", _request.url));
  }
  try {
    const raw = fs.readFileSync(MANIFEST_PATH, "utf-8");
    const manifest: Record<string, string> = JSON.parse(raw);
    const filename = manifest[mediaId];
    if (filename) {
      return NextResponse.redirect(new URL(`/images/${filename}`, _request.url));
    }
  } catch {
    // manifest missing or invalid
  }
  return NextResponse.redirect(new URL("/images/placeholder.svg", _request.url));
}
