async (page) => {
  const pause = page.locator("#btn-pause");
  if (!(await pause.evaluate((el) => el.classList.contains("active")))) {
    throw new Error("NOT_PAUSED_BEFORE_FAST_CHUNK");
  }

  await page.locator("#btn-fast").click();
  await page.waitForTimeout(3000);
  await pause.click();
  await page.waitForTimeout(250);

  const hud = await page.evaluate(() => {
    const t = (id) => document.querySelector(id)?.textContent?.trim() || "";
    const warnings = document.querySelector("#intervention-warnings")?.textContent?.trim() || "";
    return {
      money: t("#money-display"), score: t("#total-score-display"),
      elapsed: t("#elapsed-time"), reputation: t("#rep-display"),
      load: t("#rps-display"),
      failures: t("#failures-panel").match(/\d+ total/)?.[0] || "0 total",
      breakdown: t("#failures-panel").replace(/\s+/g, " ").slice(0, 180),
      event: warnings.replace(/\s+/g, " ").slice(0, 140) || "NONE",
      gameOver: document.querySelector("#modal")?.classList.contains("hidden") === false,
      paused: document.querySelector("#btn-pause")?.classList.contains("active") || false,
    };
  });
  if (!hud.paused) throw new Error(`PAUSE_FAILED ${JSON.stringify(hud)}`);

  const money = Number(hud.money.replace(/[$,]/g, ""));
  return {
    ok: !hud.gameOver,
    phase: hud.gameOver ? "GAME_OVER" : "FAST_CHUNK_PAUSED",
    ...hud,
    next: hud.gameOver
      ? "05_start_fresh.js"
      : money >= 105 ? "04_add_serverless_cache.js (only if not already run)" : "record ledger, then another 03_fast_chunk.js",
  };
}
