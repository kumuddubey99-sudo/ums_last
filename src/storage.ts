export interface Admin {
  admin_id: string;
  admin_name: string;
  username: string;
  password?: string;
}

export interface Customer {
  customer_id: string;
  customer_name: string;
  phone_number: string;
  alternate_number: string;
  email: string;
  address: string;
  created_date: string;
  updated_date: string;
  time: string;
}

export interface CreditTransaction {
  transaction_id: string;
  customer_id: string;
  customer_name?: string;
  transaction_date: string;
  due_date: string;
  total_amount: number;
  payment_status: 'Paid' | 'Pending' | 'Overdue';
  note: string;
  created_date: string;
  updated_date: string;
  time: string;
  total_paid?: number;
  pending_amount?: number;
}

export interface CreditItem {
  item_id: string;
  transaction_id: string;
  item_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
  credited_at: string;
  created_date?: string;
  updated_date?: string;
}

export interface Payment {
  payment_id: string;
  transaction_id: string;
  customer_id: string;
  customer_name?: string;
  payment_amount: number;
  payment_date: string;
  payment_method: string;
  reference_id: string;
  created_date?: string;
  updated_date?: string;
}

export interface CustomerPerformance {
  customer_id: string;
  customer_name: string;
  total_transactions: number;
  total_credit: number;
  total_paid: number;
  pending_amount: number;
  overdue_count: number;
  performance_percentage: number;
  performance_status: 'Excellent' | 'Good' | 'Average' | 'Poor';
}

export interface OutstandingRecord {
  customer_id: string;
  customer_name: string;
  total_due: number;
  total_paid: number;
  pending_amount: number;
  due_date: string;
  status: 'Paid' | 'Pending' | 'Overdue';
}

const STORAGE_KEY_ADMINS = 'udhaar_admins';
const STORAGE_KEY_CUSTOMERS = 'udhaar_customers';
const STORAGE_KEY_TXNS = 'udhaar_txns';
const STORAGE_KEY_ITEMS = 'udhaar_items';
const STORAGE_KEY_PAYMENTS = 'udhaar_payments';

export function getTodayDate(): string {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function getCurrentTime(): string {
  const d = new Date();
  return d.toTimeString().split(' ')[0];
}

export function loadAdmins(): Admin[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_ADMINS);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveAdmins(admins: Admin[]) {
  localStorage.setItem(STORAGE_KEY_ADMINS, JSON.stringify(admins));
}

export function loadCustomers(): Customer[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_CUSTOMERS);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveCustomers(custs: Customer[]) {
  localStorage.setItem(STORAGE_KEY_CUSTOMERS, JSON.stringify(custs));
}

export function loadTransactions(): CreditTransaction[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_TXNS);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveTransactions(txns: CreditTransaction[]) {
  localStorage.setItem(STORAGE_KEY_TXNS, JSON.stringify(txns));
}

export function loadItems(): CreditItem[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_ITEMS);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveItems(items: CreditItem[]) {
  localStorage.setItem(STORAGE_KEY_ITEMS, JSON.stringify(items));
}

export function loadPayments(): Payment[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_PAYMENTS);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function savePayments(pays: Payment[]) {
  localStorage.setItem(STORAGE_KEY_PAYMENTS, JSON.stringify(pays));
}

// Next ID Generators
export function getNextId(prefix: string, list: { [key: string]: any }[], key: string): string {
  let max = 0;
  for (const item of list) {
    const val = String(item[key] || '');
    if (val.startsWith(prefix)) {
      const num = parseInt(val.slice(prefix.length), 10);
      if (!isNaN(num) && num > max) {
        max = num;
      }
    }
  }
  return `${prefix}${String(max + 1).padStart(3, '0')}`;
}

export function getNextCustomerId(): string {
  return getNextId('CUST', loadCustomers(), 'customer_id');
}

export function getNextTransactionId(): string {
  return getNextId('TXN', loadTransactions(), 'transaction_id');
}

export function getNextItemId(): string {
  return getNextId('ITEM', loadItems(), 'item_id');
}

export function getNextPaymentId(): string {
  return getNextId('PAY', loadPayments(), 'payment_id');
}

// Calculations
export function getTransactionStatus(totalAmount: number, totalPaid: number, dueDate: string): 'Paid' | 'Pending' | 'Overdue' {
  if (totalPaid >= totalAmount) {
    return 'Paid';
  }
  const today = getTodayDate();
  if (today > dueDate) {
    return 'Overdue';
  }
  return 'Pending';
}

export function calculateEnrichedTransactions(): CreditTransaction[] {
  const txns = loadTransactions();
  const custs = loadCustomers();
  const pays = loadPayments();

  const custMap = new Map<string, string>();
  custs.forEach((c) => custMap.set(c.customer_id, c.customer_name));

  return txns.map((t) => {
    const tPays = pays.filter((p) => p.transaction_id === t.transaction_id);
    const paid = tPays.reduce((sum, p) => sum + p.payment_amount, 0);
    const pending = Math.max(0, t.total_amount - paid);
    const status = getTransactionStatus(t.total_amount, paid, t.due_date);

    return {
      ...t,
      customer_name: custMap.get(t.customer_id) || t.customer_id,
      total_paid: paid,
      pending_amount: pending,
      payment_status: status,
    };
  });
}

export function calculateCustomerPerformance(customerId: string): CustomerPerformance {
  const custs = loadCustomers();
  const c = custs.find((cust) => cust.customer_id === customerId);
  const custName = c ? c.customer_name : customerId;

  const txns = loadTransactions().filter((t) => t.customer_id === customerId);
  const pays = loadPayments().filter((p) => p.customer_id === customerId);

  const totalCredit = txns.reduce((sum, t) => sum + t.total_amount, 0);
  const totalPaid = pays.reduce((sum, p) => sum + p.payment_amount, 0);
  const pendingAmount = Math.max(0, totalCredit - totalPaid);

  let overdueCount = 0;
  const today = getTodayDate();

  for (const t of txns) {
    const tPays = pays.filter((p) => p.transaction_id === t.transaction_id);
    const tPaid = tPays.reduce((sum, p) => sum + p.payment_amount, 0);
    if (tPaid < t.total_amount && today > t.due_date) {
      overdueCount++;
    }
  }

  let pct = 0;
  if (totalCredit > 0) {
    pct = Math.round((totalPaid / totalCredit) * 1000) / 10;
  } else {
    pct = txns.length === 0 ? 100 : 0;
  }

  let status: 'Excellent' | 'Good' | 'Average' | 'Poor' = 'Good';
  if (txns.length === 0) {
    status = 'Good';
  } else if (overdueCount > 0) {
    status = overdueCount > 1 ? 'Poor' : 'Average';
  } else if (pendingAmount > 0) {
    status = 'Average';
  } else if (pct >= 100) {
    status = 'Excellent';
  } else {
    status = 'Good';
  }

  return {
    customer_id: customerId,
    customer_name: custName,
    total_transactions: txns.length,
    total_credit: totalCredit,
    total_paid: totalPaid,
    pending_amount: pendingAmount,
    overdue_count: overdueCount,
    performance_percentage: Math.min(100, pct),
    performance_status: status,
  };
}

export function getAllCustomerPerformances(): CustomerPerformance[] {
  const custs = loadCustomers();
  return custs.map((c) => calculateCustomerPerformance(c.customer_id));
}

export function getOutstandingBalances(): OutstandingRecord[] {
  const custs = loadCustomers();
  const txns = loadTransactions();
  const pays = loadPayments();
  const today = getTodayDate();

  return custs.map((c) => {
    const cTxns = txns.filter((t) => t.customer_id === c.customer_id);
    const cPays = pays.filter((p) => p.customer_id === c.customer_id);

    const totalDue = cTxns.reduce((sum, t) => sum + t.total_amount, 0);
    const totalPaid = cPays.reduce((sum, p) => sum + p.payment_amount, 0);
    const pending = Math.max(0, totalDue - totalPaid);

    let latestDueDate = '-';
    let hasOverdue = false;

    for (const t of cTxns) {
      const tPays = pays.filter((p) => p.transaction_id === t.transaction_id);
      const tPaid = tPays.reduce((sum, p) => sum + p.payment_amount, 0);
      if (tPaid < t.total_amount) {
        if (today > t.due_date) {
          hasOverdue = true;
        }
        latestDueDate = t.due_date;
      }
    }

    let status: 'Paid' | 'Pending' | 'Overdue' = 'Pending';
    if (pending <= 0) {
      status = 'Paid';
    } else if (hasOverdue) {
      status = 'Overdue';
    } else {
      status = 'Pending';
    }

    return {
      customer_id: c.customer_id,
      customer_name: c.customer_name,
      total_due: totalDue,
      total_paid: totalPaid,
      pending_amount: pending,
      due_date: latestDueDate,
      status,
    };
  });
}

export function getDashboardMetrics() {
  const custs = loadCustomers();
  const txns = calculateEnrichedTransactions();
  const pays = loadPayments();

  const totalCredit = txns.reduce((sum, t) => sum + t.total_amount, 0);
  const totalPaid = pays.reduce((sum, p) => sum + p.payment_amount, 0);
  const outstanding = Math.max(0, totalCredit - totalPaid);

  const recent = [...txns].reverse().slice(0, 5);

  return {
    total_customers: custs.length,
    total_credit: totalCredit,
    total_paid: totalPaid,
    outstanding_balance: outstanding,
    recent_transactions: recent,
  };
}

export function searchSystem(query: string) {
  const q = query.trim().toLowerCase();
  if (!q) return null;

  const custs = loadCustomers().filter(
    (c) =>
      c.customer_id.toLowerCase().includes(q) ||
      c.customer_name.toLowerCase().includes(q) ||
      c.phone_number.toLowerCase().includes(q) ||
      c.email.toLowerCase().includes(q)
  );

  const txns = calculateEnrichedTransactions().filter(
    (t) =>
      t.transaction_id.toLowerCase().includes(q) ||
      (t.customer_name && t.customer_name.toLowerCase().includes(q))
  );

  const items = loadItems().filter(
    (i) =>
      i.item_id.toLowerCase().includes(q) ||
      i.item_name.toLowerCase().includes(q) ||
      i.transaction_id.toLowerCase().includes(q)
  );

  const pays = loadPayments().filter(
    (p) =>
      p.payment_id.toLowerCase().includes(q) ||
      p.transaction_id.toLowerCase().includes(q) ||
      p.payment_method.toLowerCase().includes(q)
  );

  return {
    customers: custs,
    transactions: txns,
    items,
    payments: pays,
  };
}
