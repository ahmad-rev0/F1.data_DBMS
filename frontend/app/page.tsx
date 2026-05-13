import "./globals.css";

export const dynamic = "force-dynamic";

function apiBase(): string {
  const raw =
    process.env.API_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_URL?.trim() ||
    "";
  return raw.replace(/\/$/, "");
}

export default async function Home() {
  const base = apiBase();
  let stats: Record<string, number> | null = null;
  let error: string | null = null;

  if (!base) {
    error =
      "Set NEXT_PUBLIC_API_URL in Vercel to your Render service URL (no trailing slash), e.g. https://f1-platform.onrender.com";
  } else {
    try {
      const res = await fetch(`${base}/api/stats/`, { cache: "no-store" });
      if (res.ok) {
        stats = (await res.json()) as Record<string, number>;
      } else {
        error = `API returned ${res.status}`;
      }
    } catch (e) {
      error = e instanceof Error ? e.message : String(e);
    }
  }

  return (
    <main className="wrap">
      <h1>Formula 1 data</h1>
      <p className="lead">
        This Vercel app calls your <strong>Render</strong> Django service at{" "}
        <code>/api/stats/</code>. The full course UI (templates, login, admin)
        stays on the same Render URL as the API.
      </p>

      {error && (
        <p className="err" role="alert">
          {error}
        </p>
      )}

      {stats && (
        <ul className="grid">
          {Object.entries(stats).map(([k, v]) => (
            <li key={k}>
              <span className="k">{k.replace(/_/g, " ")}</span>
              <span className="v">{v.toLocaleString()}</span>
            </li>
          ))}
        </ul>
      )}

      {base && (
        <p className="foot">
          <a href={base}>Open full app on Render</a>
        </p>
      )}
    </main>
  );
}
