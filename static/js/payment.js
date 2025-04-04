/**
 * Spa en Ruedas - Payment Form JavaScript
 * Handles the payment form functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the payment form
    const paymentForm = document.getElementById('paymentForm');
    
    if (paymentForm) {
        // Credit card field formatter
        const cardNumberInput = document.getElementById('card_number');
        
        if (cardNumberInput) {
            cardNumberInput.addEventListener('input', function(e) {
                // Remove any non-digit characters
                let value = this.value.replace(/\D/g, '');
                
                // Add spaces after every 4 digits
                if (value.length > 0) {
                    value = value.match(new RegExp('.{1,4}', 'g')).join(' ');
                }
                
                // Update the input value
                this.value = value;
                
                // Limit to 19 characters (16 digits + 3 spaces)
                if (this.value.length > 19) {
                    this.value = this.value.substr(0, 19);
                }
            });
        }
        
        // Expiry date formatter (MM/YY)
        const expiryDateInput = document.getElementById('expiry_date');
        
        if (expiryDateInput) {
            expiryDateInput.addEventListener('input', function(e) {
                // Remove any non-digit characters
                let value = this.value.replace(/\D/g, '');
                
                // Format as MM/YY
                if (value.length > 0) {
                    if (value.length <= 2) {
                        this.value = value;
                    } else {
                        this.value = value.substr(0, 2) + '/' + value.substr(2, 2);
                    }
                }
                
                // Limit to 5 characters (MM/YY)
                if (this.value.length > 5) {
                    this.value = this.value.substr(0, 5);
                }
                
                // Validate month (01-12)
                if (value.length >= 2) {
                    const month = parseInt(value.substr(0, 2), 10);
                    if (month < 1) {
                        this.value = '01' + this.value.substr(2);
                    } else if (month > 12) {
                        this.value = '12' + this.value.substr(2);
                    }
                }
            });
        }
        
        // CVV formatter (3-4 digits)
        const cvvInput = document.getElementById('cvv');
        
        if (cvvInput) {
            cvvInput.addEventListener('input', function(e) {
                // Remove any non-digit characters
                this.value = this.value.replace(/\D/g, '');
                
                // Limit to 4 digits (most cards have 3, but some like Amex have 4)
                if (this.value.length > 4) {
                    this.value = this.value.substr(0, 4);
                }
            });
        }
        
        // Form validation
        paymentForm.addEventListener('submit', function(event) {
            if (!validatePaymentForm()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            this.classList.add('was-validated');
        });
        
        // Payment method toggle
        const paymentMethodRadios = document.querySelectorAll('input[name="paymentMethod"]');
        
        paymentMethodRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const creditCardForm = document.getElementById('creditCardForm');
                
                if (this.value === 'credit' || this.value === 'debit') {
                    creditCardForm.style.display = 'block';
                } else {
                    creditCardForm.style.display = 'none';
                }
            });
        });
    }
    
    // Validate the payment form
    function validatePaymentForm() {
        let isValid = true;
        
        // Card number validation (should be 16 digits)
        const cardNumberInput = document.getElementById('card_number');
        if (cardNumberInput) {
            const cardNumber = cardNumberInput.value.replace(/\s/g, '');
            if (cardNumber.length < 13 || cardNumber.length > 19) {
                isValid = false;
                showError(cardNumberInput, 'El número de tarjeta debe tener entre 13 y 19 dígitos');
            } else {
                clearError(cardNumberInput);
            }
        }
        
        // Expiry date validation (should be in format MM/YY and not expired)
        const expiryDateInput = document.getElementById('expiry_date');
        if (expiryDateInput) {
            const expiryDate = expiryDateInput.value;
            const expiryPattern = /^(0[1-9]|1[0-2])\/([0-9]{2})$/;
            
            if (!expiryPattern.test(expiryDate)) {
                isValid = false;
                showError(expiryDateInput, 'El formato debe ser MM/YY');
            } else {
                // Check if the card is expired
                const [month, year] = expiryDate.split('/');
                const expiryMonth = parseInt(month, 10);
                const expiryYear = parseInt('20' + year, 10);
                const now = new Date();
                const currentMonth = now.getMonth() + 1; // getMonth() is zero-based
                const currentYear = now.getFullYear();
                
                if (expiryYear < currentYear || (expiryYear === currentYear && expiryMonth < currentMonth)) {
                    isValid = false;
                    showError(expiryDateInput, 'La tarjeta ha expirado');
                } else {
                    clearError(expiryDateInput);
                }
            }
        }
        
        // CVV validation (should be 3-4 digits)
        const cvvInput = document.getElementById('cvv');
        if (cvvInput) {
            const cvv = cvvInput.value;
            if (cvv.length < 3 || cvv.length > 4) {
                isValid = false;
                showError(cvvInput, 'El CVV debe tener 3 o 4 dígitos');
            } else {
                clearError(cvvInput);
            }
        }
        
        // Card holder validation (should not be empty)
        const cardHolderInput = document.getElementById('card_holder');
        if (cardHolderInput) {
            if (cardHolderInput.value.trim() === '') {
                isValid = false;
                showError(cardHolderInput, 'Por favor, ingrese el nombre del titular de la tarjeta');
            } else {
                clearError(cardHolderInput);
            }
        }
        
        return isValid;
    }
    
    // Helper function to show error message
    function showError(input, message) {
        input.classList.add('is-invalid');
        
        // Create error message element if it doesn't exist
        let errorElement = input.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            input.parentNode.insertBefore(errorElement, input.nextSibling);
        }
        
        errorElement.textContent = message;
    }
    
    // Helper function to clear error message
    function clearError(input) {
        input.classList.remove('is-invalid');
        
        // Remove error message element if it exists
        const errorElement = input.nextElementSibling;
        if (errorElement && errorElement.classList.contains('invalid-feedback')) {
            errorElement.textContent = '';
        }
    }
});
