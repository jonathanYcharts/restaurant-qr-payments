import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent) },
  { path: 'dashboard', loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent) },
  { path: 'activate', loadComponent: () => import('./components/activate/activate.component').then(m => m.ActivateComponent) },
  {
    path: 'restaurant/:restaurantId/mesa/:tableNumber',
    loadComponent: () =>
      import('./components/table/table.component').then(m => m.TableComponent),
  },
  {
    path: 'success',
    loadComponent: () =>
      import('./components/pages/success/success.component').then(m => m.SuccessPageComponent),
  },
  {
    path: 'cancel',
    loadComponent: () =>
      import('./components/pages/cancel/cancel.component').then(m => m.CancelPageComponent),
  },
];
