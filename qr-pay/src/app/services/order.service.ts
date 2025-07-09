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
export class OrderService {
    constructor(private http: HttpClient) {}

    createOrder(tableNumber: number) {
        return this.http.post(`${API_BASE_URL}/order/create/`, { table_number: tableNumber }, { withCredentials: true });
    }

    updateOrderStatus(orderId: number, status: string, paidItems?: { item_id: number; quantity_paid: number }[]) {
        const body: any = { status };
        if (status === 'partial') {
            body.paid_items = paidItems || [];
        }

        return this.http.post(`${API_BASE_URL}/order/update-status/${orderId}`, body, { withCredentials: true });
    }

    addItemToOrder(orderId: number, menu_item_id: number, quantity: number) {
        return this.http.post(`${API_BASE_URL}/order/add-item/${orderId}`, { menu_item_id, quantity }, { withCredentials: true });
    }

    updateOrderItem(itemId: number, updates: { quantity?: number; price?: number }) {
        return this.http.post(`${API_BASE_URL}/order/update-item/${itemId}`, updates, { withCredentials: true });
    }

    deleteOrderItem(itemId: number) {
        return this.http.post(`${API_BASE_URL}/order/delete/${itemId}`, {}, { withCredentials: true });
    }
}