"use client";

import { useEffect, useState, type FormEvent } from "react";

import DevHub from "./devhub";
import ServiceHistory from "./service-history";

const labels = { todo: "A fazer", in_progress: "Em andamento", done: "Concluído" };
type Status = keyof typeof labels;
type Project = { id: number; name: string };
type Service = { id: number; project_id: number; name: string; url: string };
type Task = { id: number; project_id: number; service_id: number | null; title: string; status: Status; pull_request_url: string | null };
type Workspace = { projects: Project[]; services: Service[]; tasks: Task[] };

async function request(path: string, method = "GET", body?: object) {
  return fetch("/api/" + path, {
    method,
    cache: "no-store",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
}

export default function Board() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [service, setService] = useState<Service | null>(null);

  const [pullRequest, setPullRequest] = useState<string | null>(null);

  async function refresh() {
    const response = await request("workspace");
    if (response.status === 401) {
      setWorkspace(null);
      setService(null);
      setPullRequest(null);
    } else if (response.ok) {
      setWorkspace(await response.json());
    } else {
      throw new Error("Workspace indisponível.");
    }
  }

  useEffect(() => {
    refresh().catch(() => setError("Workspace indisponível. Recarregue a página."))
      .finally(() => setLoading(false));
  }, []);

  async function perform(action: () => Promise<Response>, failure: string) {
    setBusy(true);
    setError("");
    try {
      const response = await action();
      if (!response.ok) {
        if (response.status === 401) await refresh();
        setError(failure);
        return false;
      }
      await refresh();
      return true;
    } catch {
      setError("Não foi possível atualizar o Workspace. Tente novamente.");
      return false;
    } finally {
      setBusy(false);
    }
  }

  function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const password = new FormData(event.currentTarget).get("password");
    void perform(() => request("session", "POST", { password }), "Não foi possível entrar. Confira a senha.");
  }

  async function addTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!service && !pullRequest) return;
    const fields = new FormData(event.currentTarget);
    const title = String(fields.get("title")).trim();
    const projectId = service?.project_id ?? Number(fields.get("project"));
    if (!title) {
      setError("Digite um título para a tarefa.");
      return;
    }
    const saved = await perform(
      () => request("tasks", "POST", { project_id: projectId, service_id: service?.id, pull_request_url: pullRequest, title }),
      "Não foi possível criar a tarefa.",
    );
    if (saved) {
      setService(null);
      setPullRequest(null);
    }
  }

  if (loading) return <p role="status">Carregando Workspace…</p>;

  return <>
    <p role="alert">{error}</p>
    {!workspace ? (
      <form onSubmit={login}>
        <label htmlFor="password">Senha do operador</label>
        <input id="password" name="password" type="password" autoComplete="current-password" required />
        <button disabled={busy}>Entrar</button>
      </form>
    ) : (
      <>
        <button disabled={busy} onClick={() => void perform(() => request("session", "DELETE"), "Não foi possível sair.")}>Sair</button>
        <section aria-labelledby="projects">
          <h2 id="projects">Projetos</h2>
          {!workspace.projects.length && <p>Nenhum projeto cadastrado.</p>}
          {workspace.projects.map(project => (
            <article key={project.id}>
              <h3>{project.name}</h3>
              {workspace.services.filter(item => item.project_id === project.id).map(item => (
                <div key={item.id}>
                  <p>{item.name} · {item.url}</p>
                  <ServiceHistory serviceId={item.id} />
                  <button disabled={busy} onClick={() => { setPullRequest(null); setService(item); }}>Investigar {item.name}</button>
                </div>
              ))}
            </article>
          ))}
        </section>
        {(service || pullRequest) && (
          <form key={service?.id ?? pullRequest} onSubmit={addTask}>
            <h2>{service ? "Investigar " + service.name : "Criar tarefa para o PR"}</h2>
            {pullRequest && <>
              <p><a href={pullRequest}>Abrir PR no GitHub</a></p>
              <label htmlFor="task-project">Projeto</label>
              <select id="task-project" name="project" required>
                {workspace.projects.map(project => <option key={project.id} value={project.id}>{project.name}</option>)}
              </select>
            </>}
            <label htmlFor="task-title">Título da tarefa</label>
            <input id="task-title" name="title" maxLength={120} required autoFocus />
            <button disabled={busy}>Salvar tarefa</button>
            <button type="button" disabled={busy} onClick={() => { setService(null); setPullRequest(null); }}>Cancelar</button>
          </form>
        )}
        <DevHub onInvestigate={url => { setService(null); setPullRequest(url); }} />
        <section aria-labelledby="tasks">
          <h2 id="tasks">Tarefas</h2>
          {!workspace.tasks.length && <p>Nenhuma tarefa cadastrada.</p>}
          {Object.entries(labels).map(([status, label]) => (
            <div key={status}>
              <h3>{label}</h3>
              <ul>
                {workspace.tasks.filter(task => task.status === status).map(task => (
                  <li key={task.id}>
                    <strong>{task.title}</strong>
                    {task.pull_request_url && <p><a href={task.pull_request_url}>PR no GitHub</a></p>}
                    <p>{workspace.services.find(item => item.id === task.service_id)?.name}</p>
                    <label htmlFor={"task-" + task.id}>Situação de {task.title}</label>
                    <select id={"task-" + task.id} value={task.status} disabled={busy} onChange={event =>
                      void perform(() => request("tasks/" + task.id, "PATCH", { status: event.target.value }), "Não foi possível mover a tarefa.")
                    }>
                      {Object.entries(labels).map(([value, text]) => <option key={value} value={value}>{text}</option>)}
                    </select>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      </>
    )}
  </>;
}
