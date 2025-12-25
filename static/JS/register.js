document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    const password1 = document.getElementById('password1');
    const password2 = document.getElementById('password2');
    const strengthBar = document.getElementById('strengthBar');
    const phoneInput = document.getElementById('phone');
    const submitBtn = document.getElementById('submitBtn');

    // ========== Password Strength Indicator ==========
    password1.addEventListener('input', function() {
        const value = this.value;
            const length = value.length;
            
            // Simple strength indicator
            if (strengthBar) {
                if (length === 0) {
                    strengthBar.style.width = '0%';
                    strengthBar.style.backgroundColor = '#e5e7eb';
                } else if (length < 5) {
                    strengthBar.style.width = '33%';
                    strengthBar.style.backgroundColor = '#ef4444';
                } else if (length > 8){
                    strengthBar.style.width = '100%';
                    strengthBar.style.backgroundColor = '#10b981';
               }
            }
    });


    // ========== Phone Validation (Algerian format) ==========
    function validatePhone(phone) {
        // Remove spaces and dashes
        const cleanPhone = phone.replace(/[\s-]/g, '');
        
        // Algerian phone patterns:
        // +213 5/6/7 XX XX XX XX or 05/06/07 XX XX XX XX
        const patterns = [
            /^\+213[567]\d{8}$/,  // +213 5/6/7XXXXXXXX
            /^0[567]\d{8}$/        // 05/06/07XXXXXXXX
        ];
        
        return patterns.some(pattern => pattern.test(cleanPhone));
    }

    phoneInput.addEventListener('blur', function() {
        const phone = this.value.trim();
        
        if (phone && !validatePhone(phone)) {
            this.classList.add('invalid');
            this.classList.remove('valid');
            showFieldError(this, 'Please enter a valid Algerian phone number (e.g., +213 555 123 456)');
        } else if (phone) {
            this.classList.add('valid');
            this.classList.remove('invalid');
            removeFieldError(this);
        }
    });

    // ========== Helper Functions ==========
    function showFieldError(field, message) {
        removeFieldError(field); // Remove existing error first
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        
        field.parentElement.parentElement.appendChild(errorDiv);
    }

    function removeFieldError(field) {
        const existingError = field.parentElement.parentElement.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }

    // ========== Remove Error Styling on Input ==========
    [phoneInput].forEach(input => {
        input.addEventListener('input', function() {
            if (this.classList.contains('invalid')) {
                this.classList.remove('invalid');
                removeFieldError(this);
            }
        });
    });

    // ========== Password Match Check (Real-time) ==========
    password2.addEventListener('input', function() {
        const pass1 = password1.value;
        const pass2 = this.value;
        
        if (pass2 && pass1 !== pass2) {
            this.classList.add('invalid');
            this.classList.remove('valid');
            showFieldError(this, 'Passwords do not match');
        } else if (pass2 && pass1 === pass2) {
            this.classList.add('valid');
            this.classList.remove('invalid');
            removeFieldError(this);
        }
    });

    // ========== Form Validation on Submit ==========
    form.addEventListener('submit', function(e) {
        let isValid = true;
        const errors = [];
        
        // Password match check
        const pass1 = password1.value;
        const pass2 = password2.value;
        
        if (pass1 !== pass2) {
            isValid = false;
            errors.push('❌ Passwords do not match');
            password2.classList.add('invalid');
        }
        
        
        // Phone validation
        const phone = phoneInput.value.trim();
        if (!validatePhone(phone)) {
            isValid = false;
            errors.push('❌ Invalid phone number format');
            phoneInput.classList.add('invalid');
        }
        
        // Password strength check
        if (pass1.length < 8) {
            isValid = false;
            errors.push('❌ Password must be at least 8 characters long');
            password1.classList.add('invalid');
        }
        
        // Prevent submission if validation fails
        if (!isValid) {
            e.preventDefault();
            
            // Show errors in a more user-friendly way
            const errorMessage = 'Please fix the following errors:\n\n' + errors.join('\n');
            alert(errorMessage);
            
            // Scroll to first error
            const firstError = form.querySelector('.invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        } else {
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.classList.add('loading');
            submitBtn.textContent = 'Creating Account...';
        }
    });

    // ========== Phone Number Formatting (Optional) ==========
    phoneInput.addEventListener('input', function(e) {
        let value = this.value.replace(/\D/g, ''); // Remove non-digits
        
        // Format as: 05 55 12 34 56 or +213 5 55 12 34 56
        if (value.startsWith('213')) {
            // International format
            if (value.length > 3) {
                value = '+213 ' + value.substring(3, 4) + ' ' + 
                        value.substring(4, 6) + ' ' + 
                        value.substring(6, 8) + ' ' + 
                        value.substring(8, 10) + ' ' + 
                        value.substring(10, 12);
            }
        } else if (value.startsWith('0')) {
            // Local format
            if (value.length > 2) {
                value = value.substring(0, 2) + ' ' + 
                        value.substring(2, 4) + ' ' + 
                        value.substring(4, 6) + ' ' + 
                        value.substring(6, 8) + ' ' + 
                        value.substring(8, 10);
            }
        }
        
        this.value = value.trim();
    });

    // ========== Real-time Form Validation Status ==========
    function updateSubmitButton() {
        const allInputs = form.querySelectorAll('input[required]');
        const allValid = Array.from(allInputs).every(input => {
            return input.value.trim() !== '' && !input.classList.contains('invalid');
        });
        
        submitBtn.disabled = !allValid;
    }

    // Monitor all required inputs
    form.querySelectorAll('input[required]').forEach(input => {
        input.addEventListener('input', updateSubmitButton);
        input.addEventListener('blur', updateSubmitButton);
    });
});