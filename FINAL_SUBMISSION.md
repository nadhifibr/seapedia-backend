# Seapedia - Final Submission Documentation

This document serves as the final testing guide, API documentation, and business rules outline for the Seapedia fullstack project.

## 1. API Documentation
The backend exposes a fully documented OpenAPI specification. 
You can view and test the API directly via the Swagger UI interface:
- **Swagger UI:** `http://localhost:8000/api/docs/` *(or the respective deployed URL)*
- This interface documents every endpoint, required payload, and JWT token authorization scheme.

## 2. Demo Accounts & Seed Data
A management command (`python manage.py seed_data`) has been provided to easily generate all required roles and dummy data. 
You can log in to these accounts using the password: **`Seapedia123!`**

| Role | Username | Email | Setup Data |
|---|---|---|---|
| **Admin** | `admin` | `admin@seapedia.com` | Full admin privileges |
| **Seller** | `seller` | `seller@seapedia.com` | Has Store "Toko Samudra Jaya" + 3 Dummy Products |
| **Buyer** | `buyer` | `buyer@seapedia.com` | Has Rp 1,000,000 Wallet Balance + Default Address |
| **Driver** | `driver` | `driver@seapedia.com` | Ready to take delivery jobs |

*Also included in Seed Data:*
- **PROMO10**: 10% Discount Code
- **VOUCHER50K**: Rp 50.000 Fixed Voucher Code

---

## 3. Business Rules Documentation

### 3.1 Single-Store Checkout Behavior
- The `CartItemView` (`apps/cart/views.py`) strictly enforces that a cart can only belong to **one store**.
- When adding a product, if the cart already has a `store` assigned and the new product belongs to a different store, it returns a `400 Bad Request` with an error: *"Cart already contains items from [Store]. Cannot add items from [New Store]."*
- Once the cart is cleared or checked out, the cart's store association is reset.

### 3.2 Discount Combination Rule & PPN 12% Rule
- **Discounts:** Only **one** discount code (Promo or Voucher) can be applied per checkout. The `CheckoutSummarySerializer` only accepts a single `discount_code` parameter. For Vouchers (Fixed Value), a dynamic rule requires the `subtotal` to be at least **2x the discount value** (e.g. 50k voucher requires 100k subtotal).
- **PPN 12%:** As implemented in `apps/orders/views.py`, PPN (Tax) is calculated **after** the discount is deducted.
  - Formula: `tax_amount = (subtotal - discount_amount) * 12%`

### 3.3 Driver Earning Rule
- During Checkout, a `DeliveryFee` is calculated based on the delivery SLA (Instant, Next Day, Regular).
- This fee is stored in the `DeliveryJob` model as `driver_earning`.
- When a Driver successfully marks a delivery as **DONE** (`/api/deliveries/X/complete/`), the exact `driver_earning` amount is automatically added to the `total_earnings` field of their `DriverProfile`.

### 3.4 Overdue SLA & Time Simulation
- Each order has an `overdue_at` timestamp calculated upon checkout (Instant: +1 Day, Next Day: +2 Days, Regular: +5 Days).
- **Simulation:** Admin can manually shift the `overdue_at` timestamp backwards to simulate the passing of time using the endpoint `/api/admin_panel/simulate-time/` (providing `days`).
- **Trigger:** Admin can then call `/api/admin_panel/trigger-overdue/` to run the cron job manually, which immediately refunds any non-completed order whose `overdue_at` has passed.

---

## 4. Security Measures (Hardening)

1. **SQL Injection (SQLi):** 
   - All database queries strictly utilize the Django ORM (e.g. `.filter()`, `.get_or_create()`). No raw SQL execution (`.raw()`) is used, fully preventing SQLi attacks.
2. **Cross-Site Scripting (XSS) & Public Comments:** 
   - Public App Reviews (`apps/reviews/serializers.py`) are sanitized upon saving using the `bleach` library to strip `<script>` tags and malicious attributes (e.g., `onmouseover`).
   - The React Next.js frontend inherently escapes all `{data}` outputs to block XSS during rendering.
3. **Input Validation:** 
   - Strict Backend Validators: `MinValueValidator` ensures price $\ge 100$, stock $\ge 1$, quantity $\ge 1$.
   - Regex Validation: Delivery phone numbers must strictly match `^\+?1?\d{9,15}$`.
   - Django's `UnicodeUsernameValidator` restricts invalid characters in usernames.
4. **Session Behavior & Role-Based Access Control (RBAC):**
   - **Active Role Isolation:** The backend `apps/users/permissions.py` implements custom permission classes (`IsActiveBuyer`, `IsActiveSeller`, etc.) that inspect the JWT token's `active_role` payload. A multi-role user logged in as a Buyer cannot access Seller API endpoints.
   - **Frontend Routing:** `ProtectedRoute.tsx` explicitly checks `user.active_role`. Manual URL manipulation (e.g. typing `/dashboard/seller` while logged in as a Buyer) is instantly blocked.
   - **Logout:** Calling `/auth/logout/` explicitly blacklists the JWT `refresh_token` in the database, preventing stolen token reuse.

---

## 5. End-to-End Testing Guide (Demo Flow)

1. **Login as Buyer:** 
   - Go to `/auth/login`, enter `buyer` / `Seapedia123!`.
   - Role Select: Choose `BUYER`.
2. **Shop & Checkout:**
   - Go to Public Store, find "Toko Samudra Jaya", and add "Pancingan Shimano" to cart.
   - Go to Cart -> Proceed to Checkout.
   - Enter `PROMO10` as a discount code. Select "Next Day" delivery. 
   - Verify Tax is exactly 12% of the discounted subtotal. Place Order.
3. **Process Order (Seller):**
   - Click `Logout`. Login as `seller` / `Seapedia123!`. Select `SELLER` role.
   - Go to "View Store Orders". Click "Process Order" on the new order.
4. **Deliver Order (Driver):**
   - Click `Logout`. Login as `driver` / `Seapedia123!`. Select `DRIVER` role.
   - Go to Dashboard, click "Take Job" on the available order.
   - Click "Complete Delivery". The driver's earnings will increase by the exact delivery fee!
