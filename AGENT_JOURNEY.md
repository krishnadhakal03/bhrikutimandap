# 👨‍💼 Agent Journey - Complete Flow Documentation

## Overview
This document outlines the complete agent (supplier/seller) journey in the Bhrikutimandap platform, from dashboard access through order fulfillment, delivery management, and analytics.

---

## 1️⃣ Agent Login & Access

### 1.1 Login as Agent
**URL:** `http://localhost:8000/accounts/login/`

**Flow:**
1. Enter email and password for agent account
2. Click "Sign In"
3. System checks user role (Agent flag in profile)
4. Redirected to agent dashboard

**Expected Outcome:**
- ✅ Successfully logged in as agent
- ✅ Navigation shows agent portal (different from customer)
- ✅ Agent-specific menu visible in sidebar
- ✅ Dashboard displays agent metrics

**Issues to Check:**
- [ ] Login validation for agent role?
- [ ] Correct role-based redirect?
- [ ] Agent sidebar visible?
- [ ] Agent-specific data loaded?

---

### 1.2 Switch to Agent Role (If Dual Role)
**URL:** `http://localhost:8000/accounts/toggle-role/`

**Flow:**
1. If user has both customer and agent roles
2. Click dropdown menu → "Switch to Agent"
3. Page reloads with agent view

**Expected Outcome:**
- ✅ Role switched successfully
- ✅ Agent portal loads
- ✅ Agent-specific data visible
- ✅ Can switch back to customer role

**Issues to Check:**
- [ ] Role toggle button visible for dual-role users?
- [ ] Role switch works correctly?
- [ ] Data scoped to correct role?

---

## 2️⃣ Agent Dashboard

### 2.1 Dashboard Overview
**URL:** `http://localhost:8000/agent/dashboard/`

**Flow:**
1. Agent logs in or switches to agent role
2. Dashboard auto-loads
3. View key metrics:
   - Total Products
   - Total Orders
   - Pending Orders
   - Total Sales (Revenue)
   - Products in Stock
   - Low Stock Alerts
   - Recent Orders
   - Sales Trend Graph

**Dashboard Sections:**
1. **Key Metrics Cards**
   - Display current statistics
   - Color-coded for status
   - Trending indicators (up/down arrows)

2. **Recent Orders Table**
   - Order ID
   - Customer Name
   - Order Date
   - Items Count
   - Total Amount
   - Status
   - Action button → View details

3. **Sales Chart/Graph**
   - Revenue trend over time
   - Visual representation

**Expected Outcome:**
- ✅ All metrics load correctly
- ✅ Numbers accurate based on orders/products
- ✅ Recent orders display
- ✅ Chart loads and displays data
- ✅ Can click order to view details

**Issues to Check:**
- [ ] All metrics calculating correctly?
- [ ] Recent orders showing?
- [ ] Chart rendering properly?
- [ ] Numbers updating in real-time?
- [ ] Navigation to orders works?

---

## 3️⃣ Agent Profile Management

### 3.1 View Agent Profile
**URL:** `http://localhost:8000/agent/profile/`

**Flow:**
1. Click "Profile" in agent sidebar or dropdown menu
2. View current profile information:
   - Email
   - Name
   - Company Name
   - Phone Number
   - Business Address
   - Logo (if uploaded)
   - Business Banner (if uploaded)
   - Trademark/Certification (if uploaded)
   - Status (Active/Inactive)

**Expected Outcome:**
- ✅ All profile information displays
- ✅ Images load correctly
- ✅ Status shows current state
- ✅ Can see all verification documents

**Issues to Check:**
- [ ] Profile data complete?
- [ ] Images uploading and displaying?
- [ ] All documents visible?
- [ ] Status shows correctly?

---

### 3.2 Edit Agent Profile
**URL:** `http://localhost:8000/agent/profile/edit/`

**Flow:**
1. From profile page, click "Edit Profile"
2. Edit form with fields:
   - Name
   - Company Name
   - Phone Number
   - Business Address
   - Logo (image upload)
   - Business Banner (image upload)
   - Trademark/Certification (image upload)
3. Click "Save Changes"

**Expected Outcome:**
- ✅ Form loads with existing data
- ✅ Can upload/change images
- ✅ Changes save successfully
- ✅ Images replace old ones
- ✅ Confirmation message shown
- ✅ Profile page updates

**Issues to Check:**
- [ ] Form pre-fills existing data?
- [ ] Image uploads working?
- [ ] File size/type validation?
- [ ] Changes persist?
- [ ] Confirmation shown?

---

## 4️⃣ Product Management

### 4.1 View Products List
**URL:** `http://localhost:8000/agent/products/`

**Flow:**
1. Click "Products" in agent sidebar
2. View table of all agent's products:
   - Product ID
   - Product Name
   - Category
   - Price
   - Stock Quantity
   - Status (Active/Inactive)
   - Created Date
   - Action buttons (Edit, Delete, View)

**Features:**
- Search/filter by product name
- Sort by columns
- Pagination (if many products)

**Expected Outcome:**
- ✅ All products display
- ✅ Correct data for each product
- ✅ Can search and filter
- ✅ Can navigate to edit/delete
- ✅ Can view product detail

**Issues to Check:**
- [ ] All products showing?
- [ ] Data accurate?
- [ ] Search working?
- [ ] Pagination working (if applicable)?
- [ ] Action buttons functional?

---

### 4.2 Add New Product
**URL:** `http://localhost:8000/agent/product/add/`

**Flow:**
1. Click "Add Product" button
2. Fill product form:
   - Product Name (required)
   - Category (dropdown)
   - Description
   - Price (required)
   - Stock Quantity (required)
   - Product Image (upload)
   - Status (Active/Inactive)
   - Meta tags (optional)
3. Click "Save Product"

**Expected Outcome:**
- ✅ Product created successfully
- ✅ Assigned to agent automatically
- ✅ Image uploads and displays
- ✅ Product visible in products list
- ✅ Product searchable
- ✅ Status set correctly

**Issues to Check:**
- [ ] Form validation working?
- [ ] Image upload working?
- [ ] Product saves to database?
- [ ] Product immediately searchable?
- [ ] Default status correct?
- [ ] Confirmation message shown?

---

### 4.3 Edit Product
**URL:** `http://localhost:8000/agent/product/{product_id}/edit/`

**Flow:**
1. From products list, click "Edit" button
2. Form loads with existing product data
3. Modify any field:
   - Name
   - Category
   - Description
   - Price
   - Stock Quantity
   - Image (replace or keep)
   - Status
4. Click "Save Changes"

**Expected Outcome:**
- ✅ Form pre-fills with existing data
- ✅ Can change any field
- ✅ Image can be replaced
- ✅ Changes save successfully
- ✅ Changes reflected in products list
- ✅ Confirmation shown

**Issues to Check:**
- [ ] Existing data loads?
- [ ] All fields editable?
- [ ] Image replacement works?
- [ ] Changes persist?
- [ ] List updates immediately?

---

### 4.4 Delete Product
**URL:** `http://localhost:8000/agent/product/{product_id}/delete/`

**Flow:**
1. From products list, click "Delete" button
2. Confirmation dialog appears: "Are you sure?"
3. Click "Delete" to confirm
4. Product removed from list

**Expected Outcome:**
- ✅ Confirmation shown before delete
- ✅ Product removed from database
- ✅ Removed from products list
- ✅ Cannot find product on customer side
- ✅ Confirmation message shown

**Issues to Check:**
- [ ] Confirmation dialog shows?
- [ ] Product actually deleted?
- [ ] List updates immediately?
- [ ] Deleted product not searchable?

---

## 5️⃣ Stock Management

### 5.1 Stock Overview
**URL:** `http://localhost:8000/agent/stock/`

**Flow:**
1. Click "Stock" in agent sidebar
2. View stock overview:
   - Product Name
   - Current Stock Quantity
   - Stock Status (In Stock, Low Stock, Out of Stock)
   - Alert Status (if alerts set)
   - Actions (Adjust, View Alerts)

**Color Coding:**
- Green: Healthy stock
- Yellow: Low stock (near alert level)
- Red: Out of stock or critical

**Expected Outcome:**
- ✅ All products with stock visible
- ✅ Current quantities accurate
- ✅ Status badges correct
- ✅ Color coding helps identify issues
- ✅ Can adjust stock directly

**Issues to Check:**
- [ ] Stock quantities accurate?
- [ ] Status badges correct?
- [ ] Color coding working?
- [ ] All products showing?
- [ ] Adjust button accessible?

---

### 5.2 Adjust Stock
**URL:** `http://localhost:8000/agent/stock/{product_id}/adjust/`

**Flow:**
1. From stock overview, click "Adjust" for a product
2. Or from products list, select product
3. Adjust Stock Form:
   - Current Quantity (display only)
   - New Quantity (input)
   - Reason for adjustment (dropdown):
     - Stock received
     - Stock correction
     - Damaged/Return
     - Manual adjustment
   - Notes (optional)
4. Click "Save Adjustment"

**Expected Outcome:**
- ✅ Current quantity shows correctly
- ✅ Can enter new quantity
- ✅ Adjustment reason recorded
- ✅ Change saves immediately
- ✅ Stock overview updates
- ✅ Adjustment logged for records

**Issues to Check:**
- [ ] Current quantity displays?
- [ ] New quantity accepts input?
- [ ] Adjustment saves correctly?
- [ ] Stock overview updates?
- [ ] Negative quantities prevented?
- [ ] History of adjustments available?

---

### 5.3 Stock Alerts
**URL:** `http://localhost:8000/agent/stock/alerts/`

**Flow:**
1. Click "Stock Alerts" in agent sidebar
2. View current stock alerts:
   - Product Name
   - Current Stock
   - Alert Threshold
   - Status (Alert triggered/Not triggered)
   - Action buttons (Edit, Remove)

**Setting Alert:**
1. Click "Add Alert" for product
2. Form with fields:
   - Product (pre-selected if from detail)
   - Alert Threshold Quantity (e.g., alert when stock falls below 10)
3. Click "Set Alert"

**Expected Outcome:**
- ✅ Alerts display current settings
- ✅ Can set/edit threshold
- ✅ Alerts trigger when stock low
- ✅ Agent notified when threshold reached
- ✅ Can remove alerts
- ✅ Alerts show in dashboard

**Issues to Check:**
- [ ] Alert threshold saves?
- [ ] Alert triggers when stock low?
- [ ] Notifications sent to agent?
- [ ] Can edit threshold?
- [ ] Can remove alerts?
- [ ] Alerts reflect in dashboard?

---

## 6️⃣ Sales Management

### 6.1 View Sales
**URL:** `http://localhost:8000/agent/sales/`

**Flow:**
1. Click "Sales" in agent sidebar
2. View sales transactions table:
   - Order ID
   - Customer Name
   - Sale Date
   - Items Count
   - Total Amount
   - Payment Status
   - Order Status
   - Action buttons

**Features:**
- Filter by date range
- Filter by status
- Sort by columns
- Search by customer name or order ID

**Expected Outcome:**
- ✅ All sales/orders display
- ✅ Can search and filter
- ✅ Correct data for each sale
- ✅ Sorting works
- ✅ Date range filtering works
- ✅ Can view order details

**Issues to Check:**
- [ ] All sales showing?
- [ ] Data accurate?
- [ ] Filters working?
- [ ] Sorting working?
- [ ] Payment status correct?
- [ ] Order status correct?

---

### 6.2 Record Manual Sale
**URL:** `http://localhost:8000/agent/sales/record/`

**Flow:**
1. Click "Record Sale" button
2. Manual Sales Form:
   - Customer Name
   - Amount
   - Payment Method
   - Date (auto-filled with today)
   - Notes (optional)
3. Click "Record"

**Expected Outcome:**
- ✅ Sale recorded in system
- ✅ Appears in sales list
- ✅ Included in revenue calculations
- ✅ Shows in dashboard metrics
- ✅ Confirmation shown

**Issues to Check:**
- [ ] Form validation working?
- [ ] Sale saves correctly?
- [ ] Appears in sales list immediately?
- [ ] Included in revenue metrics?

---

## 7️⃣ Order Management

### 7.1 View All Orders
**URL:** `http://localhost:8000/agent/orders/`

**Flow:**
1. Click "Orders" in agent sidebar
2. View all orders containing agent's products:
   - Order ID
   - Customer Name
   - Order Date
   - Items Count
   - Total Amount
   - Order Status
   - Delivery Status (if applicable)
   - Action buttons

**Statuses:**
- Pending: Awaiting agent confirmation
- Processing: Agent preparing shipment
- Shipped: Order dispatched
- Delivered: Order delivered to customer
- Cancelled: Order cancelled

**Expected Outcome:**
- ✅ All relevant orders display
- ✅ Correct status badges
- ✅ Can click to view details
- ✅ Can filter by status
- ✅ Can search by order ID/customer

**Issues to Check:**
- [ ] All orders showing?
- [ ] Statuses accurate?
- [ ] Can filter by status?
- [ ] Can search?
- [ ] Pagination working (if many orders)?

---

### 7.2 View Incoming Orders (New Orders)
**URL:** `http://localhost:8000/agent/orders/incoming/`

**Flow:**
1. Click "Incoming Orders" (or check notification badge)
2. View orders with status "Pending" (awaiting agent action)
3. For each order:
   - Order ID
   - Customer Name
   - Order Date
   - Items from this agent
   - Total Amount
   - "View Details" button
   - "Accept & Process" button

**Expected Outcome:**
- ✅ Only pending orders show
- ✅ Agent can quickly identify new orders
- ✅ Can view details
- ✅ Can mark as processing
- ✅ Badge shows count of incoming

**Issues to Check:**
- [ ] Only pending orders showing?
- [ ] New orders appear immediately?
- [ ] Notification badge accurate?
- [ ] Can view and accept?

---

### 7.3 View Order Details
**URL:** `http://localhost:8000/agent/orders/{order_id}/`

**Flow:**
1. Click "View" or order ID
2. Order Detail Page shows:
   - **Order Information**
     - Order ID
     - Order Date
     - Customer Name & Contact
     - Delivery Address
   
   - **Order Items**
     - Item image
     - Item name
     - Quantity ordered
     - Price per item
     - Total for item
     - (Only agent's items, if order has multiple suppliers)
   
   - **Pricing Summary**
     - Subtotal
     - Tax
     - Shipping Cost
     - Total Amount
   
   - **Delivery Information** (if assigned)
     - Assigned Delivery Partner
     - Partner Contact Info
     - Assigned Vehicle Details
     - Current Delivery Status
     - Last Updated Time
     - Tracking Timeline
   
   - **Order Status**
     - Current Status badge
     - "Update Status" button
     - Status history/timeline
   
   - **Actions Available:**
     - Update Order Status
     - Assign Delivery Partner
     - View Delivery Tracking
     - Return Management (if applicable)

**Expected Outcome:**
- ✅ All order information visible
- ✅ Only agent's items shown
- ✅ Pricing calculations correct
- ✅ Delivery info shows if assigned
- ✅ Can update status
- ✅ Can assign delivery partner
- ✅ Can view delivery tracking

**Issues to Check:**
- [ ] All order data loading?
- [ ] Only agent's items showing?
- [ ] Prices correct?
- [ ] Delivery info present (if assigned)?
- [ ] Action buttons visible?
- [ ] Tracking timeline shows updates?

---

## 8️⃣ Delivery Management

### 8.1 View Delivery Partners
**URL:** `http://localhost:8000/agent/delivery-partners/`

**Flow:**
1. Click "Delivery Partners" in agent sidebar
2. View list of assigned delivery partners:
   - Partner Name
   - Contact Phone
   - Email
   - Company (if applicable)
   - Status (Active/Inactive)
   - Vehicles Count
   - Action buttons (Edit, Remove)

**Expected Outcome:**
- ✅ All delivery partners show
- ✅ Contact info visible
- ✅ Status badges correct
- ✅ Can view partner details
- ✅ Can edit or remove

**Issues to Check:**
- [ ] All partners showing?
- [ ] Contact info correct?
- [ ] Vehicle count accurate?
- [ ] Action buttons working?

---

### 8.2 Add Delivery Partner
**URL:** `http://localhost:8000/agent/delivery-partners/add/`

**Flow:**
1. Click "Add Delivery Partner" button
2. Form with fields:
   - Contact Name (required)
   - Phone Number (required)
   - Email (required)
   - Company Name (optional)
   - Status (Active/Inactive)
3. Click "Save"

**Expected Outcome:**
- ✅ Delivery partner created
- ✅ Appears in partners list
- ✅ Can be assigned to orders
- ✅ Contact info saved correctly
- ✅ Confirmation shown

**Issues to Check:**
- [ ] Form validation working?
- [ ] Partner saves correctly?
- [ ] Appears in list immediately?
- [ ] Can assign to orders right away?

---

### 8.3 Add Vehicle to Delivery Partner
**URL:** Admin interface or agent delivery partner detail

**Flow:**
1. From delivery partners list, click partner name
2. View partner details with vehicles section
3. Click "Add Vehicle" button
4. Vehicle Form:
   - Vehicle Type (bike, auto, car, truck, van)
   - Vehicle Number (license plate, required)
   - Model (optional)
   - Registration Number (required)
   - Capacity (weight/volume, required)
   - Insured (yes/no)
   - Insurance Expiry Date (if insured)
   - Status (active, maintenance, inactive)
5. Click "Save"

**Expected Outcome:**
- ✅ Vehicle created for partner
- ✅ Vehicle appears in partner's vehicle list
- ✅ Can select vehicle when assigning delivery
- ✅ Vehicle details saved correctly

**Issues to Check:**
- [ ] Vehicle form loads?
- [ ] Vehicle saves correctly?
- [ ] Vehicle appears in list?
- [ ] Can select when assigning orders?
- [ ] Vehicle details show in order assignment?

---

### 8.4 Assign Delivery Partner to Order
**URL:** `http://localhost:8000/agent/orders/{order_id}/assign-delivery/`

**Flow:**
1. From order details, click "Assign Delivery Partner"
2. Assignment Form:
   - **Select Delivery Partner** (dropdown)
     - Shows all active delivery partners
   - **Select Vehicle** (dropdown, shows after partner selected)
     - Shows all active vehicles for selected partner
     - Displays: Vehicle number, type, capacity
   - **Estimated Delivery Date** (date picker)
3. Click "Confirm Assignment"

**Expected Outcome:**
- ✅ Delivery partner dropdown loads all partners
- ✅ Vehicle dropdown populates based on selected partner
- ✅ Vehicle details display (type, capacity, etc.)
- ✅ Can select estimated delivery date
- ✅ Assignment saves successfully
- ✅ Order status updates (if configured)
- ✅ Delivery partner can see assigned order

**Issues to Check:**
- [ ] Partners dropdown working?
- [ ] Vehicles populate correctly?
- [ ] Vehicle details showing?
- [ ] Date picker working?
- [ ] Assignment saves correctly?
- [ ] Order reflects assignment?
- [ ] Delivery partner notified?

---

### 8.5 View Delivery Tracking
**URL:** `http://localhost:8000/agent/orders/{order_id}/tracking/`

**Flow:**
1. From order detail, click "View Tracking"
2. Delivery Tracking Page shows:
   - **Delivery Partner Info**
     - Name, Phone, Email
     - Company
   
   - **Vehicle Info**
     - Vehicle Number
     - Vehicle Type
     - Vehicle Capacity
     - Insurance Status
   
   - **Delivery Timeline**
     - Current Status (Pending, In Transit, Out for Delivery, Delivered)
     - Status progression with dates/times:
       - ✓ Order Confirmed (date/time)
       - ✓ Order Dispatched (date/time)
       - → In Transit (date/time)
       - → Out for Delivery (estimated date/time)
       - → Delivered (when complete)
   
   - **Last Location** (if available)
   - **Update Delivery Status** button

**Expected Outcome:**
- ✅ Delivery partner info visible
- ✅ Vehicle details displayed
- ✅ Timeline shows all updates
- ✅ Status badges correct
- ✅ Dates/times accurate
- ✅ Can see last update
- ✅ Can update status

**Issues to Check:**
- [ ] Partner info showing?
- [ ] Vehicle info complete?
- [ ] Timeline showing all updates?
- [ ] Status badges correct?
- [ ] Can update status?

---

### 8.6 Update Delivery Status
**URL:** `http://localhost:8000/agent/orders/{order_id}/update-delivery/`

**Flow:**
1. From tracking page or order detail, click "Update Delivery Status"
2. Update Form:
   - Current Status (display)
   - New Status (dropdown):
     - In Transit
     - Out for Delivery
     - Delivered
     - Failed Delivery (with reason)
   - Notes (optional)
   - Location (optional, for real-time tracking)
   - Date/Time (auto-filled with now)
3. Click "Update"

**Expected Outcome:**
- ✅ Status updates in real-time
- ✅ Timeline updates immediately
- ✅ Customer can see status change
- ✅ Previous status shown in history
- ✅ Confirmation shown
- ✅ Order history updated

**Issues to Check:**
- [ ] Status dropdown shows correct options?
- [ ] Status saves correctly?
- [ ] Timeline updates immediately?
- [ ] Customer sees update?
- [ ] Notes saved with update?

---

## 9️⃣ Reports & Analytics

### 9.1 View Reports Dashboard
**URL:** `http://localhost:8000/agent/reports/`

**Flow:**
1. Click "Reports" in agent sidebar
2. Reports page shows:
   - **Revenue Overview**
     - Total Revenue (all time)
     - Revenue this month
     - Revenue this week
     - Revenue today
   
   - **Sales Summary**
     - Total Orders (all time)
     - Orders this month
     - Completed Orders
     - Pending Orders
     - Cancelled Orders
   
   - **Revenue Chart**
     - Graph showing revenue over time
     - Selectable period (Week, Month, Year)
   
   - **Order Status Distribution**
     - Pie chart showing order statuses
   
   - **Top Products**
     - Best-selling products by units sold
     - Best-selling products by revenue
   
   - **Customer Insights**
     - New customers this month
     - Repeat customers
     - Average order value

**Expected Outcome:**
- ✅ All metrics calculate correctly
- ✅ Charts load and display data
- ✅ Data is accurate and up-to-date
- ✅ Can select different periods
- ✅ Reports exportable (if feature exists)

**Issues to Check:**
- [ ] All metrics calculating?
- [ ] Charts rendering?
- [ ] Period selection working?
- [ ] Data accurate?
- [ ] Performance acceptable?

---

### 9.2 View Market Insights
**URL:** `http://localhost:8000/agent/insights/`

**Flow:**
1. Click "Market Insights" in agent sidebar
2. Insights page shows:
   - **Trending Products**
     - Products trending in market
     - Category
     - Trend direction (up/down)
     - Change percentage
   
   - **Market Suggestions**
     - AI/System suggestions for agent
     - E.g., "High demand for [product], consider stocking more"
     - "Competitor selling [product] at lower price"
   
   - **Demand Analysis**
     - Product categories in demand
     - Customer interests
   
   - **Competition Analysis** (if available)
     - Pricing comparison
     - Stock levels comparison

**Expected Outcome:**
- ✅ Trending products display
- ✅ Suggestions are relevant
- ✅ Data shows market trends
- ✅ Can help guide inventory
- ✅ Insights update periodically

**Issues to Check:**
- [ ] Trending products showing?
- [ ] Suggestions relevant?
- [ ] Data accurate?
- [ ] Insights update regularly?

---

## 🔟 Returns Management

### 10.1 View Return Requests
**URL:** `http://localhost:8000/agent/` (look for Returns tab/menu)

**Flow:**
1. Navigate to Returns section
2. View return requests:
   - Order ID
   - Product Name
   - Return Reason
   - Return Status (Requested, Approved, Rejected, Completed)
   - Request Date
   - Action buttons

**Expected Outcome:**
- ✅ All return requests show
- ✅ Can view return details
- ✅ Can approve/reject returns
- ✅ Can track return status

**Issues to Check:**
- [ ] Return requests showing?
- [ ] Statuses accurate?
- [ ] Can take action on returns?

---

### 10.2 Handle Return Request
**URL:** `http://localhost:8000/agent/orders/{order_id}/item/{item_id}/return/`

**Flow:**
1. From return requests, click request
2. Return Details Form:
   - Order Info (read-only)
   - Product Info (read-only)
   - Return Reason (display)
   - Customer Notes (display)
   - Action: Approve Return / Reject Return
   - Response Notes (text field)
3. If Approved:
   - Generate Return Shipping Label
   - Set Return Deadline
   - Notify Customer
4. Click "Process"

**Expected Outcome:**
- ✅ Return details display
- ✅ Can approve/reject return
- ✅ Notes recorded
- ✅ Customer notified
- ✅ Status updates to Approved/Rejected
- ✅ Return processed in system

**Issues to Check:**
- [ ] Return details loading?
- [ ] Can approve/reject?
- [ ] Customer notified?
- [ ] Status updates?

---

## Summary Checklist

### Critical Agent Functions
- [ ] Agent login and role access
- [ ] Dashboard with metrics
- [ ] Profile view and edit
- [ ] Product management (add, edit, delete, view)
- [ ] Stock management (adjust, alerts)
- [ ] Sales tracking
- [ ] Order viewing (all and incoming)
- [ ] Order detail viewing with delivery info
- [ ] Delivery partner management
- [ ] Vehicle management
- [ ] Delivery assignment with vehicle selection
- [ ] Delivery tracking and status updates
- [ ] Reports and analytics
- [ ] Market insights
- [ ] Return request handling

### Key Validations
- [ ] Only agent's products in list
- [ ] Only agent's orders visible
- [ ] Delivery partner data correct
- [ ] Vehicle info accurate
- [ ] Stock calculations correct
- [ ] Revenue calculations accurate
- [ ] Status transitions valid
- [ ] Customer notifications sent
- [ ] Reports data correct
- [ ] Delivery timeline updates properly

---

## Common Issues Found
*(To be filled after testing)*

| Issue # | Page | Issue Description | Status |
|---------|------|-------------------|--------|
| 1 | Order Detail | Delivery info section shows if no delivery assigned | ❌ FOUND |
|  |  |  |  |
|  |  |  |  |

---

## Testing Notes

### Agent Test Account
- Email: `[agent_email]`
- Password: `[agent_password]`
- Company: `[company_name]`
- Status: Active

### Test Orders
- Create test orders as customer
- Assign delivery partner as agent
- Update delivery status through progression

### Performance Notes
- [ ] Dashboard loads quickly
- [ ] Product list responsive with large datasets
- [ ] Charts render without lag
- [ ] Search/filter responsive

---

**Last Updated:** December 21, 2025
**Tested By:** [Your Name]
**Environment:** Development (localhost:8000)
