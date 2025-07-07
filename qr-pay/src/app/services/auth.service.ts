// Vendor
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Interface
import { AuthUser } from '../interfaces/auth.interface';

// Constants
import { environment } from '../../environments/environment';

const API_BASE_URL = environment.apiBaseUrl;

@Injectable({ providedIn: 'root' })
export class AuthService {
    constructor(private http: HttpClient) {}

    login(username: string, password: string): Observable<any> {
        return this.http.post(`${API_BASE_URL}/api/login/`, {
            username,
            password,
        }, { withCredentials: true });
    }

    logout(): Observable<any> {
        return this.http.post(`${API_BASE_URL}/api/logout/`, {}, { withCredentials: true });
    }

    getCurrentUser(): Observable<AuthUser> {
        return this.http.get<AuthUser>(`${API_BASE_URL}/api/check-auth/`, { withCredentials: true });
    }

    getDashboardData(): Observable<any> {
        return this.http.get(`${API_BASE_URL}/dashboard/`, { withCredentials: true });
    }
}
