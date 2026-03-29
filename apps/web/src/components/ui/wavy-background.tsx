import { cn } from "@/lib/utils";
import { type ReactNode, useEffect, useRef } from "react";
import { createNoise3D } from "simplex-noise";

const DEFAULT_COLORS = [
  "#38bdf8",
  "#818cf8",
  "#c084fc",
  "#e879f9",
  "#22d3ee",
];

type WavyBackgroundProps = {
  children?: ReactNode;
  className?: string;
  containerClassName?: string;
  colors?: string[];
  waveWidth?: number;
  backgroundFill?: string;
  blur?: number;
  speed?: "slow" | "fast";
  waveOpacity?: number;
};

export function WavyBackground({
  children,
  className,
  containerClassName,
  colors,
  waveWidth: _waveWidth,
  backgroundFill = "black",
  blur = 10,
  speed = "fast",
  waveOpacity = 0.5,
}: WavyBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const noise = createNoise3D();
    const palette = colors ?? DEFAULT_COLORS;

    const spd = speed === "slow" ? 0.0004 : 0.001;

    let w = 0;
    let h = 0;
    let nt = 0;
    let raf = 0;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const fillWash = (
      color: string,
      alpha: number,
      baseY: number,
      amp: number,
      fxLarge: number,
      fxSmall: number,
      seed: number,
      fromTop: boolean,
    ) => {
      ctx.globalAlpha = alpha;
      ctx.fillStyle = color;
      ctx.beginPath();

      const edge = fromTop ? -100 : h + 100;
      ctx.moveTo(-100, edge);

      for (let x = -100; x <= w + 100; x += 4) {
        const n1 = noise(x / fxLarge, seed, nt);
        const n2 = noise(x / fxSmall, seed + 10, nt * 0.6);
        const y = baseY + n1 * amp + n2 * amp * 0.35;
        ctx.lineTo(x, y);
      }

      ctx.lineTo(w + 100, edge);
      ctx.closePath();
      ctx.fill();
    };

    const render = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.filter = blur > 0 ? `blur(${blur}px)` : "none";

      ctx.globalAlpha = 1;
      ctx.fillStyle = backgroundFill;
      ctx.fillRect(0, 0, w, h);

      const n = palette.length;

      for (let i = 0; i < n; i++) {
        const t = n > 1 ? i / (n - 1) : 0.5;
        const fromTop = t < 0.55;
        const baseY = h * (0.2 + t * 0.55);
        const amp = h * (0.12 + Math.sin(i * 2.1) * 0.04);
        const alpha = waveOpacity * (0.55 + Math.sin(i * 1.3 + 0.5) * 0.3);

        fillWash(
          palette[i],
          alpha,
          baseY,
          amp,
          380 + i * 90,
          140 + i * 35,
          i * 0.8,
          fromTop,
        );
      }

      // Detail / texture pass — smaller overlapping accents
      const detailCount = Math.min(n, 5);
      for (let j = 0; j < detailCount; j++) {
        const ci = (j * 2) % n;
        const t = j / detailCount;
        const fromTop = j % 2 !== 0;
        const baseY = h * (0.3 + t * 0.35);

        fillWash(
          palette[ci],
          waveOpacity * 0.22,
          baseY,
          h * 0.07,
          200 + j * 55,
          90 + j * 20,
          ci * 0.9 + 20,
          fromTop,
        );
      }

      ctx.globalAlpha = 1;
      nt += spd;
      raf = requestAnimationFrame(render);
    };

    resize();
    raf = requestAnimationFrame(render);
    window.addEventListener("resize", resize);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(raf);
    };
  }, [backgroundFill, blur, colors, speed, waveOpacity]);

  return (
    <div className={cn("relative min-h-screen w-full", containerClassName)}>
      <canvas
        ref={canvasRef}
        className="pointer-events-none fixed inset-0 z-0 h-screen w-full"
        aria-hidden
      />
      <div className={cn("relative z-10 w-full", className)}>{children}</div>
    </div>
  );
}
