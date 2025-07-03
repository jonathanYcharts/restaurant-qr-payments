// Vendor
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Interfaces
import { Table } from '../interfaces/order.interface';

@Injectable({ providedIn: 'root' })
export class TableService {
    constructor(private http: HttpClient) {}

    getTableItems(restaurantId: number, tableNumber: number): Observable<Table>  {
        return this.http.get<Table>(
            `http://localhost:8000/restaurant/${restaurantId}/mesa/${tableNumber}/`
        );
    }

    createCheckoutSession(restaurantId: number, items: any[]): Observable<{ id: string }> {
        return this.http.post<{ id: string }>(
            `http://localhost:8000/restaurant/${restaurantId}/create-checkout-session/`,
            { items }
        );
    }
}
