"use client";

import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";

export default function SettingsPage() {
  const { user } = useUser();
  const [pacerUsername, setPacerUsername] = useState("");
  const [pacerPassword, setPacerPassword] = useState("");
  const [pacerSaved, setPacerSaved] = useState(false);
  const [pacerTesting, setPacerTesting] = useState(false);
  const [pacerStatus, setPacerStatus] = useState<"none" | "ok" | "error">("none");

  const [defaultCourt, setDefaultCourt] = useState("");
  const [firmName, setFirmName] = useState("");
  const [barNumber, setBarNumber] = useState("");
  const [profileSaved, setProfileSaved] = useState(false);

  // Load saved settings from localStorage
  useEffect(() => {
    setPacerUsername(localStorage.getItem("ecfiler_pacer_user") || "");
    setDefaultCourt(localStorage.getItem("ecfiler_court") || "");
    setFirmName(localStorage.getItem("ecfiler_firm") || "");
    setBarNumber(localStorage.getItem("ecfiler_bar") || "");
    if (localStorage.getItem("ecfiler_pacer_user")) setPacerSaved(true);
  }, []);

  const savePacer = async () => {
    // Store username locally, send password to server for encrypted storage
    localStorage.setItem("ecfiler_pacer_user", pacerUsername);

    if (pacerPassword) {
      try {
        await fetch("/api/pacer/credentials", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: pacerUsername,
            password: pacerPassword,
            user_id: user?.id,
          }),
        });
      } catch {
        // Server storage failed — still save username locally
      }
    }

    setPacerSaved(true);
    setPacerPassword(""); // Clear from memory
    setTimeout(() => setPacerSaved(false), 3000);
  };

  const testPacer = async () => {
    setPacerTesting(true);
    setPacerStatus("none");
    try {
      const resp = await fetch("/api/pacer/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: pacerUsername, user_id: user?.id }),
      });
      const data = await resp.json();
      setPacerStatus(data.ok ? "ok" : "error");
    } catch {
      setPacerStatus("error");
    }
    setPacerTesting(false);
  };

  const saveProfile = () => {
    localStorage.setItem("ecfiler_court", defaultCourt);
    localStorage.setItem("ecfiler_firm", firmName);
    localStorage.setItem("ecfiler_bar", barNumber);
    setProfileSaved(true);
    setTimeout(() => setProfileSaved(false), 3000);
  };

  return (
    <div className="min-h-screen bg-[#f5f3ee]">
      {/* Top bar */}
      <header className="bg-white border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-3xl mx-auto px-6 h-14 flex items-center gap-4">
          <a href="/file" className="text-[13px] text-[#8a8a8a] hover:text-[#1a1a1a] transition">&larr; Back to Filing</a>
          <div className="h-5 w-px bg-[#e8e5e0]" />
          <span className="text-[15px] font-semibold text-[#1a1a1a]">Settings</span>
        </div>
      </header>
      <div className="max-w-2xl mx-auto px-6 py-10">
      <p className="text-[#525252] text-sm mb-8">Manage your account, PACER credentials, and subscription.</p>

      {/* Profile */}
      <section className="mb-10">
        <h2 className="text-sm font-bold uppercase tracking-wide text-[#8a8a8a] mb-4">Profile</h2>
        <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-4 mb-2">
            <div className="w-10 h-10 bg-[#e8e5e0] rounded-full flex items-center justify-center text-[#525252] text-sm font-bold">
              {user?.firstName?.[0] || user?.emailAddresses[0]?.emailAddress?.[0]?.toUpperCase() || "?"}
            </div>
            <div>
              <div className="text-sm font-semibold">{user?.fullName || user?.emailAddresses[0]?.emailAddress || "User"}</div>
              <div className="text-xs text-[#8a8a8a]">{user?.emailAddresses[0]?.emailAddress}</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Default Court</label>
              <input type="text" value={defaultCourt} onChange={(e) => setDefaultCourt(e.target.value)} placeholder="e.g., nysd" className="w-full px-3 py-2 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f]" />
            </div>
            <div>
              <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Firm</label>
              <input type="text" value={firmName} onChange={(e) => setFirmName(e.target.value)} placeholder="Smith & Associates" className="w-full px-3 py-2 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f]" />
            </div>
          </div>
          <div>
            <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Bar Number</label>
            <input type="text" value={barNumber} onChange={(e) => setBarNumber(e.target.value)} placeholder="NY12345" className="w-full px-3 py-2 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f] max-w-xs" />
          </div>
          <button onClick={saveProfile} className="px-5 py-2 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] transition">
            {profileSaved ? "✓ Saved" : "Save Profile"}
          </button>
        </div>
      </section>

      {/* PACER */}
      <section className="mb-10">
        <h2 className="text-sm font-bold uppercase tracking-wide text-[#8a8a8a] mb-4">PACER Credentials</h2>
        <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6">
          <p className="text-sm text-[#525252] mb-4">
            Your PACER credentials are used to authenticate with CM/ECF for filing. The password is encrypted and never stored in plaintext.
          </p>
          <div className="space-y-3 mb-4">
            <div>
              <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">PACER Username</label>
              <input type="text" value={pacerUsername} onChange={(e) => setPacerUsername(e.target.value)} placeholder="your@email.com" className="w-full px-3 py-2 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f] max-w-sm" />
            </div>
            <div>
              <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">PACER Password</label>
              <input type="password" value={pacerPassword} onChange={(e) => setPacerPassword(e.target.value)} placeholder="••••••••" className="w-full px-3 py-2 border border-[#e8e5e0] rounded-xl text-sm outline-none focus:border-[#1e3a5f] max-w-sm" />
              <p className="text-[11px] text-[#8a8a8a] mt-1">Encrypted on the server. Never stored in plaintext.</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={savePacer} disabled={!pacerUsername} className="px-5 py-2 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] disabled:opacity-20 transition">
              {pacerSaved ? "✓ Saved" : "Save Credentials"}
            </button>
            <button onClick={testPacer} disabled={!pacerUsername || pacerTesting} className="px-5 py-2 border border-[#e8e5e0] text-sm font-semibold rounded-xl hover:bg-[#fafaf8] disabled:opacity-20 transition">
              {pacerTesting ? "Testing..." : "Test Connection"}
            </button>
          </div>
          {pacerStatus === "ok" && <p className="text-sm text-[#15803d] mt-3">✓ PACER authentication successful</p>}
          {pacerStatus === "error" && <p className="text-sm text-[#b91c1c] mt-3">✗ Authentication failed — check your credentials</p>}
        </div>
      </section>

      {/* Subscription */}
      <section className="mb-10">
        <h2 className="text-sm font-bold uppercase tracking-wide text-[#8a8a8a] mb-4">Subscription</h2>
        <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-sm font-semibold">Free Plan</div>
              <div className="text-xs text-[#8a8a8a]">All features, self-hosted filing</div>
            </div>
            <span className="text-xs px-2.5 py-1 bg-[#f5f5f0] text-[#525252] rounded-full font-semibold">Current</span>
          </div>
          <div className="border border-blue-200 bg-blue-50 rounded-xl p-4 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-semibold text-blue-900">ECFiler Pro</div>
                <div className="text-xs text-blue-700">$99/attorney/month — hosted filing, team management, priority support</div>
              </div>
              <div className="text-lg font-bold text-blue-900">$99<span className="text-xs font-normal text-blue-500">/mo</span></div>
            </div>
          </div>
          <button className="px-5 py-2 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] transition">
            Upgrade to Pro
          </button>
          <p className="text-[11px] text-[#8a8a8a] mt-2">Stripe checkout — cancel anytime</p>
        </div>
      </section>

      {/* What works without PACER */}
      <section>
        <h2 className="text-sm font-bold uppercase tracking-wide text-[#8a8a8a] mb-4">Feature Access</h2>
        <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6">
          <div className="space-y-2">
            {[
              { feature: "PDF validation & redaction scanning", free: true, needsPacer: false },
              { feature: "AI document analysis & event code matching", free: true, needsPacer: false },
              { feature: "Filing review with verification checks", free: true, needsPacer: false },
              { feature: "Certificate of service generation", free: true, needsPacer: false },
              { feature: "Court & event code search (207 courts)", free: true, needsPacer: false },
              { feature: "Automated CM/ECF submission", free: true, needsPacer: true },
              { feature: "Live browser view of filing", free: true, needsPacer: true },
            ].map((f) => (
              <div key={f.feature} className="flex items-center gap-3 text-sm">
                <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                  f.needsPacer && !pacerUsername ? "bg-[#f5f5f0] text-[#8a8a8a]" : "bg-[#f0fdf4] text-[#15803d]"
                }`}>
                  {f.needsPacer && !pacerUsername ? "—" : "✓"}
                </div>
                <span className={f.needsPacer && !pacerUsername ? "text-[#8a8a8a]" : ""}>{f.feature}</span>
                {f.needsPacer && !pacerUsername && <span className="text-[10px] text-[#8a8a8a] bg-[#f5f5f0] px-1.5 py-0.5 rounded">needs PACER</span>}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
    </div>
  );
}
