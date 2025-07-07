// Vendor
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

// Services
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.template.html',
})
export class DashboardComponent implements OnInit {
  username = '';
  restaurantName = '';
  orders: any[] = [];
  menu: any[] = [];
  error = '';

  constructor(private router: Router, private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.getCurrentUser().subscribe({
      next: (user) => {
        this.username = user.username;
        this.restaurantName = user.restaurant || '';

        this.authService.getDashboardData().subscribe({
          next: (data: any) => {
            this.username = data.username;
            this.restaurantName = data.restaurant;
            this.orders = data.orders;
            this.menu = data.menu;
          },
          error: ({ error }) => {
            this.error = error.error;
          }
        });
      },
      error: () => {
        this.router.navigate(['/login']);
      }
    });
  }


  logout(): void {
      this.authService.logout().subscribe({
          next: () => this.router.navigate(['/login']),
          error: () => alert('No se pudo cerrar sesión')
      });
  }
}
