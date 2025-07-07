// Vendor
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Interfaces
import { Table } from '../interfaces/order.interface';

// Constant
import { environment } from '../../environments/environment';

const API_BASE_URL = environment.apiBaseUrl;

@Injectable({ providedIn: 'root' })
export class TableService {
    constructor(private http: HttpClient) {}

    getTableItems(restaurantId: number, tableNumber: number): Observable<Table>  {
        return this.http.get<Table>(
            `${API_BASE_URL}/restaurant/${restaurantId}/mesa/${tableNumber}/`
        );
    }

    createCheckoutSession(restaurantId: number, items: any[]): Observable<{ id: string }> {
        return this.http.post<{ id: string }>(
            `${API_BASE_URL}/restaurant/${restaurantId}/create-checkout-session/`,
            { items }
        );
    }
}
