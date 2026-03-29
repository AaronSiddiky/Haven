import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

type Props = {
  onOpenAccessibility: () => void;
};

export function FloatingNav({ onOpenAccessibility }: Props) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const check = () => setScrolled(window.scrollY > window.innerHeight - 80);
    check();
    window.addEventListener("scroll", check, { passive: true });
    return () => window.removeEventListener("scroll", check);
  }, []);

  return (
    <nav
      className="flex items-center justify-between px-6 py-4 sm:px-10"
      style={{
        backgroundColor: scrolled ? "rgba(255,255,255,0.75)" : "transparent",
        backdropFilter: scrolled ? "blur(20px)" : "blur(0px)",
        WebkitBackdropFilter: scrolled ? "blur(20px)" : "blur(0px)",
        borderBottom: scrolled ? "1px solid rgba(0,0,0,0.06)" : "1px solid transparent",
        transition: "background-color 0.5s ease, backdrop-filter 0.5s ease, -webkit-backdrop-filter 0.5s ease, border-bottom-color 0.5s ease",
      }}
      aria-label="Primary"
    >
      {/* Left — logo */}
      <Link
        to="/"
        className="flex shrink-0 items-center gap-2.5 rounded-lg py-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
      >
        <span className="flex h-8 items-end gap-0.5" aria-hidden>
          {[8, 12, 5].map((h, i) => (
            <span
              key={i}
              className="w-[3px] rounded-sm bg-fg"
              style={{ height: `${h}px` }}
            />
          ))}
        </span>
        <span className="text-lg font-bold tracking-tight text-fg">Haven</span>
      </Link>

      {/* Center — nav links */}
      <div className="hidden items-center gap-8 sm:flex">
        <a
          href="#product"
          className="text-sm font-medium text-fg/60 transition-colors hover:text-fg"
        >
          Product
        </a>
        <a
          href="#company"
          className="text-sm font-medium text-fg/60 transition-colors hover:text-fg"
        >
          Company
        </a>
        <button
          type="button"
          onClick={onOpenAccessibility}
          className="rounded text-sm font-medium text-fg/60 transition-colors hover:text-fg focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue focus-visible:ring-offset-2"
        >
          Accessibility
        </button>
      </div>

      {/* Right — login */}
      <Link
        to="/login"
        className="min-h-9 rounded-full border border-fg/15 bg-white/60 px-5 py-1.5 text-sm font-medium text-fg backdrop-blur-sm transition-colors hover:border-fg/30 hover:bg-white/80 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
      >
        Get started
      </Link>
    </nav>
  );
}
