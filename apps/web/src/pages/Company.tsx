import { useState } from "react";
import { AccessibilityDialog } from "@/components/AccessibilityDialog";
import { FloatingNav } from "@/components/FloatingNav";

export function Company() {
  const [a11yOpen, setA11yOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#fefefe]">
      <header className="fixed left-0 right-0 top-0 z-50">
        <FloatingNav onOpenAccessibility={() => setA11yOpen(true)} />
      </header>

      <main className="mx-auto max-w-5xl px-6 pb-20 pt-28 sm:px-10">
        <h1 className="font-serif-display text-4xl text-fg sm:text-5xl">
          Company
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-fg/70">
          We are building Haven to make everyday awareness more human. Our team
          focuses on dependable voice experiences that help people stay informed
          while staying present.
        </p>

        <section className="mt-12 grid gap-6 sm:grid-cols-2">
          <article className="rounded-3xl border border-black/[0.06] bg-white p-7 shadow-sm">
            <h2 className="text-lg font-semibold text-fg">Mission</h2>
            <p className="mt-2 text-sm leading-relaxed text-fg/65">
              Deliver clear, timely, and trustworthy updates through voice so
              people can make better decisions with less friction.
            </p>
          </article>

          <article className="rounded-3xl border border-black/[0.06] bg-white p-7 shadow-sm">
            <h2 className="text-lg font-semibold text-fg">What We Value</h2>
            <p className="mt-2 text-sm leading-relaxed text-fg/65">
              Accessibility, reliability, and privacy are foundational. We
              design for clarity first and avoid noisy, attention-hijacking UX.
            </p>
          </article>

          <article className="rounded-3xl border border-black/[0.06] bg-white p-7 shadow-sm">
            <h2 className="text-lg font-semibold text-fg">Our Team</h2>
            <p className="mt-2 text-sm leading-relaxed text-fg/65">
              We are a small product and engineering team with backgrounds in
              AI, voice interfaces, and human-centered design.
            </p>
          </article>

          <article className="rounded-3xl border border-black/[0.06] bg-white p-7 shadow-sm">
            <h2 className="text-lg font-semibold text-fg">Get in Touch</h2>
            <p className="mt-2 text-sm leading-relaxed text-fg/65">
              For partnerships, support, or feedback, contact us at
              hello@haven.example. We would love to hear how you use Haven.
            </p>
          </article>
        </section>
      </main>
      <AccessibilityDialog open={a11yOpen} onClose={() => setA11yOpen(false)} />
    </div>
  );
}
