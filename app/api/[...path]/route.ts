import { NextRequest } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

async function proxyRequest(request: NextRequest) {
  const backendUrl = process.env.BACKEND_API_URL?.replace(/\/+$/, '');
  const apiKey = process.env.BACKEND_API_KEY;

  if (!backendUrl || !apiKey) {
    return Response.json(
      { error: 'Backend proxy is not configured on the server.' },
      { status: 503 }
    );
  }

  const path = request.nextUrl.pathname;

  // Only allow the application's versioned REST API.
  if (!path.startsWith('/api/v1/')) {
    return Response.json({ error: 'Route not allowed' }, { status: 404 });
  }

  const upstreamUrl = `${backendUrl}${path}${request.nextUrl.search}`;

  const headers = new Headers();
  headers.set('X-API-Key', apiKey);

  const contentType = request.headers.get('content-type');
  const accept = request.headers.get('accept');

  if (contentType) headers.set('Content-Type', contentType);
  if (accept) headers.set('Accept', accept);

  try {
    const method = request.method;
    const body =
      method === 'GET' || method === 'HEAD'
        ? undefined
        : await request.arrayBuffer();

    const upstreamResponse = await fetch(upstreamUrl, {
      method,
      headers,
      body,
      cache: 'no-store',
      redirect: 'manual',
    });

    const responseHeaders = new Headers();
    const responseContentType = upstreamResponse.headers.get('content-type');
    const contentDisposition = upstreamResponse.headers.get('content-disposition');

    if (responseContentType) {
      responseHeaders.set('Content-Type', responseContentType);
    }

    if (contentDisposition) {
      responseHeaders.set('Content-Disposition', contentDisposition);
    }

    responseHeaders.set('Cache-Control', 'no-store');

    if (method === 'HEAD' || upstreamResponse.status === 204) {
      return new Response(null, {
        status: upstreamResponse.status,
        headers: responseHeaders,
      });
    }

    return new Response(upstreamResponse.body, {
      status: upstreamResponse.status,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('Backend proxy error:', error);

    return Response.json(
      { error: 'Unable to reach the backend service.' },
      { status: 502 }
    );
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PUT = proxyRequest;
export const PATCH = proxyRequest;
export const DELETE = proxyRequest;
export const HEAD = proxyRequest;
