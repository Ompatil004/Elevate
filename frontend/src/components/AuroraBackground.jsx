import React, { useEffect, useRef, useState } from 'react';

/**
 * AuroraBackground  (v3 — Theme-Aware Dual Mode)
 * ──────────────────────────────────────────────
 * Dark mode:  Original aurora mesh-gradient orbs + drifting star-field canvas + grain
 * Light mode: Warm pastel gradient background with soft glowing orbs — NO stars
 *             (stars look bad on light backgrounds)
 *
 * • Detects [data-theme] on <body> via MutationObserver — updates without full re-mount
 * • Fixed position, full viewport, z-index 0, pointer-events none
 */

/* ── Dark-mode CSS ────────────────────────────────────────────────────────── */
const DARK_CSS = `
  @keyframes auroraOrb1 {
    0%   { transform: translate(0px,   0px)   scale(1);    }
    33%  { transform: translate(70px,  -50px) scale(1.09); }
    66%  { transform: translate(-35px,  55px) scale(0.94); }
    100% { transform: translate(0px,   0px)   scale(1);    }
  }
  @keyframes auroraOrb2 {
    0%   { transform: translate(0px,  0px)    scale(1);    }
    40%  { transform: translate(-80px, 40px)  scale(1.13); }
    75%  { transform: translate(45px, -60px)  scale(0.91); }
    100% { transform: translate(0px,  0px)    scale(1);    }
  }
  @keyframes auroraOrb3 {
    0%   { transform: translate(0px,  0px)    scale(1);    }
    50%  { transform: translate(60px,  65px)  scale(1.11); }
    85%  { transform: translate(-65px,-35px)  scale(0.89); }
    100% { transform: translate(0px,  0px)    scale(1);    }
  }
  @keyframes auroraOrb4 {
    0%   { transform: translate(0px,   0px)   scale(1);    }
    30%  { transform: translate(-50px,  50px) scale(1.07); }
    70%  { transform: translate(60px,  -40px) scale(0.96); }
    100% { transform: translate(0px,   0px)   scale(1);    }
  }
  @keyframes auroraOrb5 {
    0%   { transform: translate(0px, 0px)    scale(1);    }
    45%  { transform: translate(40px, 80px)  scale(1.05); }
    80%  { transform: translate(-55px,-25px) scale(0.93); }
    100% { transform: translate(0px, 0px)    scale(1);    }
  }
  @keyframes grainShift {
    0%   { transform: translate(0, 0); }
    20%  { transform: translate(-2px, 3px); }
    40%  { transform: translate(3px, -2px); }
    60%  { transform: translate(-3px, -2px); }
    80%  { transform: translate(2px, 4px); }
    100% { transform: translate(0, 0); }
  }

  .aurora-wrapper {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
    background: #09090b;
  }

  /* Orbs */
  .aurora-orb-1 {
    position: absolute; top: -18%; left: -12%;
    width: 70vw; height: 70vw;
    max-width: 840px; max-height: 840px;
    border-radius: 50%;
    background: radial-gradient(circle at center,
      rgba(99, 102, 241, 0.26) 0%, rgba(99, 102, 241, 0.12) 38%, transparent 72%);
    filter: blur(80px);
    animation: auroraOrb1 22s ease-in-out infinite;
    will-change: transform;
  }
  .aurora-orb-2 {
    position: absolute; top: -8%; right: -14%;
    width: 60vw; height: 60vw;
    max-width: 720px; max-height: 720px;
    border-radius: 50%;
    background: radial-gradient(circle at center,
      rgba(139, 92, 246, 0.22) 0%, rgba(139, 92, 246, 0.10) 42%, transparent 74%);
    filter: blur(96px);
    animation: auroraOrb2 28s ease-in-out infinite;
    will-change: transform;
  }
  .aurora-orb-3 {
    position: absolute; bottom: -18%; right: -10%;
    width: 65vw; height: 65vw;
    max-width: 780px; max-height: 780px;
    border-radius: 50%;
    background: radial-gradient(circle at center,
      rgba(6, 182, 212, 0.20) 0%, rgba(6, 182, 212, 0.09) 44%, transparent 74%);
    filter: blur(88px);
    animation: auroraOrb3 25s ease-in-out infinite;
    will-change: transform;
  }
  .aurora-orb-4 {
    position: absolute; bottom: -12%; left: -10%;
    width: 55vw; height: 55vw;
    max-width: 660px; max-height: 660px;
    border-radius: 50%;
    background: radial-gradient(circle at center,
      rgba(16, 185, 129, 0.18) 0%, rgba(16, 185, 129, 0.08) 44%, transparent 74%);
    filter: blur(100px);
    animation: auroraOrb4 32s ease-in-out infinite;
    will-change: transform;
  }
  .aurora-orb-5 {
    position: absolute; top: 30%; left: 35%;
    width: 40vw; height: 40vw;
    max-width: 480px; max-height: 480px;
    border-radius: 50%;
    background: radial-gradient(circle at center,
      rgba(244, 63, 94, 0.10) 0%, rgba(244, 63, 94, 0.04) 44%, transparent 74%);
    filter: blur(110px);
    animation: auroraOrb5 36s ease-in-out infinite;
    will-change: transform;
  }

  .aurora-canvas {
    position: absolute; inset: 0; width: 100%; height: 100%;
  }
  .aurora-grain {
    position: absolute; inset: -50%; width: 200%; height: 200%;
    opacity: 0.032;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 180px 180px;
    animation: grainShift 0.12s steps(1) infinite;
    pointer-events: none;
  }
`;

/* ── Light-mode CSS ───────────────────────────────────────────────────────── */
const LIGHT_CSS = `
  @keyframes lightOrb1 {
    0%   { transform: translate(0px,   0px)   scale(1);    }
    40%  { transform: translate(60px, -40px)  scale(1.07); }
    80%  { transform: translate(-30px,  50px) scale(0.95); }
    100% { transform: translate(0px,   0px)   scale(1);    }
  }
  @keyframes lightOrb2 {
    0%   { transform: translate(0px,  0px)   scale(1);    }
    35%  { transform: translate(-70px, 35px) scale(1.10); }
    70%  { transform: translate(40px, -55px) scale(0.92); }
    100% { transform: translate(0px,  0px)   scale(1);    }
  }
  @keyframes lightOrb3 {
    0%   { transform: translate(0px,  0px)   scale(1);    }
    50%  { transform: translate(50px, 60px)  scale(1.08); }
    85%  { transform: translate(-60px,-30px) scale(0.90); }
    100% { transform: translate(0px,  0px)   scale(1);    }
  }
  @keyframes lightOrb4 {
    0%   { transform: translate(0px,  0px)   scale(1);    }
    45%  { transform: translate(-40px, 45px) scale(1.05); }
    80%  { transform: translate(55px, -35px) scale(0.96); }
    100% { transform: translate(0px,  0px)   scale(1);    }
  }

  .light-bg-wrapper {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
    /* Warm, premium off-white base — not stark white */
    background: #f0f0f8;
  }

  /* Very subtle cross-gradient base layer */
  .light-bg-base {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(ellipse 80% 60% at 20% 10%, rgba(224,220,255,0.55) 0%, transparent 60%),
      radial-gradient(ellipse 70% 50% at 85% 15%, rgba(209,230,255,0.50) 0%, transparent 55%),
      radial-gradient(ellipse 60% 70% at 10% 85%, rgba(220,255,240,0.40) 0%, transparent 60%),
      radial-gradient(ellipse 75% 55% at 80% 88%, rgba(255,220,240,0.35) 0%, transparent 60%);
  }

  /* Soft lavender — top-left */
  .light-orb-1 {
    position: absolute; top: -20%; left: -15%;
    width: 75vw; height: 75vw;
    max-width: 900px; max-height: 900px;
    border-radius: 50%;
    background: radial-gradient(circle at center,
      rgba(139, 92, 246, 0.14) 0%,
      rgba(139, 92, 246, 0.06) 40%,
      transparent 70%
    );
    filter: blur(90px);
    animation: lightOrb1 26s ease-in-out infinite;
    will-change: transform;
  }

  /* Soft sky-blue — top-right */
  .light-orb-2 {
    position: absolute; top: -10%; right: -18%;
    width: 65vw; height: 65vw;
    max-width: 780px; max-height: 780px;
    border-radius: 50%;
    background: radial-gradient(circle at center,
      rgba(99, 102, 241, 0.12) 0%,
      rgba(99, 102, 241, 0.05) 42%,
      transparent 72%
    );
    filter: blur(100px);
    animation: lightOrb2 32s ease-in-out infinite;
    will-change: transform;
  }

  /* Soft mint — bottom-left */
  .light-orb-3 {
    position: absolute; bottom: -20%; left: -12%;
    width: 60vw; height: 60vw;
    max-width: 720px; max-height: 720px;
    border-radius: 50%;
    background: radial-gradient(circle at center,
      rgba(16, 185, 129, 0.11) 0%,
      rgba(16, 185, 129, 0.05) 44%,
      transparent 72%
    );
    filter: blur(110px);
    animation: lightOrb3 28s ease-in-out infinite;
    will-change: transform;
  }

  /* Soft rose — bottom-right */
  .light-orb-4 {
    position: absolute; bottom: -15%; right: -10%;
    width: 55vw; height: 55vw;
    max-width: 660px; max-height: 660px;
    border-radius: 50%;
    background: radial-gradient(circle at center,
      rgba(236, 72, 153, 0.10) 0%,
      rgba(236, 72, 153, 0.04) 44%,
      transparent 70%
    );
    filter: blur(120px);
    animation: lightOrb4 35s ease-in-out infinite;
    will-change: transform;
  }

  /* Very subtle light grain */
  .light-grain {
    position: absolute; inset: -50%; width: 200%; height: 200%;
    opacity: 0.012;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 180px 180px;
    pointer-events: none;
  }
`;

/* ── Star-field canvas hook (dark mode only) ─────────────────────────────── */
function useStarfield(canvasRef, active) {
  useEffect(() => {
    if (!active) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const rand = (a, b) => Math.random() * (b - a) + a;

    const buildStars = (W, H) => {
      const stars = [];
      for (let i = 0; i < 110; i++) {
        stars.push({
          x: rand(0, W), y: rand(0, H), r: rand(0.3, 0.9),
          speed: rand(0.04, 0.10), opacity: rand(0.15, 0.40),
          opacityDir: rand(-0.002, 0.002), layer: 0, color: pickColor(),
        });
      }
      for (let i = 0; i < 70; i++) {
        stars.push({
          x: rand(0, W), y: rand(0, H), r: rand(0.8, 1.6),
          speed: rand(0.10, 0.22), opacity: rand(0.25, 0.60),
          opacityDir: rand(-0.003, 0.003), layer: 1, color: pickColor(),
        });
      }
      for (let i = 0; i < 30; i++) {
        stars.push({
          x: rand(0, W), y: rand(0, H), r: rand(1.5, 3.0),
          speed: rand(0.22, 0.40), opacity: rand(0.40, 0.85),
          opacityDir: rand(-0.004, 0.004), layer: 2,
          glow: Math.random() > 0.45, color: pickColor(),
        });
      }
      return stars;
    };

    function pickColor() {
      const palette = [
        'rgba(255,255,255,', 'rgba(165,180,252,', 'rgba(196,181,253,',
        'rgba(103,232,249,', 'rgba(167,243,208,',
      ];
      return palette[Math.floor(Math.random() * palette.length)];
    }

    let W, H, stars;
    const resize = () => {
      W = canvas.width = canvas.offsetWidth;
      H = canvas.height = canvas.offsetHeight;
      stars = buildStars(W, H);
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);

    let raf;
    let paused = false;

    const draw = () => {
      if (!paused) {
        ctx.clearRect(0, 0, W, H);
        for (const s of stars) {
          s.y -= s.speed;
          if (s.y + s.r < 0) { s.y = H + s.r; s.x = rand(0, W); }
          s.opacity += s.opacityDir;
          if (s.opacity > 0.95 || s.opacity < 0.05) s.opacityDir *= -1;
          const alpha = Math.max(0.02, Math.min(0.98, s.opacity));
          ctx.save();
          if (s.glow) {
            const grd = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 3.5);
            grd.addColorStop(0, s.color + alpha + ')');
            grd.addColorStop(1, s.color + '0)');
            ctx.beginPath(); ctx.arc(s.x, s.y, s.r * 3.5, 0, Math.PI * 2);
            ctx.fillStyle = grd; ctx.fill();
          }
          ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
          ctx.fillStyle = s.color + alpha + ')'; ctx.fill();
          ctx.restore();
        }
      }
      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);
    const vis = () => { paused = document.hidden; };
    document.addEventListener('visibilitychange', vis);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      document.removeEventListener('visibilitychange', vis);
    };
  }, [canvasRef, active]);
}

/* ── Component ───────────────────────────────────────────────────────────── */
export default function AuroraBackground() {
  const canvasRef = useRef(null);

  // Watch body[data-theme] so we re-render when user toggles theme
  const [isDark, setIsDark] = useState(
    () => document.body.getAttribute('data-theme') !== 'light'
  );

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.body.getAttribute('data-theme') !== 'light');
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ['data-theme'] });
    return () => observer.disconnect();
  }, []);

  useStarfield(canvasRef, isDark);

  if (isDark) {
    return (
      <>
        <style>{DARK_CSS}</style>
        <div className="aurora-wrapper" aria-hidden="true">
          <div className="aurora-orb-1" />
          <div className="aurora-orb-2" />
          <div className="aurora-orb-3" />
          <div className="aurora-orb-4" />
          <div className="aurora-orb-5" />
          <canvas className="aurora-canvas" ref={canvasRef} />
          <div className="aurora-grain" />
        </div>
      </>
    );
  }

  // Light mode — warm pastel gradient, NO stars
  return (
    <>
      <style>{LIGHT_CSS}</style>
      <div className="light-bg-wrapper" aria-hidden="true">
        <div className="light-bg-base" />
        <div className="light-orb-1" />
        <div className="light-orb-2" />
        <div className="light-orb-3" />
        <div className="light-orb-4" />
        <div className="light-grain" />
      </div>
    </>
  );
}
