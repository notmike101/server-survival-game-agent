async (page) => {
  const GAME_URL = "https://pshenok.github.io/server-survival/";
  await page.setViewportSize({ width: 1920, height: 1080 });

  if (!page.url().startsWith(GAME_URL)) {
    await page.goto(GAME_URL, { waitUntil: "domcontentloaded" });
  }

  const fresh = page.getByRole("button", { name: "Start Fresh", exact: true });
  if ((await fresh.count()) === 1 && (await fresh.isVisible())) {
    throw new Error("GAME_OVER_VISIBLE: run 05_start_fresh.js before starting again");
  }

  const start = page.getByRole("button", { name: "Start Survival", exact: true });
  if ((await start.count()) !== 1 || !(await start.isVisible())) {
    throw new Error("START_SURVIVAL_NOT_VISIBLE: reload once, then rerun this file");
  }
  await start.click();
  await page.waitForTimeout(650);

  const skip = page.getByRole("button", { name: "Skip Tutorial", exact: true });
  if ((await skip.count()) === 1 && (await skip.isVisible())) {
    await skip.click();
  }

  const pause = page.locator("#btn-pause");
  if (!(await pause.evaluate((el) => el.classList.contains("active")))) {
    await pause.click();
  }

  const tutorialVisible = await page.locator("#tutorial-modal").isVisible();
  const money = (await page.locator("#money-display").innerText()).trim();
  const elapsed = (await page.locator("#elapsed-time").innerText()).trim();
  if (tutorialVisible || money !== "$500" || !/^(0s|00:00)$/.test(elapsed)) {
    throw new Error(`BAD_FRESH_STATE tutorial=${tutorialVisible} money=${money} elapsed=${elapsed}`);
  }

  return { ok: true, phase: "FRESH_PAUSED", money, elapsed, next: "01_build_starter.js" };
}
