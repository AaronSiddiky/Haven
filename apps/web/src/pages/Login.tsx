import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    const raf = requestAnimationFrame(() => setRevealed(true));
    return () => cancelAnimationFrame(raf);
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);

    if (!email || !password) {
      setFormError("Email and password are required");
      return;
    }

    setSubmitting(true);
    try {
      // Placeholder login while auth provider is being wired.
      await new Promise((resolve) => setTimeout(resolve, 300));
      navigate("/voice");
    } catch (_error) {
      setFormError("Log in failed — please try again");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="relative min-h-[100dvh] overflow-hidden">
      <img
        src="/Haven login 3.png"
        alt=""
        aria-hidden="true"
        className="absolute inset-0 h-full w-full object-cover object-center"
        style={{
          filter: revealed ? "blur(0px)" : "blur(10px)",
          transform: revealed ? "scale(1)" : "scale(1.03)",
          transition: "filter 700ms cubic-bezier(0.22,1,0.36,1), transform 900ms cubic-bezier(0.22,1,0.36,1)",
        }}
      />
      <div
        className="absolute inset-0 bg-gradient-to-br from-[#f7d8f0]/35 via-[#e8d7ff]/30 to-[#d5ebff]/25"
        aria-hidden="true"
        style={{
          opacity: revealed ? 1 : 0,
          transition: "opacity 650ms ease-out 80ms",
        }}
      />

      <Link
        to="/"
        className="absolute left-5 top-5 z-20 flex items-center gap-2.5 rounded-lg py-1 text-white/85 transition-colors hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-white/50 sm:left-8 sm:top-6"
        style={{
          opacity: revealed ? 1 : 0,
          transform: revealed ? "translateY(0)" : "translateY(-8px)",
          transition: "opacity 550ms ease-out 160ms, transform 550ms ease-out 160ms",
        }}
      >
        <span className="relative block h-10 w-[138px] overflow-hidden">
          <img
            src="/Haven Logo.png"
            alt="Haven"
            className="absolute inset-0 h-full w-full scale-[2.6] object-contain"
          />
        </span>
      </Link>

      <div
        className="relative z-10 flex min-h-[100dvh] items-center justify-center px-4 py-10"
        style={{
          opacity: revealed ? 1 : 0,
          transform: revealed ? "translateY(0)" : "translateY(14px)",
          transition: "opacity 700ms cubic-bezier(0.22,1,0.36,1) 180ms, transform 700ms cubic-bezier(0.22,1,0.36,1) 180ms",
        }}
      >
        <div className="w-full max-w-[430px] rounded-[2rem] border border-white/70 bg-white/70 p-6 shadow-[0_30px_80px_rgba(20,35,70,0.22)] backdrop-blur-xl sm:p-8">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-slate-200/70 bg-white/85 text-2xl shadow-sm">
            <span aria-hidden>↪</span>
          </div>

          <h1 className="mt-5 text-center text-[2rem] font-semibold leading-tight text-slate-900">
            Sign in with email
          </h1>
          <p className="mx-auto mt-2 max-w-[300px] text-center text-sm text-slate-500">
            Continue your session with Haven.
          </p>

          <form onSubmit={onSubmit} noValidate className="mt-6">
            <div className="rounded-2xl border border-white/80 bg-gradient-to-b from-white/95 via-[#eff7ff]/90 to-[#deebff]/90 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.9)]">
              {formError && (
                <p role="alert" className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  {formError}
                </p>
              )}

              <label htmlFor="login-email" className="sr-only">
                Email
              </label>
              <input
                id="login-email"
                name="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                className="h-12 w-full rounded-xl border border-white/90 bg-white/85 px-4 text-slate-800 shadow-sm outline-none placeholder:text-slate-400 focus-visible:ring-2 focus-visible:ring-sky-300/60"
              />

              <label htmlFor="login-password" className="sr-only">
                Password
              </label>
              <input
                id="login-password"
                name="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className="mt-3 h-12 w-full rounded-xl border border-white/90 bg-white/85 px-4 text-slate-800 shadow-sm outline-none placeholder:text-slate-400 focus-visible:ring-2 focus-visible:ring-sky-300/60"
              />

              <div className="mt-2 text-right">
                <button type="button" className="text-sm font-medium text-slate-600 hover:text-slate-900">
                  Forgot password?
                </button>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="mt-4 h-12 w-full rounded-xl bg-gradient-to-b from-slate-800 to-slate-950 text-sm font-semibold text-white shadow-md transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {submitting ? "Signing in..." : "Get started"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
