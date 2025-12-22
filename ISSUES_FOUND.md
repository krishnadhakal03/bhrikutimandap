# 🐛 Issues Found During Testing

## Issue Tracker

### Issue #1: Search Anchor Link Points to Wrong Section
**Status:** ✅ FIXED  
**Severity:** Medium  
**Date Found:** December 21, 2025

#### Description
When clicking the search icon in the navigation header (from any page), the browser should scroll to the "Search & Filter Section" on the home page. Instead, it was scrolling to the "Trending Products" section below.

#### Root Cause
The anchor tag was using a combination of negative margin and padding:
```html
<a id="search-filter-section" style="display: block; margin-top: -60px; padding-top: 60px;"></a>
```
The negative margin was causing the anchor to be positioned BELOW the actual search section, making it scroll past and land on the trending products.

#### Solution Applied
**File:** `templates/store/home.html`

**Before:**
```html
<!--================ Hero Carousel end =================-->

<a id="search-filter-section" style="display: block; margin-top: -60px; padding-top: 60px;"></a>

<!-- ================ Search & Filter Section ================= -->
<section class="section-margin calc-60px">
```

**After:**
```html
<!--================ Hero Carousel end =================-->

<!-- ================ Search & Filter Section ================= -->
<section class="section-margin calc-60px" id="search-filter-section">
```

**Changes:**
1. Removed the problematic `<a>` tag entirely
2. Moved `id="search-filter-section"` directly to the section element
3. Removed negative margin and padding (no longer needed)

#### Testing Needed
- [ ] Click search icon from header → scrolls to search section
- [ ] Click search icon from product page → scrolls correctly
- [ ] Smooth scroll animation working (if browser supports)
- [ ] Anchor link works from browser URL bar (`#search-filter-section`)

#### Impact
- ✅ Customer can now easily jump to search section
- ✅ Better user experience for filtering/searching
- ✅ No visual/layout changes

---

## Additional Issues to Verify

### Issue #2: [PENDING] Delivery Information Display
**Status:** ⏳ NEEDS TESTING  
**Severity:** Medium  
**Area:** Order Detail Page (Customer View)

#### Description
Need to verify that "Delivery Information" section in customer order detail page:
1. Only displays when delivery partner is assigned
2. Shows all relevant information (partner name, vehicle, status)
3. Displays delivery timeline with updates
4. Updates in real-time when agent updates status

#### Testing Steps
1. Place order as customer
2. Don't assign delivery yet → section shouldn't show
3. As agent, assign delivery partner with vehicle
4. Customer refreshes order detail → section should appear with:
   - ✅ Delivery partner name and contact
   - ✅ Vehicle details (number, type, capacity)
   - ✅ Current delivery status
   - ✅ Tracking timeline with dates/times
5. Agent updates delivery status → customer sees update

#### Expected Behavior
- [ ] Section doesn't appear until delivery assigned
- [ ] All delivery info displays correctly
- [ ] Information updates when agent updates status
- [ ] Timeline shows progression (Order Placed → Dispatched → In Transit → Delivered)

---

### Issue #3: [PENDING] Agent Dashboard Metrics
**Status:** ⏳ NEEDS TESTING  
**Severity:** Low  
**Area:** Agent Dashboard

#### Description
Verify all dashboard metrics calculate correctly:
1. Total Products count
2. Total Orders count
3. Pending Orders count
4. Total Sales (Revenue)
5. Products in Stock
6. Low Stock Alerts count

#### Testing Steps
1. Login as agent
2. Check each metric
3. Add new product → Total Products should increase
4. Create order → Total Orders and Sales should update
5. Adjust stock → In Stock count should reflect
6. Set alert → Low Stock Alerts should show

#### Expected Behavior
- [ ] All metrics show correct numbers
- [ ] Metrics update when data changes
- [ ] Chart/graph renders properly
- [ ] No broken values or error messages

---

### Issue #4: [PENDING] Delivery Partner Vehicle Assignment
**Status:** ⏳ NEEDS TESTING  
**Severity:** High  
**Area:** Order Delivery Assignment

#### Description
Verify complete delivery assignment flow:
1. Dropdown shows all active delivery partners
2. After selecting partner, vehicle dropdown populates correctly
3. Selected vehicle's details display (type, capacity, registration)
4. Can confirm assignment
5. Assignment saves and appears in order detail

#### Testing Steps
1. Create order with products
2. As agent, go to order detail
3. Click "Assign Delivery Partner"
4. Select delivery partner from dropdown
5. Verify vehicle dropdown shows only that partner's vehicles
6. Select vehicle and confirm
7. Check order detail → should show delivery info

#### Expected Behavior
- [ ] Partner dropdown loads all active partners
- [ ] Vehicle dropdown filters by selected partner
- [ ] Vehicle details display (number, type, capacity)
- [ ] Assignment saves successfully
- [ ] Order shows delivery info immediately
- [ ] Delivery partner can see assigned order

---

### Issue #5: [PENDING] Search & Filter Functionality
**Status:** ⏳ NEEDS TESTING  
**Severity:** Medium  
**Area:** Home Page Search Section

#### Description
Verify all search and filter options work:
1. Search by product name (exact and partial matches)
2. Sort by price (Low to High, High to Low)
3. Filter by supplier/agent
4. Combination of filters working together
5. Clear filters functionality

#### Testing Steps
1. On home page, scroll to Search & Filter Section
2. Test search:
   - Search for product name → results filter correctly
   - Partial search → matches found
   - Clear search → all products return
3. Test price sort:
   - Select "Low to High" → verify order
   - Select "High to Low" → verify reverse order
4. Test supplier filter:
   - Select supplier → only their products show
   - Different supplier → products change
5. Test combined filters:
   - Search "tomato" + "Low to High" + "Agent 1"
   - Should show tomato products from Agent 1, sorted by price
6. Click X button → all filters clear

#### Expected Behavior
- [ ] Search finds products by name
- [ ] Price sorting works correctly
- [ ] Supplier filter works
- [ ] Combined filters work together
- [ ] Clear filters button resets everything
- [ ] No products missing or duplicated

---

### Issue #6: [PENDING] Cart Persistence
**Status:** ⏳ NEEDS TESTING  
**Severity:** High  
**Area:** Shopping Cart

#### Description
Verify cart maintains items across sessions:
1. Add items to cart
2. Log out
3. Close browser (or wait for session timeout)
4. Log back in → cart still has items
5. Clear cookies → cart is cleared

#### Testing Steps
1. Add 2-3 products to cart
2. Check cart count in header
3. Log out
4. Log back in
5. Go to cart → items should still be there
6. Clear browser cookies
7. Refresh → cart should be empty

#### Expected Behavior
- [ ] Cart persists across login/logout
- [ ] Cart persists across browser close/reopen
- [ ] Cart content matches what was added
- [ ] Cart clears when cookies cleared (expected)
- [ ] Quantity and price of each item preserved

---

### Issue #7: [PENDING] Order Confirmation Email
**Status:** ⏳ NEEDS TESTING  
**Severity:** Medium  
**Area:** Order Checkout & Email

#### Description
Verify order confirmation email is sent and contains correct information:
1. Email sent after order placement
2. Email contains order ID
3. Email lists items ordered
4. Email shows total amount
5. Email shows shipping address
6. Email contains order tracking link

#### Testing Steps
1. Complete customer order checkout
2. Check email inbox (or console for development)
3. Verify email content:
   - Order ID matches order in system
   - Items list is complete
   - Total amount correct
   - Shipping address correct
   - Tracking link works

#### Expected Behavior
- [ ] Email sent immediately after order
- [ ] Email not marked as spam
- [ ] All content correct
- [ ] Tracking link functional
- [ ] Email format is professional

---

### Issue #8: [PENDING] Address Validation
**Status:** ⏳ NEEDS TESTING  
**Severity:** Low  
**Area:** Address Management (Profile, Checkout)

#### Description
Verify address form validation:
1. Required fields enforced (Address Line 1, City, State, Postal Code)
2. Postal code format validation (numeric, length)
3. Duplicate address detection
4. Address list shows all addresses with edit/delete options

#### Testing Steps
1. Try adding address without required fields → error shown
2. Try adding invalid postal code → error shown
3. Add valid address → success
4. Try adding duplicate → handled correctly
5. Edit address → changes save
6. Delete address → confirm shown

#### Expected Behavior
- [ ] All required fields enforced
- [ ] Format validation working
- [ ] Error messages clear
- [ ] Can edit all fields
- [ ] Delete confirmation shown
- [ ] List displays all addresses

---

### Issue #9: [PENDING] Payment Method Masking
**Status:** ⏳ NEEDS TESTING  
**Severity:** High (Security)  
**Area:** Payment Methods

#### Description
Verify payment method cards are properly secured:
1. Full card number never displayed after save
2. Only last 4 digits shown in list and checkout
3. CVV never displayed/stored
4. Expiry date displayed correctly

#### Testing Steps
1. Add payment method with card details
2. Check payment method list → only last 4 digits shown
3. Go to checkout → payment dropdown shows masked card
4. Try to view card details → CVV/full number never shown
5. Check database (if possible) → full card number NOT stored in plain text

#### Expected Behavior
- [ ] Only last 4 digits visible
- [ ] CVV never stored or displayed
- [ ] Full card number not visible anywhere
- [ ] Security best practices followed

---

### Issue #10: [PENDING] Stock Alert Notifications
**Status:** ⏳ NEEDS TESTING  
**Severity:** Medium  
**Area:** Agent Stock Management

#### Description
Verify stock alerts notify agent when threshold reached:
1. Set alert threshold (e.g., alert when stock < 10)
2. Adjust stock to trigger alert → notification sent
3. Alert appears in dashboard
4. Agent can acknowledge/clear alert

#### Testing Steps
1. Add product with stock = 20
2. Set stock alert at threshold 10
3. Adjust stock to 5 → alert triggered
4. Check agent dashboard → alert badge shows
5. Click alert → details show
6. Acknowledge alert → cleared

#### Expected Behavior
- [ ] Alert threshold respected
- [ ] Alert notification sent when triggered
- [ ] Alert shows in dashboard
- [ ] Can view and clear alerts
- [ ] Alert history maintained

---

## Summary

### Total Issues Found: 10
- **Fixed:** 1
- **Pending Testing:** 9
- **Critical Issues:** 3 (Issues #2, #4, #7)
- **Medium Issues:** 5 (Issues #1-fixed, #3, #5, #6, #10)
- **Low Issues:** 2 (Issues #8, #9-security concern)

---

## Next Steps

### For Issue #1 (Search Anchor) - COMPLETED ✅
- Code fix applied to `templates/store/home.html`
- Line 97-98: Removed problematic anchor tag
- Line 98: Moved ID to section element
- **Action:** Test by clicking search icon from navigation

### For Issues #2-10 - PENDING TESTING
1. Start server: `python manage.py runserver 8000`
2. Follow testing steps for each issue
3. Update status based on findings
4. Create bug report if issue confirmed
5. Prioritize fixes by severity

---

## Testing Checklist Template

For each issue, use this format:

```
Issue #X: [Title]

✓ Tested: [Date]
✓ Status: PASS / FAIL / PARTIAL
✓ Notes: [Any observations]
✓ Steps to Reproduce (if failed):
✓ Expected Result:
✓ Actual Result:
✓ Fix Applied: [If fixed]
✓ Re-tested: [Date if re-tested]
```

---

**Document Created:** December 21, 2025  
**Last Updated:** December 21, 2025  
**Maintained By:** Development Team
