import React, { Suspense } from 'react';
import { 
  createBrowserRouter,
  RouterProvider
} from 'react-router-dom';

const Root = React.lazy(() => import('./Root'));
const Video = React.lazy(() => import('./Video'));

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
  },
  {
    path: "/video/:id",
    element: <Video />,
  },
]);

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <RouterProvider router={router} />
    </Suspense>
  )
}

export default App
