async (page) => {
  const fresh = page.getByRole("button", { name: "Start Fresh", exact: true });
  if ((await fresh.count()) !== 1 || !(await fresh.isVisible())) {
    throw new Error("START_FRESH_NOT_VISIBLE: do not use this unless the game-over screen is visible");
  }
  await fresh.click();
  await page.waitForTimeout(650);
  const skip = page.getByRole("button", { name: "Skip Tutorial", exact: true });
  if ((await skip.count()) === 1 && (await skip.isVisible())) await skip.click();
  const pause = page.locator("#btn-pause");
  if (!(await pause.evaluate((el) => el.classList.contains("active")))) await pause.click();
  return {
    ok: true,
    phase: "GAME_OVER_DISMISSED_FRESH_PAUSED",
    money: (await page.locator("#money-display").innerText()).trim(),
    next: "01_build_starter.js",
  };
}
