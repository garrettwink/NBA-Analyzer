import { Link, Outlet } from 'react-router-dom'
import './Layout.css'

export default function Layout() {
  return (
    <div>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/players">Players</Link>
        <Link to="/search">Search</Link>
      </nav>
      
      <main>
        <Outlet />
      </main>
    </div>
  )
}