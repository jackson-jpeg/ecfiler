export default function AppLoading() {
  return (
    <div className="min-h-screen bg-[#f5f3ee] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-xl flex items-center justify-center shadow-lg shadow-[#1e3a5f]/20 animate-pulse">
          <span className="text-white text-[12px] font-bold">E</span>
        </div>
        <div className="flex gap-1.5">
          <div className="w-2 h-2 bg-[#1e3a5f] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
          <div className="w-2 h-2 bg-[#1e3a5f] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
          <div className="w-2 h-2 bg-[#1e3a5f] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  );
}
