import { EXIT_HYSTERESIS } from './repCounterMachine';

export const drawSkeleton = (ctx, raw, mainColor) => {
  const { l_sh, r_sh, l_el, r_el, l_wr, r_wr, l_hi, r_hi, l_kn, r_kn, l_an, r_an } = raw;

  ctx.lineWidth = 4;
  ctx.strokeStyle = mainColor;
  ctx.shadowColor = mainColor;
  ctx.shadowBlur = 6;

  const drawLine = (a, b) => {
    if (a.v > 0.1 && b.v > 0.1) {
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
    }
  };

  drawLine(l_sh, r_sh); drawLine(l_hi, r_hi);
  drawLine(l_sh, l_hi); drawLine(r_sh, r_hi);
  drawLine(l_sh, l_el); drawLine(l_el, l_wr);
  drawLine(r_sh, r_el); drawLine(r_el, r_wr);
  drawLine(l_hi, l_kn); drawLine(l_kn, l_an);
  drawLine(r_hi, r_kn); drawLine(r_kn, r_an);

  ctx.shadowBlur = 0;
};

export const drawAngleArc = (ctx, a, b, c, angle, label, isPrimary = false, effectiveUp = 0, effectiveDown = 0) => {
  if (a.v < 0.1 || b.v < 0.1 || c.v < 0.1) return;
  const radius = 25;
  const startAng = Math.atan2(a.y - b.y, a.x - b.x);
  const endAng   = Math.atan2(c.y - b.y, c.x - b.x);

  let arcColor = '#22c55e';
  let textColor = '#4ade80';

  if (isPrimary && effectiveUp !== effectiveDown) {
    const extended = Math.max(effectiveUp, effectiveDown);
    const contracted = Math.min(effectiveUp, effectiveDown);
    if (angle > extended + 15 || angle < contracted - 15) {
      arcColor = '#ef4444';
      textColor = '#f87171';
    } else if (angle > extended + EXIT_HYSTERESIS || angle < contracted - EXIT_HYSTERESIS) {
      arcColor = '#f59e0b';
      textColor = '#fbbf24';
    } else {
      arcColor = '#3b82f6';
      textColor = '#60a5fa';
    }
  } else {
    arcColor = angle < 90 ? '#ef4444' : angle < 140 ? '#f59e0b' : '#22c55e';
    textColor = angle < 90 ? '#f87171' : angle < 140 ? '#fbbf24' : '#4ade80';
  }

  // Arc
  ctx.beginPath();
  ctx.arc(b.x, b.y, radius, startAng, endAng, false);
  ctx.strokeStyle = arcColor;
  ctx.lineWidth = 2;
  ctx.stroke();

  // Text background
  const tx = b.x + 15;
  const ty = b.y - 15;
  const text = `${label}: ${Math.round(angle)}°`;
  ctx.font = 'bold 13px monospace';
  const metrics = ctx.measureText(text);
  ctx.fillStyle = 'rgba(0,0,0,0.6)';
  ctx.fillRect(tx - 2, ty - 12, metrics.width + 6, 16);
  ctx.fillStyle = textColor;
  ctx.fillText(text, tx, ty);
};

export const drawExerciseAngles = (ctx, pattern, raw, angles, effectiveUp, effectiveDown) => {
  const { l_sh, r_sh, l_el, r_el, l_wr, r_wr, l_hi, r_hi, l_kn, r_kn, l_an, r_an } = raw;
  const { leftElbow, rightElbow, leftKnee, rightKnee, leftHip, rightHip, leftShoulder, rightShoulder } = angles;

  const arc = (a, b, c, angle, label, isPrimary = false) => {
    drawAngleArc(ctx, a, b, c, angle, label, isPrimary, effectiveUp, effectiveDown);
  };

  const showAngles = {
    CURL:    () => { arc(l_sh, l_el, l_wr, leftElbow, 'L Elbow', true); arc(r_sh, r_el, r_wr, rightElbow, 'R Elbow', true); },
    PRESS:   () => { arc(l_sh, l_el, l_wr, leftElbow, 'L Elbow', true); arc(r_sh, r_el, r_wr, rightElbow, 'R Elbow', true); },
    PULL:    () => { arc(l_sh, l_el, l_wr, leftElbow, 'L Elbow', true); arc(r_sh, r_el, r_wr, rightElbow, 'R Elbow', true); },
    SQUAT:   () => { arc(l_hi, l_kn, l_an, leftKnee, 'L Knee', true); arc(r_hi, r_kn, r_an, rightKnee, 'R Knee', true); arc(l_sh, l_hi, l_kn, leftHip, 'L Hip'); },
    HINGE:   () => { arc(l_sh, l_hi, l_kn, leftHip, 'L Hip', true); arc(r_sh, r_hi, r_kn, rightHip, 'R Hip', true); },
    LUNGE:   () => { arc(l_hi, l_kn, l_an, leftKnee, 'L Knee', true); arc(r_hi, r_kn, r_an, rightKnee, 'R Knee', true); },
    RAISE:   () => { arc(l_hi, l_sh, l_el, leftShoulder, 'L Shoulder', true); arc(r_hi, r_sh, r_el, rightShoulder, 'R Shoulder', true); },
    CORE:    () => { arc(l_sh, l_hi, l_kn, leftHip, 'L Hip', true); arc(r_sh, r_hi, r_kn, rightHip, 'R Hip', true); },
    CALF:    () => { arc(l_hi, l_kn, l_an, leftKnee, 'L Knee'); },
  };

  (showAngles[pattern] || (() => {
    arc(l_sh, l_el, l_wr, leftElbow, 'L Elbow');
    arc(r_sh, r_el, r_wr, rightElbow, 'R Elbow');
    arc(l_hi, l_kn, l_an, leftKnee, 'L Knee');
    arc(r_hi, r_kn, r_an, rightKnee, 'R Knee');
  }))();
};

export const drawJointNodes = (ctx, raw, mainColor) => {
  const { l_sh, r_sh, l_el, r_el, l_wr, r_wr, l_hi, r_hi, l_kn, r_kn, l_an, r_an } = raw;
  const nodes = [l_sh, r_sh, l_el, r_el, l_wr, r_wr, l_hi, r_hi, l_kn, r_kn, l_an, r_an];
  for (const n of nodes) {
    if (n.v > 0.1) {
      ctx.beginPath();
      ctx.arc(n.x, n.y, 7, 0, 2 * Math.PI);
      const grad = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, 7);
      grad.addColorStop(0, '#fff');
      grad.addColorStop(1, mainColor);
      ctx.fillStyle = grad;
      ctx.fill();
      ctx.strokeStyle = mainColor;
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  }
};

export const drawGaugeHud = (ctx, s, canvas, effectiveUp, effectiveDown, mainColor) => {
  // Draw massive progress ring for visual coaching
  if (s.lastTrackAngle && effectiveUp !== effectiveDown) {
    const extended = Math.max(effectiveUp, effectiveDown);
    const contracted = Math.min(effectiveUp, effectiveDown);
    let progress = (extended - s.lastTrackAngle) / (extended - contracted);
    progress = Math.max(0, Math.min(1, progress));
    
    // Draw the ring (canvas is mirrored horizontally, so drawing at x=60 renders it on the right)
    const cx = 60;
    const cy = 60;
    const r = 40;
    
    // Background ring
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, 2 * Math.PI);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 10;
    ctx.stroke();
    
    // Progress ring
    ctx.beginPath();
    ctx.arc(cx, cy, r, -Math.PI / 2, (-Math.PI / 2) + (2 * Math.PI * progress), false);
    ctx.strokeStyle = mainColor;
    ctx.lineWidth = 10;
    ctx.lineCap = 'round';
    ctx.stroke();
    
    // Text inside ring
    ctx.font = 'bold 18px Inter, sans-serif';
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${Math.round(progress * 100)}%`, cx, cy);
  }

  // Reset text alignment for other UI
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';

  const stageLabel = s.stage === 'rest' ? 'READY' : s.stage === 'contracting' ? '⬇ DOWN' : '⬆ UP';
  const stageColor = s.stage === 'rest' ? '#a1a1aa' : s.stage === 'contracting' ? '#f59e0b' : '#22c55e';
  ctx.font = 'bold 14px Inter, sans-serif';
  ctx.fillStyle = 'rgba(0,0,0,0.5)';
  ctx.fillRect(10, canvas.height - 35, 80, 25);
  ctx.fillStyle = stageColor;
  ctx.fillText(stageLabel, 18, canvas.height - 17);
};
