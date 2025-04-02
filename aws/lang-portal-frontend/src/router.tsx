import { createBrowserRouter } from 'react-router-dom'
import { MainLayout } from '@/components/layout/MainLayout'
import { Dashboard } from '@/pages/Dashboard'
import { StudyActivities } from '@/pages/StudyActivities'
import { StudySession } from '@/pages/StudySession'
import { Words } from '@/pages/Words'
import { Groups } from '@/pages/Groups'
import { GroupDetail } from '@/pages/GroupDetail'
import { Settings } from '@/pages/Settings'
import { AuthCallback } from './pages/AuthCallback'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'study',
        children: [
          {
            index: true,
            element: <StudyActivities />,
          },
          {
            path: ':sessionId',
            element: <StudySession />,
          },
        ],
      },
      {
        path: 'words',
        element: <Words />,
      },
      {
        path: 'groups',
        children: [
          {
            index: true,
            element: <Groups />,
          },
          {
            path: ':groupId',
            element: <GroupDetail />,
          },
        ],
      },
      {
        path: 'settings',
        element: <Settings />,
      },
      {
        path: 'auth/callback',
        element: <AuthCallback />,
      },
    ],
  },
]) 