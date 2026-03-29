import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "404 — Page Not Found | ECFiler",
  description:
    "The page you're looking for doesn't exist. Head back to ECFiler to continue filing on CM/ECF.",
};

export default function NotFound() {
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
          {/* 404 badge */}
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#1e3a5f]/10 rounded-2xl mb-6">
            <span className="text-[28px] font-bold text-[#1e3a5f]">404</span>
          </div>

          <h1 className="text-[28px] sm:text-[32px] font-bold tracking-tight text-[#0f1f35] mb-3">
            Page not found
          </h1>
          <p className="text-[15px] leading-relaxed text-[#525252] mb-8 max-w-sm mx-auto">
            The page you&apos;re looking for doesn&apos;t exist or has been
            moved. Let&apos;s get you back on track.
          </p>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/"
              className="w-full sm:w-auto px-6 py-2.5 border border-[#e8e5e0] text-[#525252] text-[14px] font-semibold rounded-lg hover:border-[#ccc8c0] hover:text-[#1a1a1a] transition"
            >
              Go Home
            </Link>
            <Link
              href="/file"
              className="w-full sm:w-auto px-6 py-2.5 bg-[#1e3a5f] text-white text-[14px] font-semibold rounded-lg hover:bg-[#162a47] transition shadow-sm"
            >
              Start Filing
            </Link>
          </div>
        </div>

        <p className="mt-6 text-[12px] text-[#8a8a8a]">
          If you think this is a mistake,{" "}
          <a
            href="mailto:support@ecfiler.com"
            className="text-[#1e3a5f] hover:text-[#162a47] transition underline underline-offset-2"
          >
            let us know
          </a>
          .
        </p>
      </div>
    </div>
  );
}
