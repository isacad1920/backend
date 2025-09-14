// Backend API Types

// Enums matching backend
export enum Role {
  ADMIN = 'ADMIN',
  MANAGER = 'MANAGER',
  CASHIER = 'CASHIER',
  INVENTORY_CLERK = 'INVENTORY_CLERK',
  ACCOUNTANT = 'ACCOUNTANT'
}

export enum CustomerType {
  INDIVIDUAL = 'INDIVIDUAL',
  COMPANY = 'COMPANY'
}

export enum CustomerStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  BLACKLISTED = 'BLACKLISTED'
}

export enum CategoryStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE'
}

export enum Currency {
  USD = 'USD',
  SLSH = 'SLSH',
  ETB = 'ETB'
}

export enum AccountType {
  CASH_US = 'CASH_US',
  CASH_SLSH = 'CASH_SLSH',
  BANK_US = 'BANK_US',
  BANK_SLSH = 'BANK_SLSH',
  SALES_REVENUE = 'SALES_REVENUE',
  COST_OF_GOODS = 'COST_OF_GOODS',
  INVENTORY_ASSET = 'INVENTORY_ASSET',
  OTHER = 'OTHER'
}

export enum BranchOrderStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  SENT = 'SENT',
  RECEIVED = 'RECEIVED',
  CANCELLED = 'CANCELLED'
}

export enum StockRequestStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  FULFILLED = 'FULFILLED',
  REJECTED = 'REJECTED'
}

export enum ProductOrderType {
  PURCHASE = 'PURCHASE',
  SUPPLY = 'SUPPLY'
}

export enum ProductOrderStatus {
  DRAFT = 'DRAFT',
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  RECEIVED = 'RECEIVED',
  CANCELLED = 'CANCELLED'
}

export enum SaleStatus {
  DRAFT = 'DRAFT',
  PENDING = 'PENDING',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
  REFUNDED = 'REFUNDED'
}

export enum PaymentMethod {
  CASH = 'CASH',
  CARD = 'CARD',
  BANK_TRANSFER = 'BANK_TRANSFER',
  MOBILE_MONEY = 'MOBILE_MONEY',
  CREDIT = 'CREDIT'
}

export enum BackupStatus {
  PENDING = 'PENDING',
  SUCCESS = 'SUCCESS',
  FAILED = 'FAILED'
}

export enum AuditLogSeverity {
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

// Core entity interfaces
export interface User {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  role: Role;
  branchId?: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Branch {
  id: number;
  name: string;
  address?: string;
  phone?: string;
  email?: string;
  isActive: boolean;
  status: 'ACTIVE' | 'INACTIVE';
  createdAt: string;
  updatedAt: string;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Product {
  id: number;
  sku: string;
  name: string;
  barcode?: string;
  description?: string;
  costPrice: string; // Decimal as string
  sellingPrice: string; // Decimal as string
  categoryId?: number;
  category?: Category;
  createdAt: string;
  updatedAt: string;
}

export interface Stock {
  id: number;
  productId: number;
  product?: Product;
  branchId?: number;
  branch?: Branch;
  quantity: number;
  minStock?: number;
  maxStock?: number;
  lastRestocked?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Customer {
  id: number;
  customerNumber: string;
  name: string;
  phone?: string;
  email?: string;
  address?: string;
  type: CustomerType;
  creditLimit: string; // Decimal as string
  currency: Currency;
  balance?: string; // Computed balance
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Account {
  id: number;
  name: string;
  type: AccountType;
  currency: Currency;
  balance: string; // Decimal as string
  branchId?: number;
  branch?: Branch;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Sale {
  id: number;
  saleNumber: string;
  branchId: number;
  branch?: Branch;
  customerId?: number;
  customer?: Customer;
  userId: number;
  user?: User;
  totalAmount: string; // Decimal as string
  paidAmount: string; // Decimal as string
  dueAmount: string; // Decimal as string
  discount: string; // Decimal as string
  status: SaleStatus;
  notes?: string;
  items?: SaleItem[];
  payments?: Payment[];
  createdAt: string;
  updatedAt: string;
}

export interface SaleItem {
  id: number;
  saleId: number;
  productId: number;
  product?: Product;
  quantity: number;
  unitPrice: string; // Decimal as string
  discount: string; // Decimal as string
  totalPrice: string; // Decimal as string
}

export interface Payment {
  id: number;
  saleId?: number;
  accountId: number;
  account?: Account;
  amount: string; // Decimal as string
  currency: Currency;
  paymentMethod: PaymentMethod;
  reference?: string;
  userId: number;
  user?: User;
  createdAt: string;
  updatedAt: string;
}

export interface JournalEntry {
  id: number;
  referenceType: string;
  referenceId?: number;
  date: string;
  description?: string;
  lines: JournalEntryLine[];
  createdAt: string;
  updatedAt: string;
}

export interface JournalEntryLine {
  id: number;
  journalEntryId: number;
  accountId: number;
  account?: Account;
  debit: string; // Decimal as string
  credit: string; // Decimal as string
  description: string;
}

export interface StockRequest {
  id: number;
  branchId: number;
  branch?: Branch;
  requestedById: number;
  requestedBy?: User;
  approvedById?: number;
  approvedBy?: User;
  fulfilledById?: number;
  fulfilledBy?: User;
  status: StockRequestStatus;
  notes?: string;
  items: StockRequestItem[];
  createdAt: string;
  updatedAt: string;
}

export interface StockRequestItem {
  id: number;
  stockRequestId: number;
  stockId: number;
  stock?: Stock;
  requestedQty: number;
  approvedQty?: number;
  fulfilledQty?: number;
}

export interface ProductOrder {
  id: number;
  branchId: number;
  branch?: Branch;
  supplierId?: number;
  orderType: ProductOrderType;
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';
  status: ProductOrderStatus;
  expectedDeliveryDate?: string;
  totalCost: string; // Decimal as string
  notes?: string;
  items: ProductOrderItem[];
  createdAt: string;
  updatedAt: string;
}

export interface ProductOrderItem {
  id: number;
  productOrderId: number;
  productId: number;
  product?: Product;
  requestedQuantity: number;
  receivedQuantity?: number;
  estimatedCost: string; // Decimal as string
  actualCost?: string; // Decimal as string
}

export interface ExchangeRate {
  id: number;
  fromCurrency: Currency;
  toCurrency: Currency;
  rate: string; // Decimal as string
  effectiveAt: string;
  createdAt: string;
  updatedAt: string;
}

export interface Notification {
  id: number;
  userId: number;
  user?: User;
  title: string;
  body: string;
  seen: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AuditLog {
  id: number;
  userId?: number;
  user?: User;
  action: string;
  entityType?: string;
  entityId?: string;
  oldValues?: unknown;
  newValues?: unknown;
  severity: AuditLogSeverity;
  ipAddress?: string;
  userAgent?: string;
  createdAt: string;
}

export interface Backup {
  id: number;
  fileName: string;
  sizeMB: number;
  type: 'DB' | 'FILES' | 'FULL';
  status: BackupStatus;
  errorMessage?: string;
  createdById?: number;
  createdBy?: User;
  createdAt: string;
  completedAt?: string;
}

export interface SystemInfo {
  systemName: string;
  version: string;
  environment: string;
  baseCurrency: Currency;
  timezone: string;
}

// API Request/Response interfaces
export interface PaginationParams {
  page?: number;
  size?: number;
  q?: string; // Search query
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  role: Role;
  branchId?: number;
  hashedPassword: string;
}

export interface CreateBranchRequest {
  name: string;
  address?: string;
  phone?: string;
  email?: string;
}

export interface CreateProductRequest {
  sku: string;
  name: string;
  barcode?: string;
  description?: string;
  costPrice: string;
  sellingPrice: string;
  categoryId?: number;
}

export interface CreateCustomerRequest {
  customerNumber: string;
  name: string;
  phone?: string;
  email?: string;
  type: CustomerType;
  creditLimit: string;
  currency: Currency;
}

export interface CreateSaleRequest {
  branchId: number;
  customerId?: number;
  userId: number;
  items: {
    productId: number;
    quantity: number;
    unitPrice: string;
    discount?: string;
  }[];
  payments: {
    accountId: number;
    amount: string;
    method: PaymentMethod;
    currency: Currency;
  }[];
  notes?: string;
}

export interface StockAdjustmentRequest {
  stockId: number;
  adjustment: number;
  reason: string;
}

export interface AccountTransferRequest {
  fromAccountId: number;
  toAccountId: number;
  amount: string;
  currency: Currency;
  rateApplied?: number;
  note?: string;
  userId: number;
}

export interface CreateJournalEntryRequest {
  referenceType?: string;
  referenceId?: number;
  lines: {
    accountId: number;
    debit: string;
    credit: string;
    description: string;
  }[];
}

// Dashboard and analytics interfaces
export interface DashboardStats {
  totalSales: string;
  totalRevenue: string;
  totalCustomers: number;
  totalProducts: number;
  salesGrowth: number;
  revenueGrowth: number;
  customerGrowth: number;
  productGrowth: number;
}

// Lightweight summaries sourced from new unified endpoints
export interface TodaySalesSummary {
  date: string; // ISO date (YYYY-MM-DD)
  total_sales: number; // count of sales
  total_revenue: string; // decimal string revenue
  total_discount: string; // decimal string discount aggregate
  average_sale_value: string; // decimal string average
  top_selling_products: Array<{
    product_id: number;
    product_name: string;
    product_sku: string;
    total_quantity: number;
  }>;
}

export interface InventorySummary {
  total_products: number;
  low_stock_count: number;
  dead_stock_cached: number;
  total_inventory_cost: number; // numeric aggregated cost value
  total_inventory_retail: number; // numeric aggregated retail value
}

export interface UnifiedInventoryItem {
  product_id: number | null;
  name: string | null;
  sku: string | null;
  quantity: number;
  low_stock: boolean;
  dead_stock: boolean;
  category_id?: number | null;
  // Optional expansions
  avg_cost?: number;
  cost_value?: number;
  sales_timeseries?: Array<{ date: string; qty: number }>;
}

export interface SalesAnalytics {
  dailySales: { date: string; amount: string; count: number }[];
  topProducts: { productId: number; productName: string; totalSold: number; revenue: string }[];
  salesByBranch: { branchId: number; branchName: string; totalSales: string; count: number }[];
  // Optional extended fields from backend analytics service
  monthlySales?: { month: string; total: string }[];
  salesByCategory?: { categoryId: number; categoryName: string; totalSales: string }[];
  salesTrends?: { date: string; trend: number }[];
  totalSalesCount?: number;
  totalRevenueAmount?: string;
}

export interface InventoryAnalytics {
  lowStockItems: Stock[];
  topMovingProducts: { productId: number; productName: string; totalMoved: number }[];
  stockValue: string;
  categories: { categoryId: number; categoryName: string; productCount: number; stockValue: string }[];
  deadStockItems?: { productId: number; productName: string; quantity: number }[];
}

export interface FinancialReport {
  revenue: string;
  expenses: string;
  profit: string;
  profitMargin: number;
  period: string;
}

export interface TrialBalance {
  accounts: {
    accountId: number;
    accountName: string;
    accountType: AccountType;
    debitBalance: string;
    creditBalance: string;
  }[];
  totalDebits: string;
  totalCredits: string;
  isBalanced: boolean;
}

// ------------------------------------------------------
// Authentication & Permission Types (frontend-focused)
// ------------------------------------------------------

// Raw token payload returned by backend auth endpoints
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string; // usually 'bearer'
  expires_in: number; // seconds until expiry (as provided by backend)
}

// Decoded JWT claims we actually care about (extend as needed)
export interface DecodedAccessTokenClaims {
  sub: string; // user id
  role?: string;
  branch_id?: number | string;
  exp?: number; // epoch seconds
  iat?: number; // issued at
  [key: string]: unknown; // allow unknown extra claims
}

// Permission identifier string (backend currently returns flat string list)
export type PermissionCode = string; // Keep loose for now; can be narrowed to union later when backend list stabilized

// Unified session object we persist in localStorage
export interface AuthSession {
  user: User;                // current authenticated user entity
  permissions: PermissionCode[]; // effective permissions resolved for user
  tokens: AuthTokens;        // latest token set
  // Precomputed absolute expiry (ms since epoch) for quick checks / refresh scheduling
  accessTokenExpiresAt: number;
  // Optional derived claims (parsed once to avoid repeated decode cost)
  claims?: DecodedAccessTokenClaims;
}

// Shape stored in localStorage (kept versioned for forward compatibility)
export interface StoredAuthSession extends AuthSession {
  schemaVersion: 1; // bump when structure changes
}

// Narrow utility guard to differentiate stored session
export function isStoredAuthSession(value: unknown): value is StoredAuthSession {
  return !!value && typeof value === 'object' && (value as any).schemaVersion === 1 && (value as any).tokens;
}

// Lightweight login result (envelope) some flows may return (tokens + optional user)
export interface LoginResult extends AuthTokens {
  user?: User;
  permissions?: PermissionCode[];
}