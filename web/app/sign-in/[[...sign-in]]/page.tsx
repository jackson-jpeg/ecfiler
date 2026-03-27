import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50">
      <div className="text-center">
        <div className="flex items-center justify-center gap-2.5 mb-8">
          <div className="w-8 h-8 bg-zinc-900 rounded-lg flex items-center justify-center text-white text-xs font-bold">E</div>
          <span className="text-lg font-semibold tracking-tight">ECFiler</span>
        </div>
        <SignIn
          fallbackRedirectUrl="/file"
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-xl shadow-zinc-200/50 border border-zinc-200",
            },
          }}
        />
      </div>
    </div>
  );
}
