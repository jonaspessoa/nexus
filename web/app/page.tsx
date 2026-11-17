import Board from "./board";

export const dynamic = "force-dynamic";

export default async function Workspace() {
  const apiUrl = process.env.NEXUS_API_HOSTPORT
    ? "http://" + process.env.NEXUS_API_HOSTPORT
    : process.env.NEXUS_API_URL ?? "http://localhost:8000";
  const response = await fetch(apiUrl + "/health", {
    cache: "no-store",
    signal: AbortSignal.timeout(2000),
  }).catch(() => null);

  return (
    <main>
      <h1>Nexus</h1>
      <p role="status">{response?.ok ? "API conectada" : "API indisponível"}</p>
      <Board />
    </main>
  );
}
