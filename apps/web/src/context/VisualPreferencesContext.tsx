import {
  createContext,
  useCallback,
  useContext,
  useLayoutEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type TextScale = "100" | "125" | "150" | "200";

type VisualPreferences = {
  highContrast: boolean;
  setHighContrast: (v: boolean) => void;
  textScale: TextScale;
  setTextScale: (v: TextScale) => void;
  dyslexiaFont: boolean;
  setDyslexiaFont: (v: boolean) => void;
};

const STORAGE_KEY = "haven.visualPreferences.v1";

const VisualPreferencesContext = createContext<VisualPreferences | null>(null);

function readStored(): {
  highContrast: boolean;
  textScale: TextScale;
  dyslexiaFont: boolean;
} {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return { highContrast: false, textScale: "100", dyslexiaFont: false };
    }
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    const textScale =
      parsed.textScale === "125" ||
      parsed.textScale === "150" ||
      parsed.textScale === "200"
        ? parsed.textScale
        : "100";
    return {
      highContrast: Boolean(parsed.highContrast),
      textScale,
      dyslexiaFont: Boolean(parsed.dyslexiaFont),
    };
  } catch {
    return { highContrast: false, textScale: "100", dyslexiaFont: false };
  }
}

function applyDom(
  highContrast: boolean,
  textScale: TextScale,
  dyslexiaFont: boolean,
) {
  const root = document.documentElement;
  if (highContrast) {
    root.setAttribute("data-contrast", "high");
  } else {
    root.removeAttribute("data-contrast");
  }
  if (textScale === "100") {
    root.removeAttribute("data-text-scale");
  } else {
    root.setAttribute("data-text-scale", textScale);
  }
  if (dyslexiaFont) {
    root.setAttribute("data-dyslexia", "true");
  } else {
    root.removeAttribute("data-dyslexia");
  }
}

export function VisualPreferencesProvider({ children }: { children: ReactNode }) {
  const initial = readStored();
  const [highContrast, setHighContrastState] = useState(initial.highContrast);
  const [textScale, setTextScaleState] = useState<TextScale>(initial.textScale);
  const [dyslexiaFont, setDyslexiaFontState] = useState(initial.dyslexiaFont);

  useLayoutEffect(() => {
    applyDom(highContrast, textScale, dyslexiaFont);
  }, [highContrast, dyslexiaFont, textScale]);

  const persist = useCallback((next: {
    highContrast: boolean;
    textScale: TextScale;
    dyslexiaFont: boolean;
  }) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }, []);

  const setHighContrast = useCallback(
    (v: boolean) => {
      setHighContrastState(v);
      persist({ highContrast: v, textScale, dyslexiaFont });
    },
    [dyslexiaFont, persist, textScale],
  );

  const setTextScale = useCallback(
    (v: TextScale) => {
      setTextScaleState(v);
      persist({ highContrast, textScale: v, dyslexiaFont });
    },
    [dyslexiaFont, highContrast, persist],
  );

  const setDyslexiaFont = useCallback(
    (v: boolean) => {
      setDyslexiaFontState(v);
      persist({ highContrast, textScale, dyslexiaFont: v });
    },
    [highContrast, persist, textScale],
  );

  const value = useMemo(
    () => ({
      highContrast,
      setHighContrast,
      textScale,
      setTextScale,
      dyslexiaFont,
      setDyslexiaFont,
    }),
    [
      dyslexiaFont,
      highContrast,
      setDyslexiaFont,
      setHighContrast,
      setTextScale,
      textScale,
    ],
  );

  return (
    <VisualPreferencesContext.Provider value={value}>
      {children}
    </VisualPreferencesContext.Provider>
  );
}

export function useVisualPreferences() {
  const ctx = useContext(VisualPreferencesContext);
  if (!ctx) {
    throw new Error("useVisualPreferences must be used within VisualPreferencesProvider");
  }
  return ctx;
}
