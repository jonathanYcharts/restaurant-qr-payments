import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class TableService {
    constructor(private http: HttpClient) {}

    getTableItems(tableNumber: number): Observable<{ table: number; items: any[] }>  {
        return this.http.get<{ table: number; items: any[] }>(
            `http://localhost:8000/mesa/${tableNumber}/`
        );
    }

    createCheckoutSession(items: any[]): Observable<{ id: string }> {
        return this.http.post<{ id: string }>(
            'http://localhost:8000/create-checkout-session/',
            { items }
        );
    }
}
