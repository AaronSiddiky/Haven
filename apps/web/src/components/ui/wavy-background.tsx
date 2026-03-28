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
  waveWidth = 50,
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
    const waveColors = colors ?? DEFAULT_COLORS;

    const getSpeed = () => {
      switch (speed) {
        case "slow":
          return 0.001;
        case "fast":
          return 0.002;
        default:
          return 0.001;
      }
    };

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

    const drawWave = (n: number) => {
      nt += getSpeed();
      const lineW = waveWidth || 50;

      for (let i = 0; i < n; i++) {
        ctx.beginPath();
        ctx.lineWidth = lineW;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.strokeStyle = waveColors[i % waveColors.length];
        ctx.globalAlpha = waveOpacity;

        for (let x = 0; x <= w; x += 5) {
          const y = noise(x / 800, 0.3 * i, nt) * 100;
          const py = y + h * 0.5;
          if (x === 0) ctx.moveTo(x, py);
          else ctx.lineTo(x, py);
        }
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    };

    const render = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.filter = blur > 0 ? `blur(${blur}px)` : "none";
      ctx.globalAlpha = 1;
      ctx.fillStyle = backgroundFill;
      ctx.fillRect(0, 0, w, h);
      drawWave(5);
      raf = requestAnimationFrame(render);
    };

    resize();
    raf = requestAnimationFrame(render);

    window.addEventListener("resize", resize);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(raf);
    };
  }, [backgroundFill, blur, colors, speed, waveOpacity, waveWidth]);

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
