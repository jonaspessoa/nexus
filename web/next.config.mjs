const api = process.env.NEXUS_API_URL ?? "http://localhost:8000";

export default {
  async rewrites() {
    return [
      { source: "/api/session", destination: api + "/session" },
      { source: "/api/workspace", destination: api + "/workspace" },
      { source: "/api/tasks", destination: api + "/tasks" },
      { source: "/api/tasks/:id", destination: api + "/tasks/:id" },
      { source: "/api/devhub", destination: api + "/devhub" },
      { source: "/api/devhub/sync", destination: api + "/devhub/sync" },
      { source: "/api/services/:id/checks", destination: api + "/services/:id/checks" },
    ];
  },
};
