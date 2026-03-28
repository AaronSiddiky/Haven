type Props = {
  onOpenAccessibility: () => void;
};

function ChevronDown({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      aria-hidden
    >
      <path
        d="M3 4.5L6 7.5L9 4.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function FloatingNav({ onOpenAccessibility }: Props) {
  return (
    <nav
      className="floating-nav mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 rounded-full border border-fg/10 bg-white px-4 py-2.5 shadow-[0_4px_24px_rgba(0,0,0,0.08)] sm:gap-4 sm:px-6 sm:py-3"
      aria-label="Primary"
    >
      <a
        href="/"
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
      </a>

      <div className="hidden items-center gap-7 lg:flex">
        {(
          [
            ["Product", true],
            ["Individuals", true],
            ["Business", false],
            ["Resources", true],
          ] as const
        ).map(([label, hasChevron]) => (
          <a
            key={label}
            href="#"
            className="flex items-center gap-1 text-sm font-medium text-fg hover:opacity-70 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue focus-visible:ring-offset-2 focus-visible:ring-offset-canvas"
            onClick={(e) => e.preventDefault()}
          >
            {label}
            {hasChevron ? <ChevronDown className="opacity-50" /> : null}
          </a>
        ))}
      </div>

      <div className="flex flex-wrap items-center justify-end gap-2 sm:gap-3">
        <button
          type="button"
          onClick={onOpenAccessibility}
          className="min-h-10 rounded-full border border-fg/20 bg-transparent px-4 text-sm font-medium text-fg hover:border-fg/35 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
        >
          Accessibility
        </button>
        <span className="hidden h-6 w-px bg-fg/10 sm:block" aria-hidden />
        <a
          href="#sign-in"
          className="inline-flex min-h-10 items-center justify-center rounded-full border border-fg bg-transparent px-4 text-sm font-medium text-fg hover:bg-fg/[0.03] focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
        >
          Log in
        </a>
        <a
          href="#sign-in"
          className="inline-flex min-h-10 items-center justify-center rounded-full border border-fg bg-lavender px-4 text-sm font-semibold text-fg hover:bg-lavender-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
        >
          Get started
        </a>
      </div>
    </nav>
  );
}
