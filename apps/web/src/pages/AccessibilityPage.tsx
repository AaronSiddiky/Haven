import { useState } from "react";
import { AccessibilityDialog } from "@/components/AccessibilityDialog";
import { FloatingNav } from "@/components/FloatingNav";

export function AccessibilityPage() {
  const [a11yOpen, setA11yOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#fefefe]">
      <header className="fixed left-0 right-0 top-0 z-50">
        <FloatingNav onOpenAccessibility={() => setA11yOpen(true)} />
      </header>

      <main className="mx-auto max-w-5xl px-6 pb-20 pt-28 sm:px-10">
        <h1 className="font-serif-display text-4xl text-fg sm:text-5xl">
          Accessibility
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-fg/70">
          Haven is designed to be usable by as many people as possible. We
          continuously improve keyboard navigation, readability, and visual
          comfort options.
        </p>

        <section className="mt-12 space-y-5">
          <article className="rounded-3xl border border-black/[0.06] bg-white p-7 shadow-sm">
            <h2 className="text-lg font-semibold text-fg">Built-In Options</h2>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-sm leading-relaxed text-fg/65">
              <li>Text scale controls for improved readability</li>
              <li>High-contrast mode for stronger visual separation</li>
              <li>Dyslexia-friendly font toggle</li>
              <li>Keyboard focus rings and skip-link support</li>
            </ul>
          </article>

          <article className="rounded-3xl border border-black/[0.06] bg-white p-7 shadow-sm">
            <h2 className="text-lg font-semibold text-fg">Standards</h2>
            <p className="mt-2 text-sm leading-relaxed text-fg/65">
              We aim to align with WCAG 2.1 AA guidance and regularly review
              interactions for color contrast, focus visibility, and semantic
              structure.
            </p>
          </article>

          <article className="rounded-3xl border border-black/[0.06] bg-white p-7 shadow-sm">
            <h2 className="text-lg font-semibold text-fg">Report an Issue</h2>
            <p className="mt-2 text-sm leading-relaxed text-fg/65">
              If you encounter an accessibility issue, email
              accessibility@haven.example with steps to reproduce and your setup
              details. We prioritize these reports.
            </p>
          </article>
        </section>
      </main>
      <AccessibilityDialog open={a11yOpen} onClose={() => setA11yOpen(false)} />
    </div>
  );
}
