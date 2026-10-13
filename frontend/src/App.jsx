import { useEffect, useState } from "react";

const TYPE_LABELS = {
  normal: "Normal", fire: "Feuer", water: "Wasser", electric: "Elektro", grass: "Pflanze", ice: "Eis",
  fighting: "Kampf", poison: "Gift", ground: "Boden", flying: "Flug", psychic: "Psycho", bug: "Käfer",
  rock: "Gestein", ghost: "Geist", dragon: "Drache", dark: "Unlicht", steel: "Stahl", fairy: "Fee",
};

const TYPE_COLORS = {
  normal: "#9fa19f", fire: "#e62829", water: "#2980ef", electric: "#d4a800", grass: "#3fa129", ice: "#3dc7ef",
  fighting: "#ff8000", poison: "#9141cb", ground: "#915121", flying: "#81b9ef", psychic: "#ef4179", bug: "#91a119",
  rock: "#afa981", ghost: "#704170", dragon: "#5060e1", dark: "#624d4e", steel: "#60a1b8", fairy: "#ef70ef",
};

const STAT_LABELS = {
  hp: "HP", attack: "Angriff", defense: "Verteidigung",
  special_attack: "Spez.-Angriff", special_defense: "Spez.-Verteidigung", speed: "Tempo",
};

const range = (from, to) => Array.from({ length: to - from + 1 }, (_, i) => from + i);

function FilterCard({ generations, genFrom, genTo, setGenFrom, setGenTo, allTypes, types, toggleType }) {
  return (
    <section className="card card-filter">
      <h2>Filter</h2>
      <label className="label">Generation:</label>
      <div className="gen-range">
        <select value={genFrom} onChange={e => setGenFrom(Number(e.target.value))}>
          {generations.map(g => <option key={g} value={g}>{g}</option>)}
        </select>
        <span>bis</span>
        <select value={genTo} onChange={e => setGenTo(Number(e.target.value))}>
          {generations.map(g => <option key={g} value={g}>{g}</option>)}
        </select>
      </div>

      <label className="label">Typen:</label>
      <div className="types">
        {allTypes.map(t => (
          <label key={t} className="type-check">
            <input type="checkbox" checked={types.includes(t)} onChange={() => toggleType(t)} />
            {TYPE_LABELS[t] ?? t}
          </label>
        ))}
      </div>
    </section>
  );
}

function StatCard({ stats, weights, setWeight }) {
  return (
    <section className="card card-stats">
      <h2>Stat-Gewichtung</h2>
      <div className="stat-grid">
        {stats.map(s => (
        <label key={s} className="stat">
          <span>{STAT_LABELS[s] ?? s}</span>
          <input
            type="range" min="0" max="5" step="0.5"
            value={weights[s] ?? 1}
            onChange={e => setWeight(s, Number(e.target.value))}
          />
          <span className="stat-value">{weights[s] ?? 1}</span>
        </label>
      ))}
      </div>
    </section>
  );
}

function ActionCard({ typeBonus, setTypeBonus, limit, setLimit, loading, onSubmit }) {
  return (
    <section className="actions">
      <button className="submit" onClick={onSubmit} disabled={loading}>
        {loading ? "Berechne…" : "Team berechnen"}
      </button>
      <label className="option">
        Typ-Bonus
        <input type="number" min="0" value={typeBonus} onChange={e => setTypeBonus(Number(e.target.value))} />
      </label>
      <label className="option">
        Anzahl
        <input type="number" min="1" max="100" value={limit} onChange={e => setLimit(Number(e.target.value))} />
      </label>
    </section>
  );
}

function ResultTable({ results }) {
  return (
    <section className="card card-results">
      <h2>Ergebnisliste</h2>
      {results.length === 0 ? (
        <p className="muted">Keine Pokémon gefunden.</p>
      ) : (
        <table>
          <thead>
            <tr><th>Pokémon</th><th>Typ</th><th>Fit-Score</th></tr>
          </thead>
          <tbody>
            {results.map(p => (
              <tr key={p.id}>
                <td className="name">
                  {p.sprite && <img src={p.sprite} alt="" />}
                  {p.name}
                </td>
                <td>
                  {p.types.map(t => (
                    <span key={t} className="type-badge" style={{ background: TYPE_COLORS[t] }}>
                      {TYPE_LABELS[t] ?? t}
                    </span>
                  ))}
                </td>
                <td className="score">{Number(p.score.toFixed(1))}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

export default function App() {
  const [meta, setMeta] = useState(null);
  const [genFrom, setGenFrom] = useState(1);
  const [genTo, setGenTo] = useState(9);
  const [types, setTypes] = useState([]);
  const [weights, setWeights] = useState({});
  const [typeBonus, setTypeBonus] = useState(50);
  const [limit, setLimit] = useState(10);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/meta")
      .then(r => r.json())
      .then(m => {
        setMeta(m);
        setGenTo(Math.max(...m.generations));
        setWeights(Object.fromEntries(m.stats.map(s => [s, 1])));
      })
      .catch(e => setError(`Backend nicht erreichbar: ${e}`));
  }, []);

  const toggleType = t =>
    setTypes(prev => (prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t]));

  const setWeight = (stat, value) => setWeights(prev => ({ ...prev, [stat]: value }));

  async function submit() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          generations: range(Math.min(genFrom, genTo), Math.max(genFrom, genTo)),
          types,
          stat_weights: weights,
          type_bonus: typeBonus,
          limit,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail, null, 2);
        setError(`Fehler ${res.status}: ${detail}`);
        setResults(null);
        return;
      }
      setResults(data.details);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header>
        <h1>PokeMatch</h1>
        <p className="muted">
          Finde das beste Pokémon für dein Team
          {meta && ` · ${meta.pokemon_loaded} Pokémon geladen · Implementierung: ${meta.implementation}`}
        </p>
      </header>

      {!meta && !error && <p className="muted">Lade Pokémon…</p>}

      {meta && (
        <div className="grid">
          <FilterCard
            generations={meta.generations}
            genFrom={genFrom} genTo={genTo} setGenFrom={setGenFrom} setGenTo={setGenTo}
            allTypes={meta.types} types={types} toggleType={toggleType}
          />
          <StatCard stats={meta.stats} weights={weights} setWeight={setWeight} />
          <ActionCard
            typeBonus={typeBonus} setTypeBonus={setTypeBonus}
            limit={limit} setLimit={setLimit}
            loading={loading} onSubmit={submit}
          />
        </div>
      )}

      {error && <pre className="error">{error}</pre>}
      {results && <ResultTable results={results} />}
    </main>
  );
}
