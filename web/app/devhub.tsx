"use client";

import { useEffect, useState } from "react";

type Activity = {
  number: number;
  kind: "issue" | "pull_request";
  title: string;
  state: string;
  url: string;
};

type Snapshot = {
  repository: string | null;
  synced_at: string | null;
  items: Activity[];
};

export default function DevHub() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  async function load(sync = false) {
    setBusy(true);
    setError("");
    try {
      const response = await fetch(sync ? "/api/devhub/sync" : "/api/devhub", {
        method: sync ? "POST" : "GET",
        cache: "no-store",
      });
      if (!response.ok) throw new Error();
      setSnapshot(await response.json());
    } catch {
      setError(sync ? "Falha ao sincronizar. Tente novamente." : "Não foi possível consultar a atividade.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => { void load(); }, []);

  return (
    <section aria-labelledby="devhub">
      <h2 id="devhub">DevHub</h2>
      {error && <p role="alert">{error}</p>}
      {!snapshot && (busy ? <p role="status">Carregando atividade…</p> :
        <button onClick={() => void load()}>Tentar novamente</button>)}
      {snapshot && (snapshot.repository ? (
        <>
          <p>{snapshot.repository}</p>
          <p role="status">{snapshot.synced_at
            ? "Última sincronização: " + new Date(snapshot.synced_at).toLocaleString("pt-BR")
            : "Aguardando a primeira sincronização."}</p>
          <button disabled={busy} onClick={() => void load(true)}>{busy ? "Sincronizando…" : "Sincronizar"}</button>
          {snapshot.synced_at && !snapshot.items.length && <p>Nenhuma atividade recente.</p>}
          <ul>
            {snapshot.items.map(item => (
              <li key={item.number}>
                <a href={item.url}>{item.kind === "pull_request" ? "PR" : "Issue"} #{item.number} · {item.title}</a>
                {" — "}{item.state === "open" ? "Em aberto" : "Encerrado"}
              </li>
            ))}
          </ul>
        </>
      ) : <p>Configure NEXUS_GITHUB_REPOSITORY no arquivo .env.</p>)}
    </section>
  );
}
