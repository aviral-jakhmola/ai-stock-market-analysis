import { http, HttpResponse } from "msw";

const BASE = "http://127.0.0.1:8000";

export const handlers = [
  http.post(`${BASE}/api/auth/register`, async () => {
    return HttpResponse.json({ id: 1, username: "testuser", email: "test@example.com" });
  }),

  http.post(`${BASE}/api/auth/login`, async ({ request }) => {
    // Sanity-check it's actually form-encoded, not JSON
    const contentType = request.headers.get("content-type") || "";
    if (!contentType.includes("application/x-www-form-urlencoded")) {
      return HttpResponse.json({ detail: "Expected form-encoded body" }, { status: 422 });
    }
    return HttpResponse.json({ access_token: "fake-jwt-token", token_type: "bearer" });
  }),

  http.get(`${BASE}/api/auth/me`, ({ request }) => {
    const auth = request.headers.get("authorization");
    if (!auth || !auth.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Not authenticated" }, { status: 401 });
    }
    return HttpResponse.json({ id: 1, username: "testuser", email: "test@example.com" });
  }),

  http.get(`${BASE}/api/watchlist`, () => HttpResponse.json([])),
  http.post(`${BASE}/api/watchlist`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: 1, ticker: body.ticker });
  }),
  http.delete(`${BASE}/api/watchlist/:itemId`, () => new HttpResponse(null, { status: 204 })),

  http.get(`${BASE}/api/search-history`, () => HttpResponse.json([])),

  http.get(`${BASE}/api/stocks/company/:ticker`, ({ params }) => {
    return HttpResponse.json({ ticker: params.ticker, name: "Test Company" });
  }),

  http.get(`${BASE}/api/stocks/:ticker/sentiment`, () => {
    return HttpResponse.json({ overall_sentiment: "neutral", articles: [] });
  }),
];