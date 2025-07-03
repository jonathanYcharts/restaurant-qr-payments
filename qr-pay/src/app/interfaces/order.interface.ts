export interface OrderItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  quantity_paid: number;
  // Backend calculated attributes
  unpaid_quantity: number;
  is_paid: boolean;
  // Frontend attributes
  quantity_to_pay: number;
}

export interface Restaurant {
  id: number;
  name: string;
}

export interface Table {
  id: number;
  restaurant: Restaurant;
  table: number;
  status: any;
  items: OrderItem[];
}
