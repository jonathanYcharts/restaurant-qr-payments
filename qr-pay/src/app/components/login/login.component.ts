// Vendor
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

// Services
import { AuthService } from '../../services/auth.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './login.template.html',
})
export class LoginComponent implements OnInit {
    username = '';
    password = '';
    error = '';

    constructor(private router: Router, private authService: AuthService) {}

    ngOnInit(): void {
        this.authService.getCurrentUser().subscribe({
            next: (user) => {
                if (user?.username) {
                    this.router.navigate(['/dashboard']);
                }
            },
        });
    }

    login(): void {
        this.authService.login(this.username, this.password).subscribe({
            next: () => this.router.navigate(['/dashboard']),
            error: () => this.error = 'Login failed. Please check your credentials.'
        });
    }
}
