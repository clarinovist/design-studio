import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json(
    {
      buildId: process.env.NEXT_PUBLIC_BUILD_ID || "dev",
      status: "ok",
      timestamp: new Date().toISOString(),
    },
    {
      status: 200,
      headers: {
        "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate",
        Pragma: "no-cache",
        Expires: "0",
      },
    }
  );
}
