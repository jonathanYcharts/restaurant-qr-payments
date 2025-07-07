// Vendor
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-activate',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './activate.template.html',
})
export class ActivateComponent implements OnInit {
  token = '';
  username = '';
  password = '';
  restaurantName = '';
  error = '';

  constructor(private route: ActivatedRoute, private http: HttpClient, private router: Router) {}

  ngOnInit(): void {
    this.token = this.route.snapshot.queryParamMap.get('token') || '';
  }

  activate(): void {
    this.http.post('http://localhost:8000/api/activate/', {
      token: this.token,
      username: this.username,
      password: this.password,
      restaurant_name: this.restaurantName,
    }, { withCredentials: true }).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: (err) => this.error = err.error?.error || 'Activación fallida.'
    });
  }
}
