import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AccessibilityDialog } from "../components/AccessibilityDialog";
import { FloatingNav } from "../components/FloatingNav";
import { SkipLink } from "../components/SkipLink";
import { WavyBackground } from "@/components/ui/wavy-background";

const HAVEN_WAVE_COLORS = ["#c4c4c4", "#b8b8b8", "#d0d0d0", "#bcbcbc", "#a8a8a8"];

export function Landing() {
  const navigate = useNavigate();
  const [a11yOpen, setA11yOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    navigate("/voice");
  }

  return (
    <WavyBackground
      blur={0}
      waveWidth={3}
      speed="slow"
      waveOpacity={0.72}
      backgroundFill="#fdfcf5"
      colors={HAVEN_WAVE_COLORS}
      containerClassName="min-h-screen w-full"
      className="flex w-full flex-col pb-24"
    >
      <SkipLink />

      {/* Stays pinned under the top edge while you scroll */}
      <header className="sticky top-4 z-50 w-full px-4 sm:px-6">
        <FloatingNav onOpenAccessibility={() => setA11yOpen(true)} />
      </header>

      <main id="main" className="mx-auto mt-8 w-full max-w-6xl px-4 sm:mt-10 sm:px-6">
        <section
          aria-labelledby="hero-heading"
          className="floating-hero mx-auto max-w-3xl rounded-3xl border border-fg/8 bg-white/95 px-6 py-16 text-center shadow-[0_8px_40px_rgba(0,0,0,0.07)] backdrop-blur-sm sm:px-12 sm:py-20 md:py-24"
        >
          <h1
            id="hero-heading"
            className="font-serif-display mx-auto max-w-3xl text-balance text-[clamp(2.25rem,6vw,4rem)] font-semibold leading-[1.08] tracking-tight"
          >
            <span className="text-hero-split">Don&apos;t watch,</span>{" "}
            <span className="font-bold text-fg">just listen.</span>
          </h1>
          <p className="mx-auto mt-8 max-w-lg text-pretty text-base font-bold leading-relaxed text-fg sm:max-w-xl sm:text-lg">
            Voice alerts when your world changes. OpenClaw watches for updates and
            danger—you hear what matters, in plain language.
          </p>
          <div className="mt-10">
            <a
              href="#sign-in"
              className="inline-flex min-h-[3rem] items-center justify-center rounded-full border border-fg bg-lavender px-10 text-base font-semibold text-fg shadow-sm transition duration-200 hover:bg-lavender-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue focus-visible:ring-offset-2 focus-visible:ring-offset-white"
            >
              Get started
            </a>
          </div>
        </section>

        <section
          id="sign-in"
          aria-labelledby="sign-in-heading"
          className="glass-panel mx-auto mt-10 max-w-xl p-6 sm:mt-12 sm:p-8"
        >
          <h2 id="sign-in-heading" className="text-base font-semibold text-fg">
            Sign in
          </h2>
          <p className="mt-1 text-sm text-muted">
            Design preview — no server. Continue to open the listening screen.
          </p>
          <form className="mt-6 flex flex-col gap-4" onSubmit={onSubmit} noValidate>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-fg">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-2 w-full min-h-11 rounded-2xl border border-glass-border bg-white/90 px-4 text-fg placeholder:text-muted/60 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-fg">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-2 w-full min-h-11 rounded-2xl border border-glass-border bg-white/90 px-4 text-fg placeholder:text-muted/60 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit"
              className="mt-2 inline-flex min-h-11 w-full items-center justify-center rounded-2xl border border-fg bg-lavender px-6 text-sm font-semibold text-fg transition hover:bg-lavender-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
            >
              Continue
            </button>
          </form>
        </section>
      </main>

      <AccessibilityDialog open={a11yOpen} onClose={() => setA11yOpen(false)} />
    </WavyBackground>
  );
}
