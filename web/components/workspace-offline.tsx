import Link from "next/link";
import { WORKSPACE_OFFLINE_NOTE } from "@/lib/workspace";

/**
 * Shown in place of every signed-in workspace page, and in place of the
 * sign-up form, while the site is built without a backend
 * (web/lib/workspace.ts). Plain statement, links to what does work.
 */
export function WorkspaceOffline({ signedIn }: { signedIn: boolean }) {
  return (
    <div className="min-h-screen bg-[#f5f3ee] flex items-center justify-center px-4 py-16">
      <div data-testid="workspace-offline" className="w-full max-w-lg bg-white border border-[#e8e5e0] rounded-2xl p-8 shadow-sm">
        <Link href="/" className="inline-flex items-center gap-2.5 mb-6">
          <div className="w-8 h-8 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[12px] font-bold">E</div>
          <span className="text-[16px] font-semibold tracking-tight text-[#1a1a1a]">ECFiler</span>
        </Link>
        <h1 className="text-[22px] font-bold tracking-tight text-[#1a1a1a] mb-3">The filing workspace is not open yet</h1>
        <p className="text-[14px] leading-relaxed text-[#525252] mb-4">{WORKSPACE_OFFLINE_NOTE}</p>
        <p className="text-[14px] leading-relaxed text-[#525252] mb-6">
          {signedIn
            ? "Your account is safe and nothing has been lost. ECFiler keeps no documents or filing history for you while the workspace is closed."
            : "New accounts open when the workspace does. Join the waitlist to hear first."}
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <Link href="/tools" className="px-5 py-2.5 bg-[#1e3a5f] text-white text-[14px] font-semibold rounded-xl hover:bg-[#162a47] transition text-center">Use the free tools</Link>
          <Link href="/#pricing" className="px-5 py-2.5 bg-white text-[#1e3a5f] text-[14px] font-semibold rounded-xl border-2 border-[#e8e5e0] hover:border-[#1e3a5f] transition text-center">Join the waitlist</Link>
        </div>
      </div>
    </div>
  );
}
