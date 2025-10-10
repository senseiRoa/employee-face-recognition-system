import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./login/login.page').then((m) => m.LoginPage),
  },
  {
    path: 'home',
    loadComponent: () => import('./home/home.page').then((m) => m.HomePage),
    canActivate: [AuthGuard]
  },
  {
    path: 'configuration',
    loadComponent: () => import('./configuration/configuration.page').then((m) => m.ConfigurationPage),
    canActivate: [AuthGuard]
  },
  {
    path: 'device-details',
    loadComponent: () => import('./device-details/device-details.page').then((m) => m.DeviceDetailsPage),
    canActivate: [AuthGuard]
  },
  {
    path: 'time-tracker',
    loadComponent: () => import('./time-tracker/time-tracker.page').then((m) => m.TimeTrackerPage),
    canActivate: [AuthGuard]
  },
  {
    path: 'reports',
    loadComponent: () => import('./reports/reports.page').then((m) => m.ReportsPage),
    canActivate: [AuthGuard]
  },
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full',
  },
];
