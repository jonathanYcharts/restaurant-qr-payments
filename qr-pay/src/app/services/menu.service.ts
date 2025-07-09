// Vendor
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Interface
import { MenuItem } from '../interfaces/menu.interface';

// Constant
import { environment } from '../../environments/environment';

const API_BASE_URL = environment.apiBaseUrl;

@Injectable({ providedIn: 'root' })
export class MenuService {
    constructor(private http: HttpClient) {}

    addItem(data: { name: string; price: number }): Observable<{ item: MenuItem}> {
        return this.http.post<{ item: MenuItem }>(`${API_BASE_URL}/menu/add/`, data, { withCredentials: true });
    }

    updateItem(id: number, data: any): Observable<{ item: MenuItem}> {
        return this.http.post<{ item: MenuItem }>(`${API_BASE_URL}/menu/update/${id}/`, data, { withCredentials: true });
    }

    deleteItem(id: number): Observable<any> {
        return this.http.post(`${API_BASE_URL}/menu/delete/${id}/`, {}, { withCredentials: true });
    }
}
