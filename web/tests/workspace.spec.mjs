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
