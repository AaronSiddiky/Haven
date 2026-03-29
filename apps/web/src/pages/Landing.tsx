import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { AccessibilityDialog } from "../components/AccessibilityDialog";
import { FloatingNav } from "../components/FloatingNav";
import { SkipLink } from "../components/SkipLink";

const FEATURES = [
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-6 w-6">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
      </svg>
    ),
    title: "Voice-first alerts",
    description: "Hear what matters in plain language. No screens to check, no notifications to read — just a calm voice keeping you informed.",
  },
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-6 w-6">
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.64 0 8.577 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.64 0-8.577-3.007-9.963-7.178Z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
      </svg>
    ),
    title: "Watches your world",
    description: "Haven monitors your environment in real time — weather shifts, traffic changes, breaking news, and hazards nearby.",
  },
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-6 w-6">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
      </svg>
    ),
    title: "Danger detection",
    description: "Severe weather, road closures, air quality alerts — Haven tells you before you need to ask.",
  },
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-6 w-6">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
      </svg>
    ),
    title: "Context-aware intelligence",
    description: "It learns what you care about and filters the noise. Only the updates that matter reach you.",
  },
];

export function Landing() {
  const [a11yOpen, setA11yOpen] = useState(false);
  const featuresRef = useRef<HTMLElement>(null);
  const [featuresVisible, setFeaturesVisible] = useState(false);

  useEffect(() => {
    const el = featuresRef.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setFeaturesVisible(true);
          io.disconnect();
        }
      },
      { rootMargin: "-5% 0px -5% 0px", threshold: 0.1 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div className="relative min-h-screen w-full">
      <SkipLink />

      <header className="fixed left-0 right-0 top-0 z-50">
        <FloatingNav onOpenAccessibility={() => setA11yOpen(true)} />
      </header>

      <main id="main" className="relative w-full">
        {/* Section 1 — hero */}
        <section
          aria-labelledby="hero-heading"
          className="relative h-[100dvh] overflow-hidden bg-[#fefefe]"
        >
          <img
            src="/Haven background 2.png"
            alt=""
            aria-hidden="true"
            className="absolute bottom-0 left-0 h-auto w-full"
          />
          <div className="relative z-10 flex h-full flex-col items-center justify-center px-6">
            <div className="w-full max-w-3xl text-center">
              <h1
                id="hero-heading"
                className="font-serif-display text-[clamp(2.75rem,8vw,5.5rem)] font-normal leading-[1.05] tracking-tight text-[#1a1025] drop-shadow-[0_1px_2px_rgba(255,255,255,0.5)]"
              >
                Hear more,
                <br />
                Worry less.
              </h1>
              <p className="mx-auto mt-8 max-w-xl text-pretty text-base leading-relaxed text-[#2a2a2a] sm:text-lg">
                Increasing internet access for people with vision and motor impairments from young to old.

              </p>
              <div className="mt-10">
                <Link
                  to="/login"
                  className="inline-flex min-h-[3rem] items-center justify-center rounded-full bg-[#1a1025] px-10 text-base font-semibold text-white shadow-md transition duration-200 hover:bg-[#1a1025]/85 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue focus-visible:ring-offset-2"
                >
                  Get started
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Section 2 — product features */}
        <section
          ref={featuresRef}
          aria-labelledby="features-heading"
          className="bg-[#fefefe] px-6 py-24 sm:px-10 sm:py-32"
        >
          <div className="mx-auto max-w-5xl">
            <h2
              id="features-heading"
              className="font-serif-display text-center text-3xl font-normal leading-tight text-fg sm:text-4xl"
            >
              Awareness without effort
            </h2>
            <p className="mx-auto mt-5 max-w-2xl text-center text-base leading-relaxed text-[#555] sm:text-lg">
              Haven runs quietly in the background, turning the chaos of your
              environment into clear, spoken updates.
            </p>

            <div className="mt-16 grid gap-6 sm:grid-cols-2">
              {FEATURES.map((f, i) => (
                <div
                  key={f.title}
                  className={`rounded-3xl border border-black/[0.06] bg-white p-8 shadow-sm transition-all duration-700 ease-out ${
                    featuresVisible
                      ? "translate-y-0 opacity-100"
                      : "translate-y-8 opacity-0"
                  }`}
                  style={{ transitionDelay: featuresVisible ? `${i * 120}ms` : "0ms" }}
                >
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#f0ecf5] text-[#6b5b8a]">
                    {f.icon}
                  </div>
                  <h3 className="mt-5 text-lg font-semibold text-fg">{f.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-[#555]">
                    {f.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Section 3 — closing */}
        <section
          aria-labelledby="value-heading"
          className="flex min-h-[60dvh] items-center bg-[#1a1025] px-6 py-20 text-white sm:px-10 sm:py-28"
        >
          <div className="mx-auto max-w-3xl text-center">
            <h2
              id="value-heading"
              className="font-serif-display text-balance text-3xl font-normal leading-tight sm:text-4xl md:text-[2.75rem]"
            >
              Awareness that keeps
              <br />
              pace with your day
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-pretty text-base leading-relaxed text-[#b8a9d4] sm:text-lg">
              Haven watches for what matters — updates, hazards, and changes
              in your environment — while you stay focused on living.
            </p>
            <div className="mt-10">
              <Link
                to="/login"
                className="inline-flex min-h-[3rem] items-center justify-center rounded-full border border-white/20 bg-white/10 px-10 text-base font-semibold text-white backdrop-blur-sm transition duration-200 hover:bg-white/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue focus-visible:ring-offset-2 focus-visible:ring-offset-[#1a1025]"
              >
                Get started free
              </Link>
            </div>
          </div>
        </section>
      </main>
      <AccessibilityDialog open={a11yOpen} onClose={() => setA11yOpen(false)} />
    </div>
  );
}
