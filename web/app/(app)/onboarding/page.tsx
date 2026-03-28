"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type OnboardingStep = "welcome" | "role" | "court" | "pacer" | "done";

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

  return (
    <div className="flex items-center justify-center min-h-screen p-8">
      <div className="max-w-md w-full">

        {/* Progress dots */}
        <div className="flex justify-center gap-2 mb-10">
          {["welcome", "role", "court", "pacer", "done"].map((s, i) => {
            const steps: OnboardingStep[] = ["welcome", "role", "court", "pacer", "done"];
            const current = steps.indexOf(step);
            return (
              <div key={s} className={`w-2 h-2 rounded-full transition-all ${i <= current ? "bg-[#1e3a5f] w-6" : "bg-[#e8e5e0]"}`} />
            );
          })}
        </div>

        {/* Welcome */}
        {step === "welcome" && (
          <div className="text-center animate-in fade-in">
            <div className="w-16 h-16 bg-[#1e3a5f] rounded-2xl flex items-center justify-center text-white text-xl font-bold mx-auto mb-6">E</div>
            <h1 className="text-2xl font-bold tracking-tight mb-3">Welcome to ECFiler</h1>
            <p className="text-[#525252] mb-8 leading-relaxed">
              AI-powered filing for federal courts. Let&apos;s get you set up in 30 seconds.
            </p>
            <button onClick={() => setStep("role")} className="px-8 py-3 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] transition shadow-sm w-full">
              Get Started
            </button>
          </div>
        )}

        {/* Role */}
        {step === "role" && (
          <div className="animate-in fade-in">
            <h2 className="text-xl font-bold tracking-tight mb-2">What&apos;s your role?</h2>
            <p className="text-[#525252] text-sm mb-6">This helps us customize your experience.</p>
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
                  className={`w-full text-left p-4 rounded-xl border transition ${
                    role === r.id ? "border-[#1e3a5f] bg-[#fafaf8]" : "border-[#e8e5e0] hover:border-[#d4d0ca]"
                  }`}
                >
                  <div className="text-sm font-semibold">{r.label}</div>
                  <div className="text-xs text-[#525252]">{r.desc}</div>
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <button onClick={() => setStep("welcome")} className="px-6 py-3 text-sm text-[#525252] hover:text-[#1a1a1a] transition">Back</button>
              <button onClick={() => setStep("court")} disabled={!role} className="flex-1 px-6 py-3 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] disabled:opacity-20 transition">
                Continue
              </button>
            </div>
          </div>
        )}

        {/* Court */}
        {step === "court" && (
          <div className="animate-in fade-in">
            <h2 className="text-xl font-bold tracking-tight mb-2">Your primary court</h2>
            <p className="text-[#525252] text-sm mb-6">Which court do you file in most? You can change this later.</p>
            <div className="space-y-3 mb-6">
              <div>
                <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Court</label>
                <input
                  type="text"
                  value={court}
                  onChange={(e) => setCourt(e.target.value)}
                  placeholder="e.g., S.D.N.Y. or nysd"
                  className="w-full px-4 py-2.5 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f] focus:ring-1 focus:ring-[#1e3a5f]/10"
                />
              </div>
              <div>
                <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Firm / Organization</label>
                <input
                  type="text"
                  value={firmName}
                  onChange={(e) => setFirmName(e.target.value)}
                  placeholder="e.g., Smith & Associates LLP"
                  className="w-full px-4 py-2.5 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f] focus:ring-1 focus:ring-[#1e3a5f]/10"
                />
              </div>
              <div>
                <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Bar Number (optional)</label>
                <input
                  type="text"
                  value={barNumber}
                  onChange={(e) => setBarNumber(e.target.value)}
                  placeholder="e.g., NY12345"
                  className="w-full px-4 py-2.5 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f] focus:ring-1 focus:ring-[#1e3a5f]/10"
                />
              </div>
            </div>
            <div className="flex gap-3">
              <button onClick={() => setStep("role")} className="px-6 py-3 text-sm text-[#525252] hover:text-[#1a1a1a] transition">Back</button>
              <button onClick={() => setStep("pacer")} className="flex-1 px-6 py-3 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] transition">
                Continue
              </button>
            </div>
          </div>
        )}

        {/* PACER */}
        {step === "pacer" && (
          <div className="animate-in fade-in">
            <h2 className="text-xl font-bold tracking-tight mb-2">PACER credentials</h2>
            <p className="text-[#525252] text-sm mb-6">
              Optional for now. You can file without PACER — ECFiler validates, analyzes, and prepares your filing. PACER is only needed for automated submission.
            </p>
            <div className="bg-[#fafaf8] border border-[#e8e5e0] rounded-xl p-4 mb-6">
              <div className="text-sm font-semibold mb-2">What works without PACER:</div>
              <div className="space-y-1.5">
                {["PDF validation & redaction scanning", "AI document analysis & event code matching", "Filing review with verification checks", "Certificate of service generation"].map((f) => (
                  <div key={f} className="flex items-center gap-2 text-xs text-[#525252]">
                    <div className="w-4 h-4 rounded-full bg-[#f0fdf4] text-[#15803d] flex items-center justify-center text-[9px] font-bold">✓</div>
                    {f}
                  </div>
                ))}
              </div>
            </div>
            <div className="flex gap-3">
              <button onClick={() => setStep("court")} className="px-6 py-3 text-sm text-[#525252] hover:text-[#1a1a1a] transition">Back</button>
              <button onClick={() => setStep("done")} className="flex-1 px-6 py-3 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] transition">
                Continue
              </button>
            </div>
          </div>
        )}

        {/* Done */}
        {step === "done" && (
          <div className="text-center animate-in fade-in">
            <div className="w-16 h-16 bg-[#f0fdf4] rounded-2xl flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-[#15803d]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-xl font-bold tracking-tight mb-3">You&apos;re all set</h2>
            <p className="text-[#525252] text-sm mb-8">
              Drop a PDF to start filing. ECFiler handles the rest.
            </p>
            <button onClick={finish} className="px-8 py-3 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] transition shadow-sm w-full">
              Start Filing &rarr;
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
