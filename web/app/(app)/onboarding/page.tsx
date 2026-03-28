"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type OnboardingStep = "welcome" | "role" | "court" | "pacer" | "done";

const STEPS: OnboardingStep[] = ["welcome", "role", "court", "pacer", "done"];

/* Step icons as inline SVGs */
function RoleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
    </svg>
  );
}

function CourtIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" />
    </svg>
  );
}

function PacerIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
    </svg>
  );
}

export default function OnboardingPage() {
  const [step, setStep] = useState<OnboardingStep>("welcome");
  const [role, setRole] = useState("");
  const [court, setCourt] = useState("");
  const [firmName, setFirmName] = useState("");
  const [barNumber, setBarNumber] = useState("");
  const router = useRouter();

  const finish = () => {
    // Save to localStorage for now (Clerk user metadata later)
    localStorage.setItem("ecfiler_onboarded", "true");
    localStorage.setItem("ecfiler_role", role);
    localStorage.setItem("ecfiler_court", court);
    localStorage.setItem("ecfiler_firm", firmName);
    localStorage.setItem("ecfiler_bar", barNumber);
    router.push("/file");
  };

  const skip = () => {
    const idx = STEPS.indexOf(step);
    if (idx < STEPS.length - 1) setStep(STEPS[idx + 1]);
  };

  const currentIdx = STEPS.indexOf(step);

  return (
    <div className="relative flex items-center justify-center min-h-screen p-8 bg-[#f5f3ee] overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%231e3a5f' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      }} />

      {/* Subtle radial gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-white/40 via-transparent to-[#1e3a5f]/[0.02]" />

      <div className="relative max-w-md w-full">
        {/* Card container */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-sm border border-[#e8e5e0]/60 p-8">

          {/* Progress dots */}
          <div className="flex justify-center gap-2.5 mb-10">
            {STEPS.map((s, i) => (
              <div
                key={s}
                className={`h-2.5 rounded-full transition-all duration-300 ${
                  i <= currentIdx
                    ? "bg-gradient-to-r from-[#1e3a5f] to-[#2a5080] w-8"
                    : "bg-[#e8e5e0] w-2.5"
                }`}
              />
            ))}
          </div>

          {/* Welcome */}
          {step === "welcome" && (
            <div className="text-center animate-in fade-in">
              <div className="w-20 h-20 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-2xl flex items-center justify-center text-white text-2xl font-bold mx-auto mb-6 shadow-lg shadow-[#1e3a5f]/20">
                E
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-[#1a1a1a] mb-3">Welcome to ECFiler</h1>
              <p className="text-[#525252] mb-8 leading-relaxed">
                AI-powered filing for federal courts. Let&apos;s get you set up in 30 seconds.
              </p>
              <button
                onClick={() => setStep("role")}
                className="px-8 py-3.5 bg-gradient-to-r from-[#1e3a5f] to-[#2a5080] text-white text-sm font-semibold rounded-xl hover:from-[#162a47] hover:to-[#1e3a5f] transition-all shadow-md shadow-[#1e3a5f]/15 w-full"
              >
                Get Started
              </button>
            </div>
          )}

          {/* Role */}
          {step === "role" && (
            <div className="animate-in fade-in">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-9 h-9 rounded-xl bg-[#1e3a5f]/[0.08] flex items-center justify-center">
                  <RoleIcon className="w-5 h-5 text-[#1e3a5f]" />
                </div>
                <h2 className="text-xl font-bold tracking-tight text-[#1a1a1a]">What&apos;s your role?</h2>
              </div>
              <p className="text-[#525252] text-sm mb-6 ml-12">This helps us customize your experience.</p>
              <div className="space-y-2 mb-8">
                {[
                  { id: "attorney", label: "Attorney", desc: "I file documents on CM/ECF" },
                  { id: "paralegal", label: "Paralegal / Legal Assistant", desc: "I prepare filings for attorneys" },
                  { id: "solo", label: "Solo Practitioner", desc: "I do everything myself" },
                  { id: "firm_admin", label: "Firm Administrator", desc: "I manage filing for the firm" },
                ].map((r) => (
                  <button
                    key={r.id}
                    onClick={() => setRole(r.id)}
                    className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                      role === r.id
                        ? "border-[#1e3a5f] bg-[#1e3a5f]/[0.04] shadow-sm"
                        : "border-[#e8e5e0] hover:border-[#c8c4be] hover:bg-[#fafaf8]"
                    }`}
                  >
                    <div className="text-sm font-semibold text-[#1a1a1a]">{r.label}</div>
                    <div className="text-xs text-[#525252] mt-0.5">{r.desc}</div>
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-3">
                <button onClick={() => setStep("welcome")} className="px-5 py-3 text-sm text-[#525252] hover:text-[#1a1a1a] transition">Back</button>
                <button
                  onClick={() => setStep("court")}
                  disabled={!role}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-[#1e3a5f] to-[#2a5080] text-white text-sm font-semibold rounded-xl hover:from-[#162a47] hover:to-[#1e3a5f] disabled:opacity-20 transition-all shadow-sm"
                >
                  Continue
                </button>
              </div>
              <div className="text-center mt-4">
                <button onClick={skip} className="text-xs text-[#8a8a8a] hover:text-[#525252] transition underline underline-offset-2">
                  Skip this step
                </button>
              </div>
            </div>
          )}

          {/* Court */}
          {step === "court" && (
            <div className="animate-in fade-in">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-9 h-9 rounded-xl bg-[#1e3a5f]/[0.08] flex items-center justify-center">
                  <CourtIcon className="w-5 h-5 text-[#1e3a5f]" />
                </div>
                <h2 className="text-xl font-bold tracking-tight text-[#1a1a1a]">Your primary court</h2>
              </div>
              <p className="text-[#525252] text-sm mb-6 ml-12">Which court do you file in most? You can change this later.</p>
              <div className="space-y-3 mb-6">
                <div>
                  <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Court</label>
                  <input
                    type="text"
                    value={court}
                    onChange={(e) => setCourt(e.target.value)}
                    placeholder="e.g., S.D.N.Y. or nysd"
                    className="w-full px-4 py-2.5 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10 bg-white transition"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Firm / Organization</label>
                  <input
                    type="text"
                    value={firmName}
                    onChange={(e) => setFirmName(e.target.value)}
                    placeholder="e.g., Smith & Associates LLP"
                    className="w-full px-4 py-2.5 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10 bg-white transition"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Bar Number (optional)</label>
                  <input
                    type="text"
                    value={barNumber}
                    onChange={(e) => setBarNumber(e.target.value)}
                    placeholder="e.g., NY12345"
                    className="w-full px-4 py-2.5 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10 bg-white transition"
                  />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button onClick={() => setStep("role")} className="px-5 py-3 text-sm text-[#525252] hover:text-[#1a1a1a] transition">Back</button>
                <button
                  onClick={() => setStep("pacer")}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-[#1e3a5f] to-[#2a5080] text-white text-sm font-semibold rounded-xl hover:from-[#162a47] hover:to-[#1e3a5f] transition-all shadow-sm"
                >
                  Continue
                </button>
              </div>
              <div className="text-center mt-4">
                <button onClick={skip} className="text-xs text-[#8a8a8a] hover:text-[#525252] transition underline underline-offset-2">
                  Skip this step
                </button>
              </div>
            </div>
          )}

          {/* PACER */}
          {step === "pacer" && (
            <div className="animate-in fade-in">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-9 h-9 rounded-xl bg-[#1e3a5f]/[0.08] flex items-center justify-center">
                  <PacerIcon className="w-5 h-5 text-[#1e3a5f]" />
                </div>
                <h2 className="text-xl font-bold tracking-tight text-[#1a1a1a]">PACER credentials</h2>
              </div>
              <p className="text-[#525252] text-sm mb-6 ml-12">
                Optional for now. You can file without PACER — ECFiler validates, analyzes, and prepares your filing. PACER is only needed for automated submission.
              </p>
              <div className="bg-[#fafaf8] border border-[#e8e5e0] rounded-xl p-5 mb-6">
                <div className="text-sm font-semibold text-[#1a1a1a] mb-3">What works without PACER:</div>
                <div className="space-y-2">
                  {["PDF validation & redaction scanning", "AI document analysis & event code matching", "Filing review with verification checks", "Certificate of service generation"].map((f) => (
                    <div key={f} className="flex items-center gap-2.5 text-xs text-[#525252]">
                      <div className="w-5 h-5 rounded-full bg-[#f0fdf4] text-[#15803d] flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={3}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      {f}
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button onClick={() => setStep("court")} className="px-5 py-3 text-sm text-[#525252] hover:text-[#1a1a1a] transition">Back</button>
                <button
                  onClick={() => setStep("done")}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-[#1e3a5f] to-[#2a5080] text-white text-sm font-semibold rounded-xl hover:from-[#162a47] hover:to-[#1e3a5f] transition-all shadow-sm"
                >
                  Continue
                </button>
              </div>
              <div className="text-center mt-4">
                <button onClick={skip} className="text-xs text-[#8a8a8a] hover:text-[#525252] transition underline underline-offset-2">
                  Skip this step
                </button>
              </div>
            </div>
          )}

          {/* Done */}
          {step === "done" && (
            <div className="text-center animate-in fade-in">
              <div className="w-20 h-20 bg-gradient-to-br from-[#15803d] to-[#166534] rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-[#15803d]/20">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-bold tracking-tight text-[#1a1a1a] mb-3">You&apos;re all set</h2>
              <p className="text-[#525252] text-sm mb-8">
                Drop a PDF to start filing. ECFiler handles the rest.
              </p>
              <button
                onClick={finish}
                className="px-8 py-3.5 bg-gradient-to-r from-[#1e3a5f] to-[#2a5080] text-white text-sm font-semibold rounded-xl hover:from-[#162a47] hover:to-[#1e3a5f] transition-all shadow-md shadow-[#1e3a5f]/15 w-full"
              >
                Start Filing &rarr;
              </button>
            </div>
          )}
        </div>

        {/* Footer note */}
        <p className="text-center text-[10px] text-[#8a8a8a] mt-6">
          You can update these settings anytime from your profile.
        </p>
      </div>
    </div>
  );
}
