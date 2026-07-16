async (page) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  const money = async () => Number((await page.locator("#money-display").innerText()).replace(/[$,]/g, ""));
  if (!(await page.locator("#btn-pause").evaluate((el) => el.classList.contains("active")))) {
    throw new Error("NOT_PAUSED_BEFORE_EXPANSION");
  }
  const before = await money();
  if (before < 105) throw new Error("NEED_AT_LEAST_$105");

  await page.locator("#tool-serverless").click();
  await page.mouse.click(1030, 500);
  await page.waitForTimeout(100);
  const afterServerless = await money();

  await page.locator("#tool-cache").click();
  await page.mouse.click(800, 500);
  await page.waitForTimeout(100);
  const afterCache = await money();
  if (before - afterServerless !== 45 || afterServerless - afterCache !== 60) {
    throw new Error(`EXPANSION_PLACE_FAILED before=${before} afterServerless=${afterServerless} afterCache=${afterCache}`);
  }

  const n = {
    alb: [869, 230], serverless1: [1051, 364], serverless2: [1022, 482],
    cache: [806, 475], nosql: [900, 600], s3: [716, 636], search: [1051, 722],
  };
  const edges = [
    ["alb", "serverless2"], ["serverless2", "cache"], ["serverless2", "nosql"],
    ["serverless2", "s3"], ["serverless2", "search"],
    ["serverless1", "cache"], ["cache", "nosql"],
  ];
  await page.locator("#tool-connect").click();
  for (const [from, to] of edges) {
    await page.mouse.click(...n[from]);
    await page.waitForTimeout(80);
    await page.mouse.click(...n[to]);
    await page.waitForTimeout(120);
  }
  await page.locator("#tool-select").click();
  return { ok: true, phase: "SERVERLESS2_CACHE_ADDED", money: await money(), next: "take screenshot; continue 03_fast_chunk.js" };
}
