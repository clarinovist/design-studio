import { NextRequest, NextResponse } from 'next/server';

const FETCH_TIMEOUT_MS = 10_000;
const MAX_ATTEMPTS = 2;
const ALLOWED_PROTOCOLS = new Set(['http:', 'https:']);

function redactUrl(rawUrl: string): string {
    try {
        const parsed = new URL(rawUrl);
        parsed.searchParams.delete('token');
        parsed.searchParams.delete('signature');
        parsed.searchParams.delete('X-Amz-Signature');
        return parsed.toString();
    } catch {
        return rawUrl.slice(0, 200);
    }
}

function validateImageUrl(rawUrl: string): URL {
    const parsed = new URL(rawUrl);

    if (!ALLOWED_PROTOCOLS.has(parsed.protocol)) {
        throw new Error(`Unsupported image URL protocol: ${parsed.protocol}`);
    }

    return parsed;
}

async function fetchImage(url: string): Promise<Response> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

        try {
            const response = await fetch(url, {
                signal: controller.signal,
                headers: {
                    // Some CDNs reject default runtime fetches or vary behavior without a UA.
                    'User-Agent': 'SmartDesignStudio/1.0 image-proxy',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                },
                cache: 'no-store',
                redirect: 'follow',
            });

            if (response.ok) {
                return response;
            }

            lastError = new Error(
                `Failed to fetch image: HTTP ${response.status} ${response.statusText || '(no status text)'} from ${redactUrl(url)}`
            );

            // Retry only transient upstream failures.
            if (response.status < 500 && response.status !== 429) {
                break;
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            const name = error instanceof Error ? error.name : 'UnknownError';
            lastError = new Error(`Failed to fetch image: ${name}: ${message} from ${redactUrl(url)}`);
        } finally {
            clearTimeout(timeout);
        }
    }

    throw lastError ?? new Error(`Failed to fetch image from ${redactUrl(url)}`);
}

export async function GET(request: NextRequest) {
    const url = request.nextUrl.searchParams.get('url');

    if (!url) {
        return NextResponse.json({ error: 'URL is required' }, { status: 400 });
    }

    let parsedUrl: URL;
    try {
        parsedUrl = validateImageUrl(url);
    } catch (error) {
        const message = error instanceof Error ? error.message : 'Invalid image URL';
        console.warn('Image proxy rejected URL:', message, redactUrl(url));
        return NextResponse.json({ error: 'Invalid image URL' }, { status: 400 });
    }

    // Generate ETag based on the canonical URL (deterministic, no need to fetch first)
    const urlHash = Buffer.from(parsedUrl.toString()).toString('base64url').slice(0, 16);
    const serverETag = `"${urlHash}"`;

    // Handle conditional requests BEFORE fetching upstream — this is the fast path
    const clientETag = request.headers.get('If-None-Match');
    if (clientETag === serverETag) {
        return new NextResponse(null, {
            status: 304,
            headers: {
                'ETag': serverETag,
                'Cache-Control': 'public, max-age=86400',
                'Access-Control-Allow-Origin': '*',
                'Vary': 'Origin',
            },
        });
    }

    try {
        const response = await fetchImage(parsedUrl.toString());
        const buffer = await response.arrayBuffer();
        const headers = new Headers();

        // Pass through the content type
        const contentType = response.headers.get('content-type');
        if (contentType) {
            headers.set('Content-Type', contentType);
        }

        // Add CORS headers to allow canvas export
        headers.set('Access-Control-Allow-Origin', '*');
        headers.set('Cache-Control', 'public, max-age=86400');
        headers.set('Vary', 'Origin');
        headers.set('ETag', serverETag);

        return new NextResponse(buffer, {
            status: 200,
            headers,
        });
    } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        console.error('Image proxy error:', message);
        return NextResponse.json({ error: 'Failed to proxy image' }, { status: 502 });
    }
}
