import { useState } from "react";
import { AccessibilityDialog } from "@/components/AccessibilityDialog";
import { FloatingNav } from "@/components/FloatingNav";

const PRODUCT_ITEMS = [
  {
    title: "Voice-First Alerts",
    body: "Haven narrates important updates in plain language, so you can stay informed without constantly checking a screen.",
  },
  {
    title: "Real-Time Monitoring",
    body: "Track weather, traffic, and local conditions continuously. Haven surfaces what matters and filters the noise.",
  },
  {
    title: "Live Screen Share Support",
    body: "Pair your voice session with live screen share for guided help, demos, and collaborative troubleshooting.",
  },
  {
    title: "Smart Transcript Memory",
    body: "Review your full conversation history with searchable transcripts to quickly revisit decisions and action items.",
  },
];

export function Product() {
  const [a11yOpen, setA11yOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#fefefe]">
      <header className="fixed left-0 right-0 top-0 z-50">
        <FloatingNav onOpenAccessibility={() => setA11yOpen(true)} />
      </header>

      <main className="mx-auto max-w-5xl px-6 pb-20 pt-28 sm:px-10">
        <h1 className="font-serif-display text-4xl text-fg sm:text-5xl">
          Product
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-fg/70">
          Haven is built to keep you aware with less effort. It combines live
          voice assistance, contextual monitoring, and collaborative tools in a
          calm interface.
        </p>

        <section className="mt-12 grid gap-5 sm:grid-cols-2">
          {PRODUCT_ITEMS.map((item) => (
            <article
              key={item.title}
              className="rounded-3xl border border-black/[0.06] bg-white p-7 shadow-sm"
            >
              <h2 className="text-lg font-semibold text-fg">{item.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-fg/65">
                {item.body}
              </p>
            </article>
          ))}
        </section>
      </main>
      <AccessibilityDialog open={a11yOpen} onClose={() => setA11yOpen(false)} />
    </div>
  );
}
