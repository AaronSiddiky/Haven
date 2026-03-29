import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { signup, login, error: authError } = useAuth();
  const [revealed, setRevealed] = useState(false);

  const [mode, setMode] = useState<"signup" | "login">(
    searchParams.get("mode") === "login" ? "login" : "signup",
  );
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

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
    if (password.length < 8) {
      setFormError("Password must be at least 8 characters");
      return;
    }

    setSubmitting(true);
    try {
      if (mode === "signup") {
        await signup(email, password, name);
      } else {
        await login(email, password);
      }
      navigate("/voice");
    } catch {
      setFormError(
        authError ??
          (mode === "signup"
            ? "Sign up failed — please try again"
            : "Log in failed — check your email and password"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-[100dvh] bg-[#f3e8f4]">
      <div className="grid min-h-[100dvh] grid-cols-1 md:grid-cols-2">
        <div className="relative flex items-center justify-center bg-gradient-to-br from-[#f5e3f3] via-[#efd7ec] to-[#e8d3e8] px-4 py-20 sm:px-8">
          {/* Back to home */}
          <Link
            to="/"
            className="absolute left-5 top-5 z-20 flex items-center gap-2.5 rounded-lg py-1 text-fg/75 transition-colors hover:text-fg focus:outline-none focus-visible:ring-2 focus-visible:ring-fg/30 sm:left-8 sm:top-6"
            style={{
              opacity: revealed ? 1 : 0,
              transition: "opacity 0.8s ease 0.2s",
            }}
          >
            <span className="flex h-8 items-end gap-0.5" aria-hidden>
              {[8, 12, 5].map((h, i) => (
                <span
                  key={i}
                  className="w-[3px] rounded-sm bg-current"
                  style={{ height: `${h}px` }}
                />
              ))}
            </span>
            <span className="text-lg font-bold tracking-tight">Haven</span>
          </Link>

          {/* Form card */}
          <div
            className="relative z-10 w-full max-w-md"
            style={{
              opacity: revealed ? 1 : 0,
              transform: revealed ? "translateX(0)" : "translateX(-20px)",
              transition: "opacity 0.9s cubic-bezier(0.22,1,0.36,1) 0.3s, transform 0.9s cubic-bezier(0.22,1,0.36,1) 0.3s",
            }}
          >
            <div className="rounded-3xl border border-black/10 bg-white/45 p-6 shadow-[0_24px_64px_rgba(0,0,0,0.1)] backdrop-blur-md sm:p-10">
          <h1 className="text-xl font-semibold text-fg">
            {mode === "signup" ? "Create an account" : "Welcome back"}
          </h1>

          <form className="mt-6 flex flex-col gap-4" onSubmit={onSubmit} noValidate>
            {formError && (
              <p role="alert" className="rounded-xl bg-red-50/90 px-4 py-3 text-sm font-medium text-red-700">
                {formError}
              </p>
            )}
            {mode === "signup" && (
              <div>
                <label htmlFor="auth-name" className="block text-sm font-medium text-fg">
                  Name
                </label>
                <input
                  id="auth-name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="mt-2 w-full min-h-11 rounded-2xl border border-white/30 bg-white/50 px-4 text-fg placeholder:text-fg/35 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/50"
                  placeholder="Jane Doe"
                />
              </div>
            )}
            <div>
              <label htmlFor="auth-email" className="block text-sm font-medium text-fg">
                Email
              </label>
              <input
                id="auth-email"
                name="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-2 w-full min-h-11 rounded-2xl border border-white/30 bg-white/50 px-4 text-fg placeholder:text-fg/35 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/50"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label htmlFor="auth-password" className="block text-sm font-medium text-fg">
                Password
              </label>
              <input
                id="auth-password"
                name="password"
                type="password"
                autoComplete={mode === "signup" ? "new-password" : "current-password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-2 w-full min-h-11 rounded-2xl border border-white/30 bg-white/50 px-4 text-fg placeholder:text-fg/35 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/50"
                placeholder={mode === "signup" ? "At least 8 characters" : "Your password"}
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="mt-2 inline-flex min-h-11 w-full items-center justify-center rounded-2xl bg-fg px-6 text-sm font-semibold text-white transition hover:bg-fg/85 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/50 disabled:opacity-50"
            >
              {submitting
                ? mode === "signup" ? "Signing up…" : "Logging in…"
                : mode === "signup" ? "Sign up" : "Log in"}
            </button>
          </form>
          <p className="mt-5 text-center text-sm text-fg/50">
            {mode === "signup" ? (
              <>
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => { setMode("login"); setFormError(null); }}
                  className="font-medium text-fg underline underline-offset-2"
                >
                  Log in
                </button>
              </>
            ) : (
              <>
                Don&apos;t have an account?{" "}
                <button
                  type="button"
                  onClick={() => { setMode("signup"); setFormError(null); }}
                  className="font-medium text-fg underline underline-offset-2"
                >
                  Sign up
                </button>
              </>
            )}
          </p>
            </div>
          </div>
        </div>

        <div className="relative hidden md:block">
          <img
            src="/Haven login 3.png"
            alt="Soft marsh landscape at sunset"
            className="h-full w-full object-cover object-center"
            style={{
              opacity: revealed ? 1 : 0,
              transform: revealed ? "scale(1)" : "scale(1.03)",
              transition: "opacity 1s cubic-bezier(0.22,1,0.36,1) 0.15s, transform 1.2s cubic-bezier(0.22,1,0.36,1) 0.15s",
            }}
          />
        </div>
      </div>
    </div>
  );
}
