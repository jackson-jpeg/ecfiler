"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    console.error("[ECFiler] Unhandled error:", error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#fafaf8] px-4">
      {/* Subtle background grid */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e3a5f06_1px,transparent_1px),linear-gradient(to_bottom,#1e3a5f06_1px,transparent_1px)] bg-[size:64px_64px]" />
      </div>

      <div className="relative w-full max-w-lg text-center">
        {/* Logo */}
        <Link href="/" className="inline-flex items-center gap-2.5 mb-10">
          <div className="w-9 h-9 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-xl flex items-center justify-center text-white text-[13px] font-bold shadow-lg shadow-[#1e3a5f]/20">
            E
          </div>
          <span className="text-[18px] font-semibold tracking-tight text-[#1a1a1a]">
            ECFiler
          </span>
        </Link>

        {/* Card */}
        <div className="bg-white border border-[#e8e5e0] rounded-2xl shadow-xl shadow-black/5 px-8 py-12 sm:px-12">
          {/* Error icon */}
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-50 rounded-2xl mb-6">
            <svg
              className="w-8 h-8 text-red-500"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
              />
            </svg>
          </div>

          <h1 className="text-[28px] sm:text-[32px] font-bold tracking-tight text-[#0f1f35] mb-3">
            Something went wrong
          </h1>
          <p className="text-[15px] leading-relaxed text-[#525252] mb-8 max-w-sm mx-auto">
            An unexpected error occurred. You can try again or head back to the
            home page.
          </p>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/"
              className="w-full sm:w-auto px-6 py-2.5 border border-[#e8e5e0] text-[#525252] text-[14px] font-semibold rounded-lg hover:border-[#ccc8c0] hover:text-[#1a1a1a] transition"
            >
              Go Home
            </Link>
            <button
              onClick={reset}
              className="w-full sm:w-auto px-6 py-2.5 bg-[#1e3a5f] text-white text-[14px] font-semibold rounded-lg hover:bg-[#162a47] transition shadow-sm cursor-pointer"
            >
              Try Again
            </button>
          </div>

          {/* Collapsible error details */}
          <div className="mt-8 border-t border-[#e8e5e0] pt-6">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-[13px] text-[#8a8a8a] hover:text-[#525252] transition cursor-pointer inline-flex items-center gap-1.5"
            >
              <svg
                className={`w-3.5 h-3.5 transition-transform ${showDetails ? "rotate-90" : ""}`}
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M8.25 4.5l7.5 7.5-7.5 7.5"
                />
              </svg>
              Error details
            </button>

            {showDetails && (
              <div className="mt-3 text-left bg-[#fafaf8] border border-[#e8e5e0] rounded-xl p-4 overflow-auto max-h-48">
                <p className="text-[13px] font-medium text-[#1a1a1a] mb-1">
                  {error.name}: {error.message}
                </p>
                {error.digest && (
                  <p className="text-[12px] text-[#8a8a8a] mb-2">
                    Digest: {error.digest}
                  </p>
                )}
                {error.stack && (
                  <pre className="text-[11px] leading-relaxed text-[#8a8a8a] whitespace-pre-wrap font-[JetBrains_Mono,monospace] break-words">
                    {error.stack}
                  </pre>
                )}
              </div>
            )}
          </div>
        </div>

        <p className="mt-6 text-[12px] text-[#8a8a8a]">
          If this keeps happening,{" "}
          <a
            href="mailto:support@ecfiler.com"
            className="text-[#1e3a5f] hover:text-[#162a47] transition underline underline-offset-2"
          >
            contact support
          </a>
          .
        </p>
      </div>
    </div>
  );
}
