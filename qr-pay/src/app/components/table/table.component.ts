import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TableService } from '../../services/table.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { loadStripe } from '@stripe/stripe-js';
import { environment } from '../../../environments/environment';

interface OrderItem {
  id: number;
  name: string;
  price: number;
  selected: boolean;
}

interface Order {
  table: number;
  items: OrderItem[];
}

@Component({
  selector: 'app-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './table.template.html',
  styleUrl: './table.css'
})
export class TableComponent implements OnInit {
  tableNumber!: number;
  items: OrderItem[] = [];

  constructor(private route: ActivatedRoute, private tableService: TableService) {}

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.tableNumber = +params['id'];
      this.tableService.getTableItems(this.tableNumber).subscribe((res: Order) => {
        this.items = res.items.map(item => ({ ...item, selected: false }));
      });
    });
  }

  getSelectedItems(): OrderItem[] {
    return this.items.filter(item => item.selected);
  }

  calculateTotal(): number {
    return this.getSelectedItems().reduce((sum, item) => sum + item.price, 0);
  }

  async confirmSelection(): Promise<void> {
    const selected = this.getSelectedItems();

    this.tableService.createCheckoutSession(selected).subscribe({
      next: async (res) => {
        const stripe = await loadStripe(environment.stripePublishableKey);

        if (!stripe) {
          console.error('Stripe failed to load.');
          return;
        }

        if (stripe) {
          await stripe.redirectToCheckout({ sessionId: res.id });
        } else {
          console.error('Stripe failed to load.');
        }
      },
      error: (err) => {
        console.error('Stripe session error:', err);
      }
    });
  }
}
