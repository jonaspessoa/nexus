import { expect, test } from "@playwright/test";

const base = "http://127.0.0.1:3000";

test("persiste a investigação e encerra a sessão", async ({ page }) => {
  await page.goto(base);
  await expect.poll(async () => (await page.request.get(base + "/api/workspace")).status()).toBe(401);

  await page.getByLabel("Senha do operador").fill(process.env.NEXUS_OPERATOR_PASSWORD);
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.getByRole("button", { name: "Investigar Site do portfólio" }).click();
  await page.getByLabel("Título da tarefa").fill("Conferir o deploy");
  await page.getByRole("button", { name: "Salvar tarefa" }).click();

  const status = page.getByLabel("Situação de Conferir o deploy");
  await expect(status).toHaveValue("todo");
  await status.selectOption("in_progress");
  await expect(status).toHaveValue("in_progress");
  await page.reload();
  await expect(status).toHaveValue("in_progress");
  await expect(page.getByRole("listitem").filter({ hasText: "Conferir o deploy" })).toContainText("Site do portfólio");

  await page.getByRole("button", { name: "Sair" }).click();
  await expect(page.getByLabel("Senha do operador")).toBeVisible();
  expect((await page.request.get(base + "/api/workspace")).status()).toBe(401);
});

test("sincroniza PRs e mantém o vínculo na tarefa", async ({ page }) => {
  test.skip(!process.env.NEXUS_GITHUB_REPOSITORY, "O teste precisa de um repositório público com PRs.");
  await page.goto(base);
  await page.getByLabel("Senha do operador").fill(process.env.NEXUS_OPERATOR_PASSWORD);
  await page.getByRole("button", { name: "Entrar" }).click();

  const sync = page.getByRole("button", { name: "Sincronizar", exact: true });
  for (let attempt = 0; attempt < 2; attempt += 1) {
    const completed = page.waitForResponse(response =>
      response.url().endsWith("/api/devhub/sync") && response.request().method() === "POST"
    );
    await sync.click();
    expect((await completed).ok()).toBe(true);
  }
  await expect(page.getByText(/Última sincronização:/)).toBeVisible();

  const investigate = page.getByRole("button", { name: /Investigar PR #/ }).first();
  await investigate.click();
  const url = await page.getByRole("link", { name: "Abrir PR no GitHub" }).getAttribute("href");
  await page.getByLabel("Título da tarefa").fill("Revisar alteração do GitHub");
  await page.getByRole("button", { name: "Salvar tarefa" }).click();

  const task = page.getByRole("listitem").filter({ hasText: "Revisar alteração do GitHub" });
  await expect(task.getByRole("link", { name: "PR no GitHub" })).toHaveAttribute("href", url);
  await page.reload();
  await expect(task.getByRole("link", { name: "PR no GitHub" })).toHaveAttribute("href", url);
});
