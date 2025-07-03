// Vendor
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { loadStripe } from '@stripe/stripe-js';
import { environment } from '../../../environments/environment';

// Interfaces
import { Table, OrderItem } from '../../interfaces/order.interface';

// Services
import { TableService } from '../../services/table.service';

@Component({
  selector: 'app-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './table.template.html',
  styleUrl: './table.css'
})
export class TableComponent implements OnInit {
  restaurantId!: number;
  tableNumber!: number;
  table: Table | null = null;

  constructor(private route: ActivatedRoute, private tableService: TableService) {}

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.restaurantId = +params['restaurantId'];
      this.tableNumber = +params['tableNumber'];
      this.tableService.getTableItems(this.restaurantId, this.tableNumber).subscribe((response: Table) => {
        this.table = {
          ...response,
          items: response.items.map((item) => { 
            return {
              ...item,
              quantity_to_pay: 0,
            };
          }),
        }
      });
    });
  }

  getSelectedItems(): OrderItem[] {
    return this.table
      ? this.table.items.filter(item => item.quantity_to_pay && item.quantity_to_pay > 0)
      : [];
  }

  calculateTotal(): number {
    return this.getSelectedItems().reduce((sum, item) => {
      return sum + item.price * item.quantity_to_pay;
    }, 0);
  }

  async confirmSelection(): Promise<void> {
    const selected = this.getSelectedItems().map(item => ({
      id: item.id,
      name: item.name,
      price: item.price,
      quantity: item.quantity_to_pay,
    }));

    this.tableService.createCheckoutSession(this.restaurantId, selected).subscribe({
      next: async (res) => {
        const stripe = await loadStripe(environment.stripePublishableKey);
        if (!stripe) {
          console.error('Stripe failed to load.');
          return;
        }
        await stripe.redirectToCheckout({ sessionId: res.id });
      },
      error: (err) => {
        console.error('Stripe session error:', err);
      }
    });
  }
}
