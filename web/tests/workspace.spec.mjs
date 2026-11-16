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

  const lastSync = page.getByText(/Última sincronização:/);
  const previousSync = await lastSync.innerText();
  const pullRequests = page.getByRole("button", { name: /Investigar PR #/ });
  const previousCount = await pullRequests.count();
  expect(previousCount).toBeGreaterThan(0);
  await page.route("**/api/devhub/sync", route => route.fulfill({ status: 502 }));
  await sync.click();
  await expect(page.getByText("Falha ao sincronizar. Tente novamente.")).toBeVisible();
  await expect(lastSync).toHaveText(previousSync);
  await expect(pullRequests).toHaveCount(previousCount);

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

test("registra a recuperação sem perder a tarefa de investigação", async ({ page }) => {
  test.skip(process.env.NEXUS_TEST_OUTAGE_HISTORY !== "1", "O histórico controlado é preparado pela CI.");
  await page.goto(base);
  await page.getByLabel("Senha do operador").fill(process.env.NEXUS_OPERATOR_PASSWORD);
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.getByText("Histórico de verificações", { exact: true }).click();
  await expect(page.getByText(/Queda detectada.*HTTP 503/)).toBeVisible();
  await expect(page.getByText(/Recuperado.*HTTP 200/)).toBeVisible();
  const title = "Investigar o HTTP 503";
  await page.getByRole("button", { name: "Investigar Site do portfólio" }).click();
  await page.getByLabel("Título da tarefa").fill(title);
  await page.getByRole("button", { name: "Salvar tarefa" }).click();
  const task = page.getByRole("listitem").filter({ hasText: title });
  await expect(task).toContainText("Site do portfólio");
  await page.reload();
  await expect(task).toContainText("Site do portfólio");
});

test("cadastra projeto e serviço sem a carga de exemplo", async ({ page }) => {
  await page.goto(base);
  await page.getByLabel("Senha do operador").fill(process.env.NEXUS_OPERATOR_PASSWORD);
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.getByLabel("Nome do projeto").fill("Projeto de teste");
  await page.getByRole("button", { name: "Criar projeto" }).click();

  const project = page.getByRole("article").filter({
    has: page.getByRole("heading", { name: "Projeto de teste", exact: true }),
  });
  await project.getByText("Adicionar serviço", { exact: true }).click();
  await project.getByLabel("Nome do serviço").fill("Página de status");
  await project.getByLabel("URL do serviço").fill("https://example.com/status");
  await project.getByRole("button", { name: "Cadastrar serviço" }).click();
  await expect(project.getByRole("button", { name: "Investigar Página de status" })).toBeVisible();
  await page.reload();
  await expect(project).toContainText("https://example.com/status");
});
