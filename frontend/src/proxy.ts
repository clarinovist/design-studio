import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const AUTH_BYPASS_FOR_E2E = process.env.PLAYWRIGHT_AUTH_BYPASS === "true";

function rejectStaleServerAction(request: NextRequest): NextResponse | null {
  if (!request.headers.has("next-action")) {
    return null;
  }

  // Design Studio does not currently define Server Actions in the frontend source.
  // Requests that still carry `next-action` usually come from stale tabs or bots
  // probing an old build and otherwise spam Next.js with "Failed to find Server Action".
  return NextResponse.json(
    {
      error: "Stale client action. Please refresh the page and retry.",
    },
    {
      status: 409,
      headers: {
        "Cache-Control": "no-store",
      },
    }
  );
}

// Reuse the same authorization logic as the previous middleware but expose
// it as a `proxy` as recommended by Next.js newer releases.
const proxyHandler = withAuth(
  function proxy(request: NextRequest) {
    const staleActionResponse = rejectStaleServerAction(request);
    if (staleActionResponse) {
      return staleActionResponse;
    }

    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: ({ token }) => AUTH_BYPASS_FOR_E2E || !!token,
    },
  }
);

export const proxy = proxyHandler;

// Protect these routes (same matcher as before)
export const config = {
  matcher: [
    "/projects/:path*",
    "/start/:path*",
    "/design/:path*",
    "/create/:path*",
    "/edit/:path*",
    "/settings/:path*",
  ],
};
