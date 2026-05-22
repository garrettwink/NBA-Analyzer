import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Layout from './Layout'
import HomePage from './pages/HomePage'
import PlayersPage from './pages/PlayersPage'
import SearchPage from './pages/SearchPage'

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "/",
        element: <HomePage />
      },
      {
        path: "/players",
        element: <PlayersPage />
      },
      {
        path: "/search",
        element: <SearchPage />
      }
    ]
  }
])

export default function App() {
  return <RouterProvider router={router} />
}