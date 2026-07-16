async (page) => page.evaluate(() => {
  const t = (id) => document.querySelector(id)?.textContent?.trim() || "";
  return {
    money: t("#money-display"), score: t("#total-score-display"),
    elapsed: t("#elapsed-time"), reputation: t("#rep-display"),
    load: t("#rps-display"), upkeep: t("#upkeep-display"),
    failures: t("#failures-panel").replace(/\s+/g, " ").slice(0, 240),
    warning: (document.querySelector("#intervention-warnings")?.textContent || "").trim().replace(/\s+/g, " ").slice(0, 160) || "NONE",
    paused: document.querySelector("#btn-pause")?.classList.contains("active") || false,
    tutorialVisible: !!(document.querySelector("#tutorial-modal")?.offsetWidth || document.querySelector("#tutorial-modal")?.offsetHeight),
    gameOver: document.querySelector("#modal")?.classList.contains("hidden") === false,
  };
})
