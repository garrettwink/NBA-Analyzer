import { Link, Outlet } from 'react-router-dom'
import './Layout.css'

export default function Layout() {
  return (
    <div>
      <nav>
        <Link to="/">Home</Link>
      </nav>
      
      <main>
        <Outlet />
      </main>
    </div>
  )
}