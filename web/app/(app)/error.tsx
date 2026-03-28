"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("App error boundary caught:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-[#f5f3ee] flex items-center justify-center px-6">
      <div className="max-w-md w-full bg-white border border-[#e8e5e0] rounded-2xl p-8 shadow-sm text-center">
        {/* Icon */}
        <div className="w-14 h-14 mx-auto mb-5 bg-[#fef2f2] rounded-2xl flex items-center justify-center">
          <svg
            className="w-7 h-7 text-[#dc2626]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
        </div>

        {/* Heading */}
        <h1 className="text-xl font-bold text-[#1a1a1a] mb-2">
          Something went wrong
        </h1>
        <p className="text-[14px] text-[#525252] leading-relaxed mb-6">
          An unexpected error occurred. You can try again or head back to the
          filing workspace.
        </p>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-6">
          <button
            onClick={reset}
            className="w-full sm:w-auto px-6 py-2.5 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] active:scale-[0.98] transition-all shadow-sm hover:shadow-md"
          >
            Try again
          </button>
          <Link
            href="/file"
            className="w-full sm:w-auto px-6 py-2.5 border border-[#e8e5e0] text-sm font-semibold text-[#525252] rounded-xl hover:bg-[#f5f3ee] hover:border-[#d4d0ca] active:scale-[0.98] transition-all text-center"
          >
            Go to Filing
          </Link>
        </div>

        {/* Collapsible error details */}
        <details className="text-left bg-[#fafaf9] border border-[#e8e5e0] rounded-xl overflow-hidden">
          <summary className="px-4 py-3 text-[12px] font-semibold text-[#8a8a8a] uppercase tracking-wide cursor-pointer hover:bg-[#f5f3ee] transition-colors select-none">
            Error details
          </summary>
          <div className="px-4 pb-4 pt-1">
            <p className="text-[13px] text-[#525252] font-mono break-all whitespace-pre-wrap leading-relaxed">
              {error.message || "Unknown error"}
            </p>
            {error.digest && (
              <p className="text-[11px] text-[#8a8a8a] mt-2">
                Digest: {error.digest}
              </p>
            )}
          </div>
        </details>
      </div>
    </div>
  );
}
