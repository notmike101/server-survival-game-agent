async (page) => {
  await page.setViewportSize({ width: 1920, height: 1080 });

  const text = async (selector) => (await page.locator(selector).innerText()).trim();
  const moneyValue = async () => Number((await text("#money-display")).replace(/[$,]/g, ""));
  const pause = page.locator("#btn-pause");
  if (!(await pause.evaluate((el) => el.classList.contains("active")))) {
    throw new Error("NOT_PAUSED: click Pause, then rerun");
  }
  if ((await page.locator("#tutorial-modal").isVisible()) || (await moneyValue()) !== 500) {
    throw new Error("NOT_CLEAN_START: use 00_start_survival.js on a fresh run");
  }

  const placements = [
    ["#tool-waf", 500, 250, 460],
    ["#tool-apigw", 700, 210, 390],
    ["#tool-alb", 880, 250, 340],
    ["#tool-serverless", 1030, 380, 295],
    ["#tool-cdn", 500, 520, 235],
    ["#tool-s3", 700, 650, 210],
    ["#tool-nosql", 900, 600, 130],
    ["#tool-search", 1040, 740, 10],
  ];

  for (const [tool, x, y, expectedMoney] of placements) {
    await page.locator(tool).click();
    await page.mouse.click(x, y);
    await page.waitForTimeout(100);
    const actualMoney = await moneyValue();
    if (actualMoney !== expectedMoney) {
      throw new Error(`PLACE_FAILED tool=${tool} expectedMoney=${expectedMoney} actualMoney=${actualMoney}`);
    }
  }

  const nodes = {
    internet: [655, 360], waf: [503, 230], api: [684, 190], alb: [869, 230],
    serverless: [1051, 364], cdn: [500, 509], s3: [716, 636],
    nosql: [900, 600], search: [1051, 722],
  };
  const edges = [
    ["internet", "waf"], ["waf", "api"], ["api", "alb"],
    ["alb", "serverless"], ["internet", "cdn"], ["cdn", "s3"],
    ["serverless", "nosql"], ["serverless", "s3"], ["serverless", "search"],
  ];

  await page.locator("#tool-connect").click();
  for (const [from, to] of edges) {
    await page.mouse.click(...nodes[from]);
    await page.waitForTimeout(80);
    await page.mouse.click(...nodes[to]);
    await page.waitForTimeout(120);
  }
  await page.locator("#tool-select").click();

  return {
    ok: true,
    phase: "STARTER_BUILT_PAUSED",
    money: await text("#money-display"),
    topology: "I->WAF->API->ALB->Srv; I->CDN->S3; Srv->{NoSQL,S3,Search}",
    next: "take screenshot, then 02_prove_starter.js",
  };
}
