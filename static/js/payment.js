// Payment.js - Maneja la interacción con formulario de pago y botones

document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const paymentForm = document.getElementById('payment-form');
    const stripeButton = document.getElementById('stripe-button');
    
    // Si existe el formulario de pago
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(event) {
            // Desactivar botón durante el procesamiento para evitar múltiples envíos
            if (stripeButton) {
                stripeButton.disabled = true;
                stripeButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Procesando...';
            }
            
            // Continuar con el envío normal del formulario
            // El backend se encargará de crear la sesión de Stripe o procesar el pago
        });
    }
    
    // Función para formatear montos como moneda
    function formatCurrency(amount) {
        return new Intl.NumberFormat('es-PR', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }
    
    // Función para mostrar mensajes de estado
    function showMessage(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insertar al inicio del contenedor principal
        const container = document.querySelector('.payment-section .container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
        }
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 500);
        }, 5000);
    }
});
