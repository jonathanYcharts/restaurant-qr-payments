import { Routes } from '@angular/router';

export const routes: Routes = [
    { path: 'mesa/:id', loadComponent: () => import('./components/table/table.component').then(m => m.TableComponent) },
    { path: 'success', loadComponent: () => import('./components/pages/success/success.component').then(m => m.SuccessPageComponent) },
    { path: 'cancel', loadComponent: () => import('./components/pages/cancel/cancel.component').then(m => m.CancelPageComponent) },
    { path: '**', redirectTo: '', pathMatch: 'full' },
];
