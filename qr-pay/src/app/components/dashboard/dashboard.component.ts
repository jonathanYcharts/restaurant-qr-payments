// Vendor
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

// Services
import { AuthService } from '../../services/auth.service';
import { MenuService } from '../../services/menu.service';
import { OrderService } from '../../services/order.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.template.html',
})
export class DashboardComponent implements OnInit {
  username = '';
  restaurantName = '';
  orders: any[] = [];
  menu: any[] = [];
  error = '';
  // Menu attributes
  newItem = { name: '', price: 0 };
  editingItem: any = null;
  // Order attributes
  selectedOrder: any = null;
  newOrderTableNumber: number | null = null;
  newOrderItem: { menu_item_id: number; quantity: number } = { menu_item_id: 0, quantity: 1 };
  showPartialPaymentForm = false;

  get canEditOrder(): boolean {
    return !['paid', 'canceled'].includes(this.selectedOrder?.status);
  }

  constructor(
    private router: Router,
    private authService: AuthService,
    private menuService: MenuService,
    private orderService: OrderService,
  ) {}

  ngOnInit(): void {
    this.authService.getCurrentUser().subscribe({
      next: (user) => {
        this.username = user.username;
        this.restaurantName = user.restaurant || '';

        this.authService.getDashboardData().subscribe({
          next: (data: any) => {
            this.username = data.username;
            this.restaurantName = data.restaurant;
            this.orders = data.orders;
            this.menu = data.menu;
          },
          error: ({ error }) => {
            this.error = error.error;
          }
        });
      },
      error: () => {
        this.router.navigate(['/login']);
      }
    });
  }


  logout(): void {
      this.authService.logout().subscribe({
          next: () => this.router.navigate(['/login']),
          error: () => alert('No se pudo cerrar sesión')
      });
  }

  // Menu Item methods
  addMenuItem(): void {
    if (!this.newItem.name || this.newItem.price <= 0) return;
    this.menuService.addItem(this.newItem).subscribe({
      next: ({ item }) => {
        this.menu.push(item);
        this.newItem = { name: '', price: 0 };
      },
      error: (err) => alert('Error al agregar: ' + err.error?.error || 'desconocido'),
    });
  }

  startEditItem(item: any): void {
    this.editingItem = { ...item }; // shallow copy
  }

  saveEdit(): void {
    if (!this.editingItem) return;
    this.menuService.updateItem(this.editingItem.id, this.editingItem).subscribe({
      next: ({ item }) => {
        const index = this.menu.findIndex(m => m.id === item.id);
        if (index !== -1) this.menu[index] = item;
        this.editingItem = null;
      },
      error: () => alert('Error al guardar cambios.'),
    });
  }

  deleteItem(id: number): void {
    const confirmed = confirm('¿Estás seguro de que deseas eliminar este ítem?');
    if (!confirmed) return;
    this.menuService.deleteItem(id).subscribe({
      next: () => {
        this.menu = this.menu.filter(item => item.id !== id);
      },
      error: () => alert('Error al eliminar.'),
    });
  }

  // Order methods
  createOrder(): void {
    if (!this.newOrderTableNumber) return;

    this.orderService.createOrder(this.newOrderTableNumber).subscribe({
      next: (order: any) => {
        this.orders.unshift(order);
        this.newOrderTableNumber = null;
      },
      error: (err) => {
        if (err.status === 409) {
          alert(`Esta mesa ya tiene una orden activa (ID: ${err.error.existing_order_id}, Estado: ${err.error.status})`);
        } else {
          alert('Error al crear orden.');
        }
      },
    });
  }

  selectOrder(order: any): void {
    this.selectedOrder = order;
    // Puedes hacer aquí una llamada para obtener todos los detalles si agregas ese endpoint.
  }

  changeOrderStatus(newStatus: string): void {
    if (!this.selectedOrder) return;

    if (newStatus === 'partial') {
      this.showPartialPaymentForm = true;
      return;
    }

    this.showPartialPaymentForm = false;

    this.orderService.updateOrderStatus(this.selectedOrder.id, newStatus).subscribe({
      next: (res: any) => {
        this.selectedOrder.status = res.new_status;
      },
      error: (err) => {
        if (err.status === 409) {
          alert(`No se puede cambiar a ${newStatus} porque ya existe otra orden activa en esta mesa.`);
        } else {
          alert('Error al actualizar estado.');
        }
      }
    });
  }

  confirmPartialPayment(): void {
    if (!this.selectedOrder) return;

    const paidItems = this.selectedOrder.items
      .filter((item: any) => item.quantity_paid > 0)
      .map((item: any) => ({
        item_id: item.id,
        quantity_paid: item.quantity_paid,
      }));

    if (paidItems.length === 0) {
      alert('Debes seleccionar al menos un producto pagado.');
      return;
    }

    this.orderService.updateOrderStatus(this.selectedOrder.id, 'partial', paidItems).subscribe({
      next: (res: any) => {
        this.selectedOrder.status = res.new_status;
        this.showPartialPaymentForm = false;
      },
      error: (err) => {
        alert(err.error?.error || 'Error al actualizar estado.');
      }
    });
  }

  getAvailableStatuses(): { value: string, label: string }[] {
    if (!this.selectedOrder) return [];

    const statuses = [
      { value: 'partial', label: 'Parcial' },
      { value: 'paid', label: 'Pagada' },
      { value: 'canceled', label: 'Cancelada' },
    ];

    // Oculta el estado actual
    const currentStatus = this.selectedOrder.status;
    let filtered = statuses.filter(s => s.value !== currentStatus);

    // Si no hay ítems, oculta las opciónes 'partial' y 'paid'
    const hasItems = this.selectedOrder.items?.length > 0;
    if (!hasItems) {
      filtered = filtered.filter(s => !['partial', 'paid'].includes(s.value));
    }

    return filtered;
  }

  addItemToOrder(): void {
    if (!this.selectedOrder) return;
    const { menu_item_id, quantity } = this.newOrderItem;
    if (!menu_item_id || quantity <= 0) return;

    this.orderService.addItemToOrder(this.selectedOrder.id, menu_item_id, quantity).subscribe({
      next: (res: any) => {
        this.selectedOrder.items = this.selectedOrder.items || [];
        this.selectedOrder.items.push(res.item);
      },
      error: () => alert('Error al agregar ítem.'),
    });
  }

  updateOrderItem(item: any): void {
    this.orderService.updateOrderItem(item.id, { quantity: item.quantity, price: item.price }).subscribe({
      next: () => {},
      error: () => alert('Error al actualizar ítem.'),
    });
  }

  deleteOrderItem(itemId: number): void {
    this.orderService.deleteOrderItem(itemId).subscribe({
      next: () => {
        this.selectedOrder.items = this.selectedOrder.items.filter((i: any) => i.id !== itemId);
      },
      error: () => alert('Error al eliminar ítem.'),
    });
  }
}
