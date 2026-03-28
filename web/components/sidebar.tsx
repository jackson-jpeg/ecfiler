"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton, useUser } from "@clerk/nextjs";

const filing = [
  { href: "/file", label: "New Filing", icon: "M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" },
  { href: "/drafts", label: "Drafts", icon: "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" },
  { href: "/history", label: "History", icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" },
];

const tools = [
  { href: "/validate", label: "Validate PDF", icon: "M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
  { href: "/certificate", label: "Certificate of Service", icon: "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" },
  { href: "/courts", label: "Courts", icon: "M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21" },
  { href: "/settings", label: "Settings", icon: "M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7 7 0 010 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a7 7 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a7 7 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.991a7 7 0 010-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28z M15 12a3 3 0 11-6 0 3 3 0 016 0z" },
];

function NavIcon({ d }: { d: string }) {
  return (
    <svg className="w-4 h-4 shrink-0 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d={d} />
    </svg>
  );
}

function NavItem({ href, label, icon, active }: { href: string; label: string; icon: string; active: boolean }) {
  return (
    <Link
      href={href}
      className={`flex items-center gap-2.5 px-2.5 py-[7px] rounded-lg text-[13px] transition-colors ${
        active
          ? "bg-zinc-700 text-white font-medium"
          : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
      }`}
    >
      <NavIcon d={icon} />
      {label}
    </Link>
  );
}

function UserName() {
  const { user } = useUser();
  if (!user) return null;
  return (
    <div className="min-w-0">
      <div className="text-xs text-zinc-300 font-medium truncate">{user.firstName || user.emailAddresses[0]?.emailAddress?.split("@")[0] || "User"}</div>
      <div className="text-[10px] text-zinc-600 truncate">{user.emailAddresses[0]?.emailAddress || ""}</div>
    </div>
  );
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[220px] bg-zinc-900 flex flex-col shrink-0 h-screen border-r border-zinc-800">
      <div className="px-4 pt-5 pb-6 flex items-center gap-2.5">
        <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center text-white text-[11px] font-bold">
          E
        </div>
        <span className="text-white text-[15px] font-semibold tracking-tight">
          ECFiler
        </span>
      </div>

      <div className="px-3 mb-5">
        <div className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest px-2.5 mb-1.5">
          Filing
        </div>
        {filing.map((item) => (
          <NavItem key={item.href} {...item} active={pathname === item.href} />
        ))}
      </div>

      <div className="px-3">
        <div className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest px-2.5 mb-1.5">
          Tools
        </div>
        {tools.map((item) => (
          <NavItem key={item.href} {...item} active={pathname === item.href} />
        ))}
      </div>

      <div className="mt-auto border-t border-zinc-800">
        <div className="px-4 py-3 flex items-center gap-3">
          <UserButton
            appearance={{
              elements: { avatarBox: "w-7 h-7" },
            }}
          />
          <UserName />
        </div>
        <div className="px-4 pb-3 flex gap-3">
          <a href="/api/docs" target="_blank" className="text-[11px] text-zinc-600 hover:text-zinc-400 transition">
            API
          </a>
          <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="text-[11px] text-zinc-600 hover:text-zinc-400 transition">
            GitHub
          </a>
        </div>
      </div>
    </aside>
  );
}
