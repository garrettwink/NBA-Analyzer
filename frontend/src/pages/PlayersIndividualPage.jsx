import { useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'

export default function PlayersIndividualPage() {
    const { playerId } = useParams()
    const [player, setPlayer] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        fetch(`http://localhost:8000/players/${playerId}`)
        .then(response => {
            if (!response.ok) 
              throw new Error('Player doesn\'t exist')
            return response.json()
        })

        .then(data => {
          setPlayer(data);
          setLoading(false);
        })
        .catch(error => {
          setError(error.message);
          setLoading(false);
        })
    }, [playerId]);

    if (loading) return <div>Loading...</div>
    if (error) return <div>Error: {error}</div>

  return (
    <div className="player-page">
      <header className="player-header">
        <div>
          <h1>{player.name}</h1>
          <p>
            Position: {player.position} <br />
            Draft Year: {player.draft_year} <br />
            Birth Date: {player.birth_date} <br />
            Height: {player.height} <br />
            Weight: {player.weight}
          </p>
        </div>
      </header>

      <section className="stats-section">
        <h2>Season stats</h2>

        {player.stats.map(stat => (
          <article className="season-card" key={stat.season}>
            <h3>{stat.season}</h3>
            <dl className="stat-grid">
              <div>
                <dt>PTS</dt>
                <dd>{stat.pts}</dd>
              </div>
              <div>
                <dt>AST</dt>
                <dd>{stat.ast}</dd>
              </div>
              <div>
                <dt>REB</dt>
                <dd>{stat.reb}</dd>
              </div>
              <div>
                <dt>OREB</dt>
                <dd>{stat.off_reb}</dd>
              </div>
              <div>
                <dt>DREB</dt>
                <dd>{stat.def_reb}</dd>
              </div>
              <div>
                <dt>STL</dt>
                <dd>{stat.stl}</dd>
              </div>
              <div>
                <dt>BLK</dt>
                <dd>{stat.blk}</dd>
              </div>
              <div>
                <dt>TOV</dt>
                <dd>{stat.tov}</dd>
              </div>
              <div>
                <dt>FG%</dt>
                <dd>{stat.fg_pct}</dd>
              </div>
              <div>
                <dt>3P%</dt>
                <dd>{stat.fg3_pct}</dd>
              </div>
              <div>
                <dt>FT%</dt>
                <dd>{stat.ft_pct}</dd>
              </div>
              <div>
                <dt>GP</dt>
                <dd>{stat.gp}</dd>
              </div>
              <div>
                <dt>MPG</dt>
                <dd>{Math.round(stat.mpg * 100) / 100}</dd>
              </div>
              <div>
                <dt>USG%</dt>
                <dd>{stat.usg_pct}</dd>
              </div>
              <div>
                <dt>Net Rating</dt>
                <dd>{stat.net_rating}</dd>
              </div>
              <div>
                <dt>PIE</dt>
                <dd>{stat.pie}</dd>
              </div>
              <div>
                <dt>TS%</dt>
                <dd>{stat.ts_pct}</dd>
              </div>
            </dl>
          </article>
        ))}
      </section>
    </div>
  )
}