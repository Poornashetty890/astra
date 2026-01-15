def add_additional_headers(resp, request):
    resp.headers.__setitem__(
        "Access-Control-Allow-Origin", request.headers.get("origin", "*")
    )
    resp.headers.__setitem__(
        "Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, OPTIONS"
    )
    resp.headers.__setitem__(
        "Access-Control-Allow-Headers",
        "Content-Type, Authorization, Access-Control-Allow-Headers, X-Requested-With, x-client-utc-offset, DNT, User-Agent, If-Modified-Since, Cache-Control, Range, traceparent, tracestate, x-highlight-request",
    )
    resp.headers.__setitem__("Access-Control-Max-Age", "86400")
    resp.headers.__setitem__("Access-Control-Allow-Credentials", "true")
    resp.headers.__setitem__("X-Content-Type-Options", "nosniff")
    resp.headers.__setitem__(
        "Content-Security-Policy",
        "default-src 'self' http://*localhost:8000 https://effulgent-medovik-b2dacc.netlify.app",
    )
    resp.headers.__setitem__("X-Download-Options", "noopen")
    resp.headers.__setitem__(
        "Strict-Transport-Security", "max-age=15552000; includeSubDomains"
    )
    resp.headers.__setitem__("X-Frame-Options", "SAMEORIGIN")
    resp.headers.__setitem__("X-DNS-Prefetch-Control", "off")
    resp.headers.__setitem__("Pragma", "no-cache")
    resp.headers.__setitem__("X-Forwarded-Proto", "https")
    return resp
