import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Layout from './Layout'
import HomePage from './pages/HomePage'
import PlayersPage from './pages/PlayersPage'
import SearchPage from './pages/SearchPage'
import PlayersIndividualPage from './pages/PlayersIndividualPage'

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
        path: "/search",
        element: <SearchPage />
      }
    ]
  }
])

export default function App() {
  return <RouterProvider router={router} />
}