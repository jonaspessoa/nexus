"use client";

import { useEffect, useState } from "react";

const labels = { up: "Disponível", down: "Indisponível", blocked: "Verificação bloqueada" };
type Check = {
  id: number;
  checked_at: string;
  outcome: keyof typeof labels;
  http_status: number | null;
  latency_ms: number | null;
};
type Incident = { id: number; opened_at: string; resolved_at: string | null };
type History = { checks: Check[]; stale: boolean; incidents: Incident[] };

export default function ServiceHistory({ serviceId }: { serviceId: number }) {
  const [history, setHistory] = useState<History | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/services/" + serviceId + "/checks", { cache: "no-store", signal: controller.signal })
      .then(response => {
        if (!response.ok) throw new Error();
        return response.json();
      })
      .then(setHistory)
      .catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, [serviceId]);

  if (error) return <p role="alert">Não foi possível carregar o histórico.</p>;
  if (!history) return <p role="status">Carregando verificações…</p>;
  const latest = history.checks[0];
  if (!latest) return <p>Aguardando a primeira verificação.</p>;

  return (
    <>
      <p>{history.stale ? "Verificação atrasada · Último resultado: " : ""}{labels[latest.outcome]}</p>
      <details>
        <summary>Histórico de verificações</summary>
        <ol>
          {history.checks.map((check, index) => {
            const previous = history.checks[index + 1];
            const recovered = check.outcome === "up" && previous?.outcome === "down";
            const fell = check.outcome === "down" && previous?.outcome === "up";
            return (
              <li key={check.id}>
                <time dateTime={check.checked_at}>{new Date(check.checked_at).toLocaleString("pt-BR")}</time>
                {" · "}{recovered ? "Recuperado" : fell ? "Queda detectada" : labels[check.outcome]}
                {check.http_status !== null && " · HTTP " + check.http_status}
                {check.latency_ms !== null && " · " + check.latency_ms + " ms"}
              </li>
            );
          })}
        </ol>
      </details>
      {history.incidents.length > 0 && (
        <details>
          <summary>Incidentes recentes</summary>
          <ol>
            {history.incidents.map(incident => (
              <li key={incident.id}>
                Aberto em <time dateTime={incident.opened_at}>{new Date(incident.opened_at).toLocaleString("pt-BR")}</time>
                {incident.resolved_at
                  ? <> · Resolvido em <time dateTime={incident.resolved_at}>{new Date(incident.resolved_at).toLocaleString("pt-BR")}</time></>
                  : " · Em andamento"}
              </li>
            ))}
          </ol>
        </details>
      )}
    </>
  );
}
