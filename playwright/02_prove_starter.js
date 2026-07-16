async (page) => {
  const read = async () => page.evaluate(() => {
    const t = (id) => document.querySelector(id)?.textContent?.trim() || "";
    return {
      money: t("#money-display"), score: t("#total-score-display"),
      elapsed: t("#elapsed-time"), reputation: t("#rep-display"),
      load: t("#rps-display"),
      failures: t("#failures-panel").match(/\d+ total/)?.[0] || "0 total",
      breakdown: t("#failures-panel").replace(/\s+/g, " ").slice(0, 180),
      paused: document.querySelector("#btn-pause")?.classList.contains("active") || false,
    };
  });

  if (!(await page.locator("#btn-pause").evaluate((el) => el.classList.contains("active")))) {
    throw new Error("NOT_PAUSED_BEFORE_PROOF");
  }
  await page.locator("#btn-play").click();
  await page.waitForTimeout(8000);
  await page.locator("#btn-pause").click();
  await page.waitForTimeout(250);

  const hud = await read();
  if (!hud.paused || hud.failures !== "0 total" || hud.reputation !== "100%" || Number(hud.score.replace(/,/g, "")) <= 0) {
    throw new Error(`STARTER_PROOF_FAILED ${JSON.stringify(hud)}`);
  }
  return { ok: true, phase: "STARTER_PROVEN", ...hud, next: "03_fast_chunk.js" };
}
