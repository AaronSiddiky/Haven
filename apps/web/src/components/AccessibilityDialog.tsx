import { useCallback, useEffect, useId, useRef, useState } from "react";
import {
  useVisualPreferences,
  type TextScale,
} from "../context/VisualPreferencesContext";

type TabId = "visual" | "audio";

const TEXT_SCALES: TextScale[] = ["100", "125", "150", "200"];

type Props = {
  open: boolean;
  onClose: () => void;
};

export function AccessibilityDialog({ open, onClose }: Props) {
  const titleId = useId();
  const panelId = useId();
  const dialogRef = useRef<HTMLDivElement>(null);
  const lastFocusRef = useRef<HTMLElement | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>("visual");

  const {
    highContrast,
    setHighContrast,
    textScale,
    setTextScale,
    dyslexiaFont,
    setDyslexiaFont,
  } = useVisualPreferences();

  useEffect(() => {
    if (!open) return;
    lastFocusRef.current = document.activeElement as HTMLElement;
    const node = dialogRef.current;
    const focusable = node?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
    focusable?.[0]?.focus();

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
        return;
      }
      if (e.key !== "Tab" || !node) return;
      const list = Array.from(
        node.querySelectorAll<HTMLElement>(
          'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ),
      ).filter((el) => el.offsetParent !== null || el === document.activeElement);
      if (list.length === 0) return;
      const first = list[0];
      const last = list[list.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      lastFocusRef.current?.focus?.();
    };
  }, [onClose, open]);

  const onTabKeyDown = useCallback(
    (e: React.KeyboardEvent, tab: TabId) => {
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
        e.preventDefault();
        setActiveTab(tab === "visual" ? "audio" : "visual");
      }
    },
    [],
  );

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="presentation"
    >
      <button
        type="button"
        aria-label="Close accessibility settings"
        className="absolute inset-0 bg-black/60 backdrop-blur-sm motion-safe:transition-opacity"
        onClick={onClose}
      />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="glass-panel relative z-10 w-full max-w-lg p-6 shadow-2xl"
      >
        <div className="flex items-start justify-between gap-4">
          <h2 id={titleId} className="text-lg font-semibold text-fg">
            Accessibility
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="min-h-11 min-w-11 rounded-full border border-glass-border text-muted motion-safe:transition hover:border-fg/30 hover:text-fg focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
          >
            <span className="sr-only">Close</span>
            <span aria-hidden>×</span>
          </button>
        </div>

        <div
          role="tablist"
          aria-label="Accessibility categories"
          className="mt-6 flex gap-2 border-b border-glass-border pb-3"
        >
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "visual"}
            aria-controls={`${panelId}-visual`}
            id={`${panelId}-tab-visual`}
            tabIndex={activeTab === "visual" ? 0 : -1}
            onClick={() => setActiveTab("visual")}
            onKeyDown={(e) => onTabKeyDown(e, "visual")}
            className={`rounded-full px-4 py-2 text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue ${
              activeTab === "visual"
                ? "bg-fg/10 text-fg"
                : "text-muted hover:text-fg"
            }`}
          >
            Visual accessibility
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "audio"}
            aria-controls={`${panelId}-audio`}
            id={`${panelId}-tab-audio`}
            tabIndex={activeTab === "audio" ? 0 : -1}
            onClick={() => setActiveTab("audio")}
            onKeyDown={(e) => onTabKeyDown(e, "audio")}
            className={`rounded-full px-4 py-2 text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue ${
              activeTab === "audio"
                ? "bg-fg/10 text-fg"
                : "text-muted hover:text-fg"
            }`}
          >
            Audio
          </button>
        </div>

        <div className="mt-5">
          {activeTab === "visual" ? (
            <div
              role="tabpanel"
              id={`${panelId}-visual`}
              aria-labelledby={`${panelId}-tab-visual`}
              className="flex flex-col gap-6"
            >
              <p className="text-sm text-muted">
                Adjust how Haven looks. Changes apply immediately and are saved in this
                browser.
              </p>

              <label className="flex cursor-pointer items-center justify-between gap-4 rounded-2xl border border-glass-border bg-fg/[0.04] px-4 py-3">
                <span className="text-sm font-medium text-fg">High contrast</span>
                <input
                  type="checkbox"
                  checked={highContrast}
                  onChange={(e) => setHighContrast(e.target.checked)}
                  className="h-5 w-5 rounded border-glass-border text-accent-blue focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
                />
              </label>

              <fieldset className="rounded-2xl border border-glass-border bg-fg/[0.04] px-4 py-3">
                <legend className="px-1 text-sm font-medium text-fg">Text size</legend>
                <div className="mt-3 flex flex-wrap gap-2">
                  {TEXT_SCALES.map((step) => (
                    <button
                      key={step}
                      type="button"
                      onClick={() => setTextScale(step)}
                      className={`min-h-11 rounded-full px-4 text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue ${
                        textScale === step
                          ? "bg-accent-blue text-white"
                          : "border border-glass-border text-muted hover:text-fg"
                      }`}
                    >
                      {step}%
                    </button>
                  ))}
                </div>
              </fieldset>

              <label className="flex cursor-pointer items-center justify-between gap-4 rounded-2xl border border-glass-border bg-fg/[0.04] px-4 py-3">
                <span className="text-sm font-medium text-fg">Dyslexia-friendly font</span>
                <input
                  type="checkbox"
                  checked={dyslexiaFont}
                  onChange={(e) => setDyslexiaFont(e.target.checked)}
                  className="h-5 w-5 rounded border-glass-border text-accent-blue focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
                />
              </label>

              <p className="text-xs text-muted">
                We use semantic HTML and keyboard-friendly controls. Decorative graphics are
                hidden from screen readers.
              </p>
            </div>
          ) : (
            <div
              role="tabpanel"
              id={`${panelId}-audio`}
              aria-labelledby={`${panelId}-tab-audio`}
            >
              <p className="text-sm text-muted">
                Audio preferences for voice alerts will appear here. This is a preview
                layout only.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
