import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "ECFiler — AI-Powered Federal Court Filing";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          background: "linear-gradient(135deg, #0f1f35 0%, #1e3a5f 50%, #0f2440 100%)",
          fontFamily: "system-ui, -apple-system, sans-serif",
        }}
      >
        {/* Logo */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "20px",
            marginBottom: "40px",
          }}
        >
          <div
            style={{
              width: "64px",
              height: "64px",
              background: "linear-gradient(135deg, #2a5080, #1e3a5f)",
              borderRadius: "16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontSize: "32px",
              fontWeight: 700,
              border: "2px solid rgba(255,255,255,0.15)",
            }}
          >
            E
          </div>
          <div style={{ color: "white", fontSize: "48px", fontWeight: 700, letterSpacing: "-0.03em" }}>
            ECFiler
          </div>
        </div>

        {/* Headline */}
        <div
          style={{
            color: "white",
            fontSize: "36px",
            fontWeight: 600,
            textAlign: "center",
            lineHeight: 1.3,
            maxWidth: "800px",
            marginBottom: "24px",
          }}
        >
          The intelligent way to file on CM/ECF
        </div>

        {/* Subline */}
        <div
          style={{
            color: "rgba(255,255,255,0.5)",
            fontSize: "20px",
            textAlign: "center",
            maxWidth: "600px",
            marginBottom: "40px",
          }}
        >
          Drop a PDF. AI extracts everything. File with one click.
        </div>

        {/* Stats */}
        <div style={{ display: "flex", gap: "40px" }}>
          {[
            { n: "207", label: "Federal Courts" },
            { n: "7", label: "Safety Gates" },
            { n: "<1m", label: "To Prepare" },
          ].map((s) => (
            <div
              key={s.label}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                padding: "16px 32px",
                background: "rgba(255,255,255,0.08)",
                borderRadius: "12px",
                border: "1px solid rgba(255,255,255,0.1)",
              }}
            >
              <div style={{ color: "white", fontSize: "28px", fontWeight: 700 }}>{s.n}</div>
              <div style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px", fontWeight: 500 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* URL */}
        <div
          style={{
            position: "absolute",
            bottom: "30px",
            color: "rgba(255,255,255,0.25)",
            fontSize: "16px",
            fontWeight: 500,
          }}
        >
          ecfiler.com
        </div>
      </div>
    ),
    { ...size },
  );
}
