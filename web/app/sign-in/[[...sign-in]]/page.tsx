import { SignIn } from "@clerk/nextjs";
import Link from "next/link";

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f5f3ee] px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2.5 mb-4">
            <div className="w-9 h-9 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-xl flex items-center justify-center text-white text-[13px] font-bold shadow-lg shadow-[#1e3a5f]/20">E</div>
            <span className="text-[18px] font-semibold tracking-tight text-[#1a1a1a]">ECFiler</span>
          </Link>
          <p className="text-[13px] text-[#8a8a8a]">Sign in to your filing workspace</p>
        </div>
        <SignIn
          fallbackRedirectUrl="/file"
          appearance={{
            elements: {
              rootBox: "mx-auto w-full",
              card: "shadow-xl shadow-black/5 border border-[#e8e5e0] rounded-2xl bg-white",
              headerTitle: "text-[#1a1a1a]",
              headerSubtitle: "text-[#8a8a8a]",
              formButtonPrimary: "bg-[#1e3a5f] hover:bg-[#162a47] shadow-sm",
              footerActionLink: "text-[#1e3a5f] hover:text-[#162a47]",
            },
          }}
        />
        <div className="text-center mt-6">
          <Link href="/" className="text-[12px] text-[#8a8a8a] hover:text-[#525252] transition">&larr; Back to ECFiler</Link>
        </div>
      </div>
    </div>
  );
}
