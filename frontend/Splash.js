// ==========================================================
// KAVACHAI Splash Screen
// Sequences: scan sweep -> shield fill -> pulse -> checkmark
// -> wordmark -> divider -> typewriter subtitle -> status dot
// Optional synthesized "scan/confirm" sound (Web Audio API,
// no external audio file needed). Sound is OFF by default
// because browsers block autoplaying audio without a user
// gesture — a speaker icon lets the person turn it on and
// replay the sequence with sound.
// ==========================================================

(function () {
  const SKIP_REPEAT_VISITS = true; // set to false to replay every page load
  const STORAGE_KEY = "kavachaiSplashShown";

  const overlay = document.getElementById("kavachai-splash");
  if (!overlay) return; // splash markup not present on this page

  // Skip entirely on repeat visits within the same browser tab session
  if (SKIP_REPEAT_VISITS && sessionStorage.getItem(STORAGE_KEY)) {
    overlay.classList.add("splash-hide");
    overlay.style.display = "none";
    return;
  }

  const shieldWrap = document.getElementById("shieldWrap");
  const shieldFill = document.getElementById("shieldFill");
  const shieldOutline = document.getElementById("shieldOutline");
  const checkMark = document.getElementById("checkMark");
  const scanLine = document.getElementById("scanLine");
  const wordmark = document.getElementById("wordmarkReveal");
  const divider = document.getElementById("dividerLine");
  const subtitleEl = document.getElementById("subtitleType");
  const statusDot = document.getElementById("statusDot");
  const skipBtn = document.getElementById("splashSkip");
  const audioToggle = document.getElementById("splashAudioToggle");

  const SUBTITLE_TEXT = "AI DOCUMENT SCREENING";

  let audioEnabled = false;
  let audioCtx = null;

  // ---- Synthesized sound (Web Audio API, no asset files) ----
  function getAudioContext() {
    if (!audioCtx) {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (Ctx) audioCtx = new Ctx();
    }
    return audioCtx;
  }

  function playTone(freq, duration, type, startGain, delay) {
    if (!audioEnabled) return;
    const ctx = getAudioContext();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type || "sine";
    osc.frequency.value = freq;

    const startTime = ctx.currentTime + (delay || 0);
    gain.gain.setValueAtTime(startGain || 0.05, startTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(startTime);
    osc.stop(startTime + duration);
  }

  function playScanSound() {
    // quick upward sweep, like a scanner beam
    playTone(220, 0.4, "sine", 0.04, 0);
    playTone(880, 0.4, "sine", 0.02, 0.05);
  }

  function playConfirmSound() {
    // short two-note "verified" blip
    playTone(660, 0.12, "triangle", 0.06, 0);
    playTone(990, 0.15, "triangle", 0.05, 0.1);
  }

  function preparePathDraw(pathEl) {
    if (!pathEl || typeof pathEl.getTotalLength !== "function") return;
    const length = pathEl.getTotalLength();
    pathEl.style.strokeDasharray = length;
    pathEl.style.strokeDashoffset = length;
    // force reflow so the browser registers the starting state
    pathEl.getBoundingClientRect();
  }

  function drawPath(pathEl) {
    if (!pathEl) return;
    pathEl.style.strokeDashoffset = 0;
  }

  function typeSubtitle(el, text, speedMs) {
    let i = 0;
    const interval = setInterval(() => {
      el.textContent = text.slice(0, i + 1);
      i++;
      if (i >= text.length) clearInterval(interval);
    }, speedMs);
  }

  function runSequence() {
    // Prep draw-on effects before animating
    preparePathDraw(shieldOutline);
    preparePathDraw(checkMark);

    // t=0: start scan line sweep + shield outline draw
    requestAnimationFrame(() => {
      scanLine.classList.add("sweep");
      drawPath(shieldOutline);
      playScanSound();
    });

    // t=350ms: shield fills with lime
    setTimeout(() => {
      shieldFill.classList.add("reveal");
    }, 350);

    // t=650ms: pulse + checkmark draws + confirm sound
    setTimeout(() => {
      shieldWrap.classList.add("pulse");
      checkMark.classList.add("reveal");
      drawPath(checkMark);
      playConfirmSound();
    }, 650);

    // t=1000ms: wordmark punches in
    setTimeout(() => {
      wordmark.classList.add("reveal");
    }, 1000);

    // t=1350ms: divider draws
    setTimeout(() => {
      divider.classList.add("reveal");
    }, 1350);

    // t=1500ms: subtitle types on
    setTimeout(() => {
      typeSubtitle(subtitleEl, SUBTITLE_TEXT, 28);
    }, 1500);

    // t=2200ms: status dot pulses
    setTimeout(() => {
      statusDot.classList.add("reveal");
    }, 2200);

    // t=3200ms: hold complete, fade out splash
    setTimeout(() => {
      hideSplash();
    }, 3200);
  }

  function hideSplash() {
    overlay.classList.add("splash-hide");
    if (SKIP_REPEAT_VISITS) {
      sessionStorage.setItem(STORAGE_KEY, "true");
    }
    // fully remove after the CSS fade transition finishes
    setTimeout(() => {
      overlay.style.display = "none";
    }, 650);
  }

  // ---- Controls ----
  skipBtn.addEventListener("click", hideSplash);

  audioToggle.addEventListener("click", () => {
    audioEnabled = !audioEnabled;
    audioToggle.textContent = audioEnabled ? "🔊" : "🔈";
    const ctx = getAudioContext();
    if (ctx && ctx.state === "suspended") {
      ctx.resume();
    }
    if (audioEnabled) {
      // give a short preview so the person knows sound is on
      playConfirmSound();
    }
  });

  runSequence();
})();