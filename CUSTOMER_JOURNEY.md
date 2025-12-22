# 🛍️ Customer Journey - Complete Flow Documentation

## Overview
This document outlines the complete customer journey in the Bhrikutimandap e-commerce platform, from registration through order placement and management.

---

## 1️⃣ Customer Registration & Login

### 1.1 Registration
**URL:** `http://localhost:8000/accounts/register/`

**Flow:**
1. Click "Register" link in header/navigation
2. Fill registration form:
   - Email
   - Full Name
   - Password
   - Confirm Password
3. Click "Create Account" button
4. System sends activation email (in development, check console)
5. Click activation link in email
6. Account activated, redirect to login

**Expected Outcome:**
- ✅ Account created
- ✅ User receives activation email
- ✅ After activation, user can login

**Issues to Check:**
- [ ] Registration form validation working?
- [ ] Email activation link valid?
- [ ] Redirect after activation correct?

---

### 1.2 Customer Login
**URL:** `http://localhost:8000/accounts/login/`

**Flow:**
1. Enter email and password
2. Click "Sign In" button
3. If "Remember Me" checked, session persists
4. Redirected to home page (customer view)

**Expected Outcome:**
- ✅ Successfully logged in
- ✅ Navigation shows "Hello, [Name]" with dropdown menu
- ✅ Cart button visible in header
- ✅ Can access customer dashboard

**Issues to Check:**
- [ ] Login credentials validated correctly?
- [ ] Session management working?
- [ ] Redirect URL correct?

---

## 2️⃣ Customer Profile Management

### 2.1 View Profile
**URL:** `http://localhost:8000/customer/profile/`

**Flow:**
1. Click user dropdown menu (top-right)
2. Select "My Profile"
3. View current profile information

**Visible Fields:**
- Email
- First Name
- Last Name
- Phone Number
- Company Name
- User Role (Customer/Agent toggle)

**Expected Outcome:**
- ✅ All profile information displays correctly
- ✅ Cannot edit directly from this page (read-only view)

**Issues to Check:**
- [ ] All fields display correctly?
- [ ] Data saved from registration appears?

---

### 2.2 Edit Profile
**URL:** `http://localhost:8000/customer/profile/` (Edit button)

**Flow:**
1. From profile page, click "Edit Profile" button
2. Modify any field:
   - First Name
   - Last Name
   - Phone Number
   - Company Name
3. Click "Save Changes"

**Expected Outcome:**
- ✅ Changes saved successfully
- ✅ Confirmation message displayed
- ✅ Profile updated in database

**Issues to Check:**
- [ ] Edit form loads existing data?
- [ ] Form validation working?
- [ ] Changes persisted after page refresh?
- [ ] Confirmation message shown?

---

### 2.3 Manage Addresses
**URL:** `http://localhost:8000/customer/addresses/`

**Flow:**
1. Click dropdown menu → "Addresses"
2. View list of saved addresses
3. Options for each address:
   - **Edit**: Modify address details
   - **Delete**: Remove address
   - **Set as Default**: Use for future orders

**Adding New Address:**
1. Click "Add New Address" button
2. Fill form:
   - Address Line 1
   - Address Line 2 (optional)
   - City
   - State
   - Postal Code
   - Country
3. Click "Save Address"

**Expected Outcome:**
- ✅ New address saved
- ✅ Address appears in list
- ✅ Can set as default
- ✅ Can edit and delete addresses

**Issues to Check:**
- [ ] Address form validation working?
- [ ] Default address marked correctly?
- [ ] Delete confirmation shown?
- [ ] Address list displays all addresses?

---

### 2.4 Manage Payment Methods
**URL:** `http://localhost:8000/customer/payment-methods/`

**Flow:**
1. Click dropdown menu → "Payment Methods"
2. View saved payment methods
3. Options:
   - **Add New**: Add payment method
   - **Delete**: Remove payment method
   - **Set as Default**: Use for future purchases

**Adding Payment Method:**
1. Click "Add New Payment Method"
2. Fill form:
   - Card Holder Name
   - Card Number
   - CVV
   - Expiry Date
3. Click "Save"

**Expected Outcome:**
- ✅ Payment method saved (last 4 digits visible)
- ✅ Can set as default
- ✅ Can delete payment methods

**Issues to Check:**
- [ ] Card validation working (last 4 digits only)?
- [ ] Default payment method marked?
- [ ] Can set new default?

---

## 3️⃣ Product Search & Browsing

### 3.1 Home Page Search
**URL:** `http://localhost:8000/` (home page)

**Flow:**
1. Scroll to "Search & Filter Section" on home page
2. Enter search term in "Search by product name" field
3. Options:
   - Filter by Price: Low to High / High to Low
   - Filter by Supplier: Select specific agent/supplier
4. Click "Filter" button
5. View filtered results

**Expected Outcome:**
- ✅ Search results display below
- ✅ Results filtered by name, price, supplier
- ✅ Can clear filters with "X" button
- ✅ Active filters shown with tags

**Issues to Check:**
- [ ] Search box working correctly?
- [ ] Price sorting working?
- [ ] Supplier filter working?
- [ ] Results update correctly?

---

### 3.2 Product List Page
**URL:** `http://localhost:8000/products/`

**Flow:**
1. Click "Browse Products" or navigate to products page
2. View all products in grid
3. For each product:
   - Product image
   - Product name
   - Price
   - Supplier name
   - Rating/Reviews
   - "Add to Cart" button
   - "Quick View" icon

**Actions:**
- Click product → Go to product detail page
- Click heart icon → Add to wishlist
- Click cart icon → Add to cart directly
- Click search icon → Quick view modal

**Expected Outcome:**
- ✅ All products display correctly
- ✅ Product images load
- ✅ Prices display with currency
- ✅ Supplier information visible
- ✅ Quick actions work

**Issues to Check:**
- [ ] Product images loading?
- [ ] Prices displayed correctly?
- [ ] Supplier names correct?
- [ ] Add to cart working from list?

---

### 3.3 Product Detail Page
**URL:** `http://localhost:8000/product/{product_id}/`

**Flow:**
1. Click product name or image from list
2. View detailed product page:
   - Large product image
   - Product name
   - Price
   - Supplier information
   - Product description
   - Stock status
   - Ratings and reviews
3. Quantity selector
4. "Add to Cart" button
5. "Add to Wishlist" button

**Actions:**
1. Change quantity (if in stock)
2. Click "Add to Cart" → Item added
3. Click wishlist icon → Added to wishlist

**Expected Outcome:**
- ✅ All product information visible
- ✅ Can adjust quantity
- ✅ "Out of Stock" message if no inventory
- ✅ Add to cart works
- ✅ Wishlist toggle works

**Issues to Check:**
- [ ] Product image displays correctly?
- [ ] Description loads fully?
- [ ] Stock status accurate?
- [ ] Quantity selector works?
- [ ] Reviews/ratings display?

---

## 4️⃣ Shopping Cart Management

### 4.1 Add to Cart
**URL:** Product page or product list

**Flow - From Product Detail:**
1. Select quantity
2. Click "Add to Cart" button
3. Notification: "Added to cart"
4. Can continue shopping or go to cart

**Flow - From Product List:**
1. Click cart icon on product card
2. Item added with default quantity (1)

**Expected Outcome:**
- ✅ Item added to cart
- ✅ Success notification shown
- ✅ Cart count in header increases
- ✅ Can view in cart

**Issues to Check:**
- [ ] Notification appears and disappears?
- [ ] Cart count updates in header?
- [ ] Item actually in cart?

---

### 4.2 View Cart
**URL:** `http://localhost:8000/cart/`

**Flow:**
1. Click "Cart" button in header or navigation
2. View cart items:
   - Product image
   - Product name
   - Supplier
   - Price per item
   - Quantity selector
   - Total price
   - Remove button
3. Subtotal shown
4. "Continue Shopping" and "Checkout" buttons

**Expected Outcome:**
- ✅ All items display correctly
- ✅ Prices calculate correctly
- ✅ Subtotal accurate
- ✅ Can see supplier for each item

**Issues to Check:**
- [ ] Cart displays all items?
- [ ] Prices correct?
- [ ] Subtotal calculation accurate?
- [ ] Images loading?

---

### 4.3 Edit Cart Items
**URL:** `http://localhost:8000/cart/`

**Flow:**
1. In cart, modify quantity:
   - Click "+" to increase
   - Click "-" to decrease
   - Or type quantity directly
2. Price updates automatically
3. Subtotal recalculates

**Or Remove Item:**
1. Click "Remove" button on item
2. Item deleted from cart
3. Subtotal updates

**Expected Outcome:**
- ✅ Quantity updates in real-time
- ✅ Price recalculates correctly
- ✅ Item removed successfully
- ✅ Subtotal updates

**Issues to Check:**
- [ ] Quantity input accepts only valid numbers?
- [ ] Price updates instantly?
- [ ] Remove button confirms deletion?
- [ ] Cart persists after page refresh?

---

## 5️⃣ Checkout Process

### 5.1 Proceed to Checkout
**URL:** `http://localhost:8000/checkout/`

**Flow:**
1. From cart, click "Checkout" button
2. Checkout page loads with:
   - Order Summary (items, subtotal)
   - Shipping Address selector
   - Payment Method selector
   - Order Total
3. "Place Order" button

**Expected Outcome:**
- ✅ Cart items visible
- ✅ Saved addresses appear in dropdown
- ✅ Saved payment methods appear in dropdown
- ✅ Correct total displayed
- ✅ Can select address and payment

**Issues to Check:**
- [ ] Addresses loading from profile?
- [ ] Payment methods loading?
- [ ] Default address pre-selected?
- [ ] Order total correct?

---

### 5.2 Select Shipping Address
**URL:** `http://localhost:8000/checkout/`

**Flow:**
1. In "Shipping Address" section
2. Select address from dropdown
3. Address details display below
4. Can click "Add New Address" to create new one

**Expected Outcome:**
- ✅ Existing addresses show in dropdown
- ✅ Selected address displays fully
- ✅ "Add New Address" form works
- ✅ Default address pre-selected

**Issues to Check:**
- [ ] Addresses populate correctly?
- [ ] Selected address highlighted?
- [ ] Address details match profile?
- [ ] "Add New Address" form works?

---

### 5.3 Select Payment Method
**URL:** `http://localhost:8000/checkout/`

**Flow:**
1. In "Payment Method" section
2. Select payment method from dropdown
3. Method details display (last 4 digits)
4. Can click "Add New Payment Method" to create new one

**Expected Outcome:**
- ✅ Payment methods show in dropdown
- ✅ Selected method displays
- ✅ Default method pre-selected
- ✅ "Add New Method" form works

**Issues to Check:**
- [ ] Payment methods loading?
- [ ] Selected method highlighted?
- [ ] Payment details masked correctly (last 4 digits)?
- [ ] "Add New Payment Method" works?

---

### 5.4 Place Order
**URL:** `http://localhost:8000/checkout/`

**Flow:**
1. Verify all details:
   - Cart items correct
   - Shipping address selected
   - Payment method selected
2. Click "Place Order" button
3. Order processing...
4. Redirect to order confirmation page

**Expected Outcome:**
- ✅ Order created in database
- ✅ Order ID generated
- ✅ Confirmation page shows:
   - Order number
   - Items ordered
   - Shipping address
   - Estimated delivery date
   - Order status (pending)
5. Cart cleared
6. Email confirmation sent

**Issues to Check:**
- [ ] Order created successfully?
- [ ] Order ID displayed?
- [ ] All order details correct?
- [ ] Cart emptied?
- [ ] Confirmation email sent?
- [ ] Order status shows "pending"?

---

## 6️⃣ Order Management

### 6.1 View Order History
**URL:** `http://localhost:8000/customer/orders/`

**Flow:**
1. Click dropdown menu → "My Orders"
2. View list of all orders:
   - Order ID
   - Date ordered
   - Items count
   - Total amount
   - Order status (Pending, Processing, Shipped, Delivered)
3. Click order → View order detail

**Expected Outcome:**
- ✅ All orders display in reverse chronological order
- ✅ Status badges show correct status
- ✅ Amounts display with currency
- ✅ Can click to see details

**Issues to Check:**
- [ ] All orders showing?
- [ ] Statuses correct?
- [ ] Dates formatted properly?
- [ ] Can navigate to details?

---

### 6.2 View Order Details
**URL:** `http://localhost:8000/order/{order_id}/`

**Flow:**
1. From order list, click order
2. View complete order information:
   - Order ID
   - Order date
   - Items ordered (with quantities, prices)
   - Subtotal
   - Tax (if applicable)
   - Shipping cost
   - Total amount
   - Shipping address
   - Estimated delivery date
3. **Delivery Information Section** (if order assigned to delivery partner):
   - Delivery partner name
   - Contact phone/email
   - Assigned vehicle (if available)
   - Current delivery status
   - Tracking timeline with updates

**Expected Outcome:**
- ✅ All order items visible
- ✅ Prices calculate correctly
- ✅ Shipping address matches checkout
- ✅ Delivery info shows if order in delivery
- ✅ Status updates visible
- ✅ Timeline shows delivery progress

**Issues to Check:**
- [ ] All order items displaying?
- [ ] Prices and totals correct?
- [ ] Delivery information showing (after agent assigns)?
- [ ] Status timeline accurate?
- [ ] Delivery partner info complete?

---

### 6.3 Request Return (If Applicable)
**URL:** `http://localhost:8000/order/{order_id}/` → "Request Return" button

**Flow:**
1. On order detail, click "Request Return" on specific item
2. Select reason for return:
   - Defective product
   - Wrong item received
   - Not as described
   - Changed mind
   - Other
3. Add return notes
4. Click "Submit Return Request"

**Expected Outcome:**
- ✅ Return request created
- ✅ Status shows "Return Requested"
- ✅ Notification sent to seller/agent
- ✅ Agent can view in "Returns" section

**Issues to Check:**
- [ ] Return form loads?
- [ ] Reasons populate?
- [ ] Return request saves?
- [ ] Status updates?

---

## 7️⃣ Wishlist Management

### 7.1 Add to Wishlist
**URL:** Product page or product list

**Flow:**
1. Click heart icon on product
2. Item added to wishlist
3. Heart fills (indicates in wishlist)

**Expected Outcome:**
- ✅ Item added to wishlist
- ✅ Heart icon changes (filled vs outlined)
- ✅ Can view in wishlist page

**Issues to Check:**
- [ ] Heart icon changes?
- [ ] Item actually added?
- [ ] Works from both detail and list pages?

---

### 7.2 View Wishlist
**URL:** `http://localhost:8000/customer/wishlist/`

**Flow:**
1. Click dropdown menu → "Wishlist"
2. View all wishlisted products:
   - Product image
   - Product name
   - Price
   - Supplier
   - "Add to Cart" button
   - "Remove from Wishlist" button

**Expected Outcome:**
- ✅ All wishlisted items display
- ✅ Can add to cart directly
- ✅ Can remove from wishlist
- ✅ Empty state message if no items

**Issues to Check:**
- [ ] All wishlist items showing?
- [ ] Add to cart works?
- [ ] Remove button works?
- [ ] Empty state displays when no items?

---

## Summary Checklist

### Critical Customer Functions
- [ ] Registration and email activation
- [ ] Login/Logout
- [ ] Profile creation and editing
- [ ] Address management (add, edit, delete, set default)
- [ ] Payment method management
- [ ] Product search and filtering
- [ ] Product browsing
- [ ] Add to cart (from both list and detail)
- [ ] View and edit cart
- [ ] Checkout process
- [ ] Place order
- [ ] View order history
- [ ] View order details with delivery info
- [ ] Request returns
- [ ] Wishlist management

### Key Validations
- [ ] Prices calculate correctly throughout journey
- [ ] Cart persists across sessions
- [ ] Order data saved accurately
- [ ] Email confirmations sent
- [ ] Status updates reflect correctly
- [ ] Delivery information shows after agent assignment
- [ ] All role-based redirects work

---

## Common Issues Found
*(To be filled after testing)*

| Issue # | Page | Issue Description | Status |
|---------|------|-------------------|--------|
| 1 | Search | Trending product div instead of search div | ❌ FOUND |
|  |  |  |  |
|  |  |  |  |

---

**Last Updated:** December 21, 2025
**Tested By:** [Your Name]
**Environment:** Development (localhost:8000)
