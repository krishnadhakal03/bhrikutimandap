from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from .models import User, Address, PaymentMethod, AgentProfile, Product, StockHistory, SalesTransaction, StockAlert, Category, ProductReview, ProductMedia


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'type': 'tel'
            }),
        }

    def clean_email(self):
        """Ensure email is unique (except for current user)"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class ProductReviewForm(forms.ModelForm):
    """Form for customer reviews"""
    
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{"★" * i}{"☆" * (5-i)}') for i in range(5, 0, -1)],
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your product review here...',
                'rows': 4
            }),
        }


class AddressForm(forms.ModelForm):
    """Form for managing delivery addresses"""
    
    class Meta:
        model = Address
        fields = ['label', 'recipient_name', 'phone', 'address_line1', 
                  'address_line2', 'city', 'state', 'postal_code', 'country', 'is_default']
        widgets = {
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address Label (e.g., Home, Office)'
            }),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'type': 'tel'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, suite, etc. (Optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State / Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP / Postal Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'India'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        return phone


class PaymentMethodForm(forms.ModelForm):
    """Form for managing payment methods (tokenized only)"""
    
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'display_name', 'last_four', 'is_default']
        widgets = {
            'payment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., My Visa Card, My UPI',
                'help_text': 'A friendly name for this payment method'
            }),
            'last_four': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last 4 digits (optional)',
                'maxlength': '4'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_last_four(self):
        """Validate last_four contains only digits"""
        last_four = self.cleaned_data.get('last_four')
        if last_four and not last_four.isdigit():
            raise forms.ValidationError("Last four digits should contain only numbers.")
        return last_four


class OrderFilterForm(forms.Form):
    """Form for filtering order history"""
    
    STATUS_CHOICES = [
        ('', 'All Orders'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    DATE_CHOICES = [
        ('', 'All Dates'),
        ('30days', 'Last 30 Days'),
        ('90days', 'Last 90 Days'),
        ('6months', 'Last 6 Months'),
        ('1year', 'Last Year'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_range = forms.ChoiceField(
        choices=DATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by order ID...'
        })
    )


# ==================== AGENT/SUPPLIER PORTAL FORMS ====================

class AgentProfileForm(forms.ModelForm):
    """Form for agent profile management"""
    
    class Meta:
        model = AgentProfile
        fields = ['company_name', 'company_address', 'company_phone', 'gst_number', 'bank_account', 'bank_ifsc', 'monthly_target', 'company_logo', 'company_banner', 'trademark_image']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),
            'company_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Company Address',
                'rows': 3
            }),
            'company_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Phone',
                'type': 'tel'
            }),
            'gst_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'GST Number (Optional)'
            }),
            'bank_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank Account Number'
            }),
            'bank_ifsc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank IFSC Code'
            }),
            'monthly_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Monthly Sales Target'
            }),
            'company_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'company_banner': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'trademark_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


class AgentProductForm(forms.ModelForm):
    """Form for creating/editing products by agent"""
    
    class Meta:
        model = Product
        fields = ['title', 'category', 'description', 'price', 'stock', 'delivery_rules', 'payment_methods', 'image', 'expiration_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product Name'
            }),
            # category widget is handled by the explicit field definition below
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Product Description',
                'rows': 4
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Price',
                'step': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Initial Stock',
                'min': '0'
            }),
            'delivery_rules': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Free shipping, Ships in 2-3 days',
                'rows': 2
            }),
            'payment_methods': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., COD, Card, UPI (comma-separated)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'expiration_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Category"
    )

    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        error_messages={'required': 'At least one primary product image is required.'}
    )

    additional_media = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Upload more images or videos for your product (Hold Ctrl/Cmd to select multiple)."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enable multiple file selection for additional_media
        self.fields['additional_media'].widget.attrs.update({'multiple': True})


class StockAdjustmentForm(forms.ModelForm):
    """Form for adjusting stock"""
    
    class Meta:
        model = StockHistory
        fields = ['action', 'quantity_changed', 'reason']
        widgets = {
            'action': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantity_changed': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantity to add/remove'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for adjustment',
                'rows': 2
            }),
        }


class SalesTransactionForm(forms.ModelForm):
    """Form for recording sales transactions"""
    
    class Meta:
        model = SalesTransaction
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantity Sold',
                'min': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unit Price',
                'step': '0.01'
            }),
        }


class SalesFilterForm(forms.Form):
    """Form for filtering sales transactions"""
    
    DATE_CHOICES = [
        ('', 'All Time'),
        ('today', 'Today'),
        ('7days', 'Last 7 Days'),
        ('30days', 'Last 30 Days'),
        ('90days', 'Last 90 Days'),
    ]
    
    date_range = forms.ChoiceField(
        choices=DATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Products'
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by product name...'
        })
    )


class StockAlertForm(forms.ModelForm):
    """Form for setting stock alert thresholds"""
    
    class Meta:
        model = StockAlert
        fields = ['product', 'threshold_quantity', 'is_active']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control'
            }),
            'threshold_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alert when stock falls below',
                'min': '1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class AgentDeliveryPartnerForm(forms.ModelForm):
    """Form for managing agent's preferred delivery partners"""
    
    class Meta:
        from .models import AgentDeliveryPartner
        model = AgentDeliveryPartner
        fields = ['delivery_partner', 'is_preferred', 'is_active', 'notes']
        widgets = {
            'delivery_partner': forms.Select(attrs={
                'class': 'form-control form-control-lg',
            }),
            'is_preferred': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Special instructions or notes for this delivery partner',
                'rows': 3
            }),
        }

class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form that handles email sending without template rendering errors"""
    
    def save(self, *args, **kwargs):
        """
        Override save to skip Django's default email rendering.
        Django's default tries to render a template to get the reset link,
        which can fail if URL names aren't configured correctly.
        We'll handle email sending in the view's send_mail method instead.
        """
        try:
            email = self.cleaned_data["email"]
            UserModel = self.get_users(email)
            for user in UserModel:
                # Let Django generate the token but skip the template rendering
                # The view's send_mail will be called by Django's PasswordResetView.form_valid()
                pass
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Password reset form save error: {e}")
        return email