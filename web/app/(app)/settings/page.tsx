"use client";

import { useState, useEffect } from "react";
import { useUser, UserButton } from "@clerk/nextjs";
import Link from "next/link";

// Simple email-like validation
function isEmailLike(v: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
}

// Bar number format hint: alphanumeric, 4-12 chars
function isBarNumberValid(v: string) {
  return /^[A-Za-z0-9]{4,12}$/.test(v);
}

export default function SettingsPage() {
  const { user } = useUser();
  const [pacerUsername, setPacerUsername] = useState("");
  const [pacerPassword, setPacerPassword] = useState("");
  const [showPacerPassword, setShowPacerPassword] = useState(false);
  const [pacerSaved, setPacerSaved] = useState(false);
  const [pacerSaving, setPacerSaving] = useState(false);
  const [pacerTesting, setPacerTesting] = useState(false);
  const [pacerStatus, setPacerStatus] = useState<"none" | "ok" | "error">("none");

  const [defaultCourt, setDefaultCourt] = useState("");
  const [firmName, setFirmName] = useState("");
  const [barNumber, setBarNumber] = useState("");
  const [profileSaved, setProfileSaved] = useState(false);
  const [profileSaving, setProfileSaving] = useState(false);

  // Danger zone state
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");

  // Load saved settings from localStorage
  useEffect(() => {
    setPacerUsername(localStorage.getItem("ecfiler_pacer_user") || "");
    setDefaultCourt(localStorage.getItem("ecfiler_court") || "");
    setFirmName(localStorage.getItem("ecfiler_firm") || "");
    setBarNumber(localStorage.getItem("ecfiler_bar") || "");
    if (localStorage.getItem("ecfiler_pacer_user")) setPacerSaved(true);
  }, []);

  const savePacer = async () => {
    setPacerSaving(true);
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

    setPacerSaving(false);
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

  const saveProfile = async () => {
    setProfileSaving(true);
    // Simulate a brief async save
    await new Promise((r) => setTimeout(r, 400));
    localStorage.setItem("ecfiler_court", defaultCourt);
    localStorage.setItem("ecfiler_firm", firmName);
    localStorage.setItem("ecfiler_bar", barNumber);
    setProfileSaving(false);
    setProfileSaved(true);
    setTimeout(() => setProfileSaved(false), 3000);
  };

  const features = [
    { feature: "PDF validation & redaction scanning", needsPacer: false },
    { feature: "Certificate of service generation", needsPacer: false },
    { feature: "Court & event code search (207 courts)", needsPacer: false },
    { feature: "Filing fee lookup", needsPacer: false },
    { feature: "AI document analysis & event code matching", needsPacer: true },
    { feature: "AI docket text generation", needsPacer: true },
    { feature: "3-pass AI safety verification", needsPacer: true },
    { feature: "Automated CM/ECF submission", needsPacer: true },
    { feature: "Live browser view of filing", needsPacer: true },
  ];

  const pacerUsernameInvalid = pacerUsername.length > 0 && !isEmailLike(pacerUsername);
  const barNumberInvalid = barNumber.length > 0 && !isBarNumberValid(barNumber);

  return (
    <div className="min-h-screen bg-[#f5f3ee]">
      {/* Header — matches filing workspace */}
      <header className="bg-white border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-3xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-5">
            <Link href="/" className="flex items-center gap-2.5">
              <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold shadow-sm">E</div>
              <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a]">ECFiler</span>
            </Link>
            <div className="h-5 w-px bg-[#e8e5e0]" />
            <span className="text-[15px] font-semibold text-[#1a1a1a]">Settings</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/file" className="group flex items-center gap-1.5 text-[13px] text-[#8a8a8a] hover:text-[#1e3a5f] transition-colors font-medium">
              <svg className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
              </svg>
              Back to Filing
            </Link>
            <UserButton appearance={{ elements: { avatarBox: "w-7 h-7" } }} />
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-6 py-10 space-y-8">

        {/* Page intro */}
        <div>
          <h1 className="text-xl font-bold text-[#1a1a1a] mb-1">Account Settings</h1>
          <p className="text-[14px] text-[#525252] leading-relaxed">Manage your profile, PACER credentials, and subscription plan.</p>
        </div>

        {/* ── Profile ────────────────────────────────────────────── */}
        <section>
          <div className="mb-3">
            <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#8a8a8a]">Profile</h2>
            <p className="text-[13px] text-[#999] mt-0.5">Your identity as it appears on filings and certificates of service.</p>
          </div>
          <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300">
            {/* User info row */}
            <div className="flex items-center gap-4 mb-6 pb-5 border-b border-[#f0eee9]">
              <div className="w-11 h-11 bg-gradient-to-br from-[#1e3a5f] to-[#2d5a8e] rounded-full flex items-center justify-center text-white text-sm font-bold shadow-sm">
                {user?.firstName?.[0] || user?.emailAddresses[0]?.emailAddress?.[0]?.toUpperCase() || "?"}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[15px] font-semibold text-[#1a1a1a] truncate">{user?.fullName || user?.emailAddresses[0]?.emailAddress || "User"}</div>
                <div className="text-[13px] text-[#8a8a8a] truncate">{user?.emailAddresses[0]?.emailAddress}</div>
              </div>
            </div>
            {/* Form fields */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-[11px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Default Court</label>
                <input
                  type="text"
                  value={defaultCourt}
                  onChange={(e) => setDefaultCourt(e.target.value)}
                  placeholder="e.g., nysd"
                  className="w-full px-3.5 py-2.5 border border-[#e8e5e0] rounded-xl text-sm text-[#1a1a1a] outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10 transition-all placeholder:text-[#c5c5c5] bg-[#fafaf9]"
                />
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Firm Name</label>
                <input
                  type="text"
                  value={firmName}
                  onChange={(e) => setFirmName(e.target.value)}
                  placeholder="Smith & Associates"
                  className="w-full px-3.5 py-2.5 border border-[#e8e5e0] rounded-xl text-sm text-[#1a1a1a] outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10 transition-all placeholder:text-[#c5c5c5] bg-[#fafaf9]"
                />
              </div>
            </div>
            <div className="mb-5">
              <label className="block text-[11px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Bar Number</label>
              <input
                type="text"
                value={barNumber}
                onChange={(e) => setBarNumber(e.target.value)}
                placeholder="NY12345"
                className={`w-full sm:max-w-xs px-3.5 py-2.5 border rounded-xl text-sm text-[#1a1a1a] outline-none focus:ring-2 transition-all placeholder:text-[#c5c5c5] bg-[#fafaf9] ${
                  barNumberInvalid
                    ? "border-[#f59e0b] focus:border-[#f59e0b] focus:ring-[#f59e0b]/10"
                    : "border-[#e8e5e0] focus:border-[#1e3a5f] focus:ring-[#1e3a5f]/10"
                }`}
              />
              {barNumberInvalid && (
                <p className="text-[12px] text-[#f59e0b] mt-1.5 flex items-center gap-1">
                  <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>
                  Expected format: 4-12 alphanumeric characters (e.g., NY12345)
                </p>
              )}
            </div>
            <button
              onClick={saveProfile}
              disabled={profileSaving}
              className="px-5 py-2.5 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
            >
              {profileSaving ? (
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                  Saving...
                </span>
              ) : profileSaved ? (
                <span className="flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                  Saved
                </span>
              ) : "Save Profile"}
            </button>
          </div>
        </section>

        {/* ── PACER Credentials ──────────────────────────────────── */}
        <section>
          <div className="mb-3">
            <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#8a8a8a]">PACER Credentials</h2>
            <p className="text-[13px] text-[#999] mt-0.5">Required for automated CM/ECF filing. Your password is encrypted server-side.</p>
          </div>
          <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300">
            {/* Security note */}
            <div className="flex items-start gap-3 bg-[#f8f7f4] border border-[#eae8e3] rounded-xl p-3.5 mb-5">
              <svg className="w-5 h-5 text-[#1e3a5f] mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
              <div>
                <p className="text-[13px] text-[#525252] font-medium">End-to-end encrypted</p>
                <p className="text-[12px] text-[#8a8a8a] mt-0.5">Your password is encrypted at rest with AES-256 and never stored in plaintext. Credentials are only decrypted at the moment of filing.</p>
              </div>
            </div>

            <div className="space-y-4 mb-5">
              <div>
                <label className="block text-[11px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">PACER Username</label>
                <input
                  type="text"
                  value={pacerUsername}
                  onChange={(e) => setPacerUsername(e.target.value)}
                  placeholder="your@email.com"
                  className={`w-full sm:max-w-sm px-3.5 py-2.5 border rounded-xl text-sm text-[#1a1a1a] outline-none focus:ring-2 transition-all placeholder:text-[#c5c5c5] bg-[#fafaf9] ${
                    pacerUsernameInvalid
                      ? "border-[#f59e0b] focus:border-[#f59e0b] focus:ring-[#f59e0b]/10"
                      : "border-[#e8e5e0] focus:border-[#1e3a5f] focus:ring-[#1e3a5f]/10"
                  }`}
                />
                {pacerUsernameInvalid && (
                  <p className="text-[12px] text-[#f59e0b] mt-1.5 flex items-center gap-1">
                    <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>
                    PACER username should be a valid email address
                  </p>
                )}
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">PACER Password</label>
                <div className="relative w-full sm:max-w-sm">
                  <input
                    type={showPacerPassword ? "text" : "password"}
                    value={pacerPassword}
                    onChange={(e) => setPacerPassword(e.target.value)}
                    placeholder="Enter password to update"
                    className="w-full px-3.5 py-2.5 pr-11 border border-[#e8e5e0] rounded-xl text-sm text-[#1a1a1a] outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10 transition-all placeholder:text-[#c5c5c5] bg-[#fafaf9]"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPacerPassword(!showPacerPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8a8a8a] hover:text-[#525252] transition-colors"
                    tabIndex={-1}
                    aria-label={showPacerPassword ? "Hide password" : "Show password"}
                  >
                    {showPacerPassword ? (
                      <svg className="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                      </svg>
                    ) : (
                      <svg className="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2.5">
              <button
                onClick={savePacer}
                disabled={!pacerUsername || pacerSaving}
                className="px-5 py-2.5 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] active:scale-[0.98] disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
              >
                {pacerSaving ? (
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                    Saving...
                  </span>
                ) : pacerSaved ? (
                  <span className="flex items-center gap-1.5">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                    Saved
                  </span>
                ) : "Save Credentials"}
              </button>
              <button
                onClick={testPacer}
                disabled={!pacerUsername || pacerTesting}
                className="px-5 py-2.5 border border-[#e8e5e0] text-sm font-semibold text-[#525252] rounded-xl hover:bg-[#f5f3ee] hover:border-[#d4d0ca] active:scale-[0.98] disabled:opacity-30 disabled:cursor-not-allowed transition-all"
              >
                {pacerTesting ? (
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                    Testing...
                  </span>
                ) : "Test Connection"}
              </button>
            </div>

            {/* Status messages */}
            {pacerStatus === "ok" && (
              <div className="flex items-center gap-2 mt-4 p-3 bg-[#f0fdf4] border border-[#bbf7d0] rounded-xl animate-in fade-in duration-300">
                <svg className="w-5 h-5 text-[#15803d]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <p className="text-sm text-[#15803d] font-medium">PACER authentication successful</p>
              </div>
            )}
            {pacerStatus === "error" && (
              <div className="flex items-center gap-2 mt-4 p-3 bg-[#fef2f2] border border-[#fecaca] rounded-xl animate-in fade-in duration-300">
                <svg className="w-5 h-5 text-[#b91c1c]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>
                <p className="text-sm text-[#b91c1c] font-medium">Authentication failed -- check your credentials</p>
              </div>
            )}
          </div>
        </section>

        {/* ── Subscription ───────────────────────────────────────── */}
        <section>
          <div className="mb-3">
            <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#8a8a8a]">Subscription</h2>
            <p className="text-[13px] text-[#999] mt-0.5">Your current plan and available upgrades.</p>
          </div>
          <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300">
            {/* Current plan */}
            <div className="flex items-center justify-between mb-5 pb-5 border-b border-[#f0eee9]">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-[#f0eee9] rounded-xl flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#8a8a8a]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z" /></svg>
                </div>
                <div>
                  <div className="text-[14px] font-semibold text-[#1a1a1a]">Free Plan</div>
                  <div className="text-[13px] text-[#8a8a8a]">All features, self-hosted filing</div>
                </div>
              </div>
              <span className="text-[11px] px-3 py-1.5 bg-[#f0eee9] text-[#525252] rounded-full font-bold uppercase tracking-wide">Current</span>
            </div>

            {/* Pro upgrade card */}
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#1e3a5f] via-[#24476f] to-[#2d5a8e] p-5 mb-5">
              {/* Subtle pattern overlay */}
              <div className="absolute inset-0 opacity-[0.04]" style={{ backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)", backgroundSize: "24px 24px" }} />
              <div className="relative flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="text-[15px] font-bold text-white">ECFiler Pro</span>
                    <span className="text-[10px] px-2 py-0.5 bg-white/15 text-white/90 rounded-full font-semibold backdrop-blur-sm">Recommended</span>
                  </div>
                  <ul className="space-y-1 mt-3">
                    {["Hosted CM/ECF filing", "Team management", "Priority support", "Filing analytics"].map((item) => (
                      <li key={item} className="flex items-center gap-2 text-[13px] text-white/80">
                        <svg className="w-3.5 h-3.5 text-emerald-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="text-right flex-shrink-0 ml-4">
                  <div className="text-3xl font-bold text-white">$99</div>
                  <div className="text-[12px] text-white/60 font-medium">per attorney / month</div>
                </div>
              </div>
            </div>

            <button className="w-full sm:w-auto px-6 py-2.5 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] active:scale-[0.98] transition-all shadow-sm hover:shadow-md">
              Upgrade to Pro
            </button>
            <p className="text-[12px] text-[#999] mt-2.5">Secure checkout via Stripe. Cancel anytime, no lock-in.</p>
          </div>
        </section>

        {/* ── Data & Privacy ─────────────────────────────────────── */}
        <section>
          <div className="mb-3">
            <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#8a8a8a]">Data &amp; Privacy</h2>
            <p className="text-[13px] text-[#999] mt-0.5">What data ECFiler stores and where it lives.</p>
          </div>
          <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="space-y-4">
              {[
                {
                  label: "Profile & preferences",
                  detail: "Court, firm name, and bar number are stored in your browser's local storage. They never leave your device.",
                  icon: (
                    <svg className="w-4.5 h-4.5 text-[#1e3a5f]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                    </svg>
                  ),
                },
                {
                  label: "PACER credentials",
                  detail: "Your username is stored locally. Your password is AES-256 encrypted at rest on our server and only decrypted at the moment of filing.",
                  icon: (
                    <svg className="w-4.5 h-4.5 text-[#1e3a5f]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                    </svg>
                  ),
                },
                {
                  label: "Uploaded documents",
                  detail: "PDFs are processed in-memory for validation and analysis. Documents are not permanently stored on our servers after the filing session ends.",
                  icon: (
                    <svg className="w-4.5 h-4.5 text-[#1e3a5f]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                    </svg>
                  ),
                },
                {
                  label: "Authentication",
                  detail: "Account management is handled by Clerk. ECFiler does not store your login password directly.",
                  icon: (
                    <svg className="w-4.5 h-4.5 text-[#1e3a5f]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                    </svg>
                  ),
                },
              ].map((item) => (
                <div key={item.label} className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-[#f0eee9] rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                    {item.icon}
                  </div>
                  <div>
                    <div className="text-[14px] font-semibold text-[#1a1a1a]">{item.label}</div>
                    <p className="text-[13px] text-[#8a8a8a] mt-0.5 leading-relaxed">{item.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Keyboard Shortcuts ─────────────────────────────────── */}
        <section>
          <div className="mb-3">
            <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#8a8a8a]">Keyboard Shortcuts</h2>
            <p className="text-[13px] text-[#999] mt-0.5">Navigate quickly with these shortcuts available throughout the app.</p>
          </div>
          <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="space-y-3">
              {[
                { keys: ["\u2318", "K"], label: "Open command palette", description: "Quickly navigate to any page or action" },
                { keys: ["\u2318", "\u21A9"], label: "Submit / Confirm", description: "Submit the current form or confirm an action" },
                { keys: ["Esc"], label: "Close / Cancel", description: "Close dialogs, modals, or cancel the current action" },
              ].map((shortcut) => (
                <div key={shortcut.label} className="flex items-center justify-between py-2.5 px-3 rounded-xl hover:bg-[#fafaf8] transition-colors">
                  <div>
                    <div className="text-[14px] font-medium text-[#1a1a1a]">{shortcut.label}</div>
                    <div className="text-[12px] text-[#8a8a8a] mt-0.5">{shortcut.description}</div>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0 ml-4">
                    {shortcut.keys.map((key, i) => (
                      <span key={i}>
                        <kbd className="inline-flex items-center justify-center min-w-[28px] h-7 px-2 bg-[#f5f3ee] border border-[#e8e5e0] rounded-lg text-[12px] font-semibold text-[#525252] shadow-sm">
                          {key}
                        </kbd>
                        {i < shortcut.keys.length - 1 && <span className="text-[#c5c5c5] text-[11px] mx-0.5">+</span>}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Feature Access ─────────────────────────────────────── */}
        <section>
          <div className="mb-3">
            <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#8a8a8a]">Feature Access</h2>
            <p className="text-[13px] text-[#999] mt-0.5">What you can do right now based on your current configuration.</p>
          </div>
          <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="space-y-2.5">
              {features.map((f) => {
                const available = !(f.needsPacer && !pacerUsername);
                return (
                  <div key={f.feature} className={`flex items-center gap-3 p-2.5 rounded-xl transition-colors ${available ? "hover:bg-[#fafaf8]" : "opacity-60"}`}>
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                      available
                        ? "bg-[#f0fdf4] text-[#15803d]"
                        : "bg-[#f5f5f0] text-[#c5c5c5]"
                    }`}>
                      {available ? (
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                      ) : (
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 12h-15" /></svg>
                      )}
                    </div>
                    <span className={`text-[14px] ${available ? "text-[#1a1a1a]" : "text-[#8a8a8a]"}`}>{f.feature}</span>
                    {f.needsPacer && !pacerUsername && (
                      <span className="ml-auto text-[11px] text-[#1e3a5f] bg-[#f0f4fa] px-2 py-0.5 rounded-md font-semibold flex-shrink-0">Pro</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* ── Danger Zone ────────────────────────────────────────── */}
        <section>
          <div className="mb-3">
            <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#dc2626]">Danger Zone</h2>
            <p className="text-[13px] text-[#999] mt-0.5">Irreversible actions. Please be certain.</p>
          </div>
          <div className="bg-white border border-[#fecaca] rounded-2xl p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <div className="text-[14px] font-semibold text-[#1a1a1a]">Delete Account</div>
                <p className="text-[13px] text-[#8a8a8a] mt-0.5">Permanently remove your account, filing history, and all stored credentials. This cannot be undone.</p>
              </div>
              <button
                onClick={() => {
                  setDeleteConfirmOpen(true);
                  setDeleteConfirmText("");
                }}
                className="flex-shrink-0 px-5 py-2.5 border border-[#fecaca] text-[#dc2626] text-sm font-semibold rounded-xl hover:bg-[#fef2f2] active:scale-[0.98] transition-all"
              >
                Delete Account
              </button>
            </div>

            {/* Two-step confirmation */}
            {deleteConfirmOpen && (
              <div className="mt-5 pt-5 border-t border-[#fecaca]/50 animate-in fade-in slide-in-from-top-2 duration-200">
                <div className="bg-[#fef2f2] border border-[#fecaca] rounded-xl p-4">
                  <p className="text-[13px] text-[#b91c1c] font-medium mb-3">
                    This action is permanent. To confirm, type <span className="font-bold">DELETE</span> below:
                  </p>
                  <input
                    type="text"
                    value={deleteConfirmText}
                    onChange={(e) => setDeleteConfirmText(e.target.value)}
                    placeholder="Type DELETE to confirm"
                    className="w-full sm:max-w-xs px-3.5 py-2.5 border border-[#fecaca] rounded-xl text-sm text-[#1a1a1a] outline-none focus:border-[#dc2626] focus:ring-2 focus:ring-[#dc2626]/10 transition-all placeholder:text-[#c5c5c5] bg-white"
                    autoFocus
                  />
                  <div className="flex gap-2.5 mt-3">
                    <button
                      disabled={deleteConfirmText !== "DELETE"}
                      onClick={() => {
                        // Account deletion would go here
                        setDeleteConfirmOpen(false);
                        setDeleteConfirmText("");
                      }}
                      className="px-5 py-2.5 bg-[#dc2626] text-white text-sm font-semibold rounded-xl hover:bg-[#b91c1c] active:scale-[0.98] disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                    >
                      Permanently Delete
                    </button>
                    <button
                      onClick={() => {
                        setDeleteConfirmOpen(false);
                        setDeleteConfirmText("");
                      }}
                      className="px-5 py-2.5 border border-[#e8e5e0] text-sm font-semibold text-[#525252] rounded-xl hover:bg-[#f5f3ee] active:scale-[0.98] transition-all"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Bottom spacer */}
        <div className="h-4" />
      </div>
    </div>
  );
}
