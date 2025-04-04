/**
 * Spa en Ruedas - Booking JavaScript
 * -------------------------------------------------- 
 */

document.addEventListener('DOMContentLoaded', function() {
    const bookingForm = document.getElementById('bookingForm');
    const dateInput = document.getElementById('booking-date');
    const locationSelect = document.getElementById('booking-location');
    const serviceSelect = document.getElementById('booking-service');
    const timeSelect = document.getElementById('booking-time');
    const servicePrice = document.getElementById('service-price');
    const serviceDuration = document.getElementById('service-duration');
    const bookingSummary = document.getElementById('booking-summary');
    const summaryService = document.getElementById('summary-service');
    const summaryDate = document.getElementById('summary-date');
    const summaryTime = document.getElementById('summary-time');
    const summaryLocation = document.getElementById('summary-location');
    const summaryPrice = document.getElementById('summary-price');
    
    // Inicializar datepicker
    if (dateInput) {
        flatpickr(dateInput, {
            minDate: "today",
            maxDate: new Date().fp_incr(60), // 60 días desde hoy
            dateFormat: "Y-m-d",
            disable: [
                function(date) {
                    // Deshabilitar domingos (0) y sábados por la tarde (6)
                    return (date.getDay() === 0);
                }
            ],
            locale: {
                firstDayOfWeek: 1,
                weekdays: {
                    shorthand: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'],
                    longhand: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
                },
                months: {
                    shorthand: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                    longhand: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
                }
            },
            onChange: function(selectedDates, dateStr, instance) {
                if (locationSelect.value) {
                    fetchAvailableTimeSlots(dateStr, locationSelect.value);
                }
                updateSummary();
            }
        });
    }
    
    // Evento de cambio de ubicación
    if (locationSelect) {
        locationSelect.addEventListener('change', function() {
            if (dateInput.value) {
                fetchAvailableTimeSlots(dateInput.value, this.value);
            }
            updateSummary();
        });
    }
    
    // Evento de cambio de servicio
    if (serviceSelect) {
        serviceSelect.addEventListener('change', function() {
            const selectedService = this.options[this.selectedIndex];
            const price = selectedService.getAttribute('data-price');
            const duration = selectedService.getAttribute('data-duration');
            
            if (servicePrice) {
                servicePrice.textContent = formatCurrency(price);
            }
            
            if (serviceDuration) {
                serviceDuration.textContent = `${duration} minutos`;
            }
            
            updateSummary();
        });
        
        // Disparar el evento change para establecer los valores iniciales
        serviceSelect.dispatchEvent(new Event('change'));
    }
    
    // Evento de cambio de hora
    if (timeSelect) {
        timeSelect.addEventListener('change', function() {
            updateSummary();
        });
    }
    
    // Función para obtener slots de tiempo disponibles
    function fetchAvailableTimeSlots(date, locationId) {
        if (!date || !locationId) return;
        
        timeSelect.disabled = true;
        timeSelect.innerHTML = '<option value="">Cargando horarios...</option>';
        
        // Hacer la solicitud AJAX
        fetch(`/slots_disponibles?fecha=${date}&ubicacion=${locationId}`)
            .then(response => response.json())
            .then(data => {
                timeSelect.innerHTML = '';
                
                if (data.slots && data.slots.length > 0) {
                    // Añadir opción por defecto
                    timeSelect.innerHTML = '<option value="">Selecciona una hora</option>';
                    
                    // Añadir slots disponibles
                    data.slots.forEach(slot => {
                        const option = document.createElement('option');
                        option.value = slot;
                        option.textContent = formatTime(slot);
                        timeSelect.appendChild(option);
                    });
                    
                    timeSelect.disabled = false;
                } else {
                    timeSelect.innerHTML = '<option value="">No hay horarios disponibles</option>';
                    timeSelect.disabled = true;
                }
            })
            .catch(error => {
                console.error('Error al obtener horarios disponibles:', error);
                timeSelect.innerHTML = '<option value="">Error al cargar horarios</option>';
                timeSelect.disabled = true;
            });
    }
    
    // Función para actualizar el resumen de reserva
    function updateSummary() {
        if (!bookingSummary) return;
        
        // Servicio
        if (serviceSelect && summaryService) {
            const selectedService = serviceSelect.options[serviceSelect.selectedIndex];
            if (selectedService && selectedService.value) {
                summaryService.textContent = selectedService.text;
            } else {
                summaryService.textContent = 'No seleccionado';
            }
        }
        
        // Fecha
        if (dateInput && summaryDate) {
            if (dateInput.value) {
                const date = new Date(dateInput.value);
                summaryDate.textContent = date.toLocaleDateString('es-PR', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                });
            } else {
                summaryDate.textContent = 'No seleccionada';
            }
        }
        
        // Hora
        if (timeSelect && summaryTime) {
            const selectedTime = timeSelect.options[timeSelect.selectedIndex];
            if (selectedTime && selectedTime.value) {
                summaryTime.textContent = selectedTime.text;
            } else {
                summaryTime.textContent = 'No seleccionada';
            }
        }
        
        // Ubicación
        if (locationSelect && summaryLocation) {
            const selectedLocation = locationSelect.options[locationSelect.selectedIndex];
            if (selectedLocation && selectedLocation.value) {
                summaryLocation.textContent = selectedLocation.text;
            } else {
                summaryLocation.textContent = 'No seleccionada';
            }
        }
        
        // Precio
        if (serviceSelect && summaryPrice) {
            const selectedService = serviceSelect.options[serviceSelect.selectedIndex];
            if (selectedService && selectedService.value) {
                const price = selectedService.getAttribute('data-price');
                summaryPrice.textContent = formatCurrency(price);
            } else {
                summaryPrice.textContent = formatCurrency(0);
            }
        }
        
        // Mostrar u ocultar el resumen
        if (serviceSelect.value && dateInput.value && timeSelect.value && locationSelect.value) {
            bookingSummary.classList.remove('d-none');
        } else {
            bookingSummary.classList.add('d-none');
        }
    }
    
    // Validación del formulario antes de enviar
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(event) {
            if (!validateBookingForm()) {
                event.preventDefault();
            }
        });
    }
    
    // Función para validar el formulario de reserva
    function validateBookingForm() {
        let isValid = true;
        
        // Validar servicio
        if (serviceSelect.value === '') {
            showError(serviceSelect, 'Por favor, selecciona un servicio');
            isValid = false;
        } else {
            removeError(serviceSelect);
        }
        
        // Validar fecha
        if (dateInput.value === '') {
            showError(dateInput, 'Por favor, selecciona una fecha');
            isValid = false;
        } else {
            removeError(dateInput);
        }
        
        // Validar ubicación
        if (locationSelect.value === '') {
            showError(locationSelect, 'Por favor, selecciona una ubicación');
            isValid = false;
        } else {
            removeError(locationSelect);
        }
        
        // Validar hora
        if (timeSelect.value === '') {
            showError(timeSelect, 'Por favor, selecciona una hora');
            isValid = false;
        } else {
            removeError(timeSelect);
        }
        
        // Validar campos del cliente
        const nameInput = document.getElementById('client-name');
        const emailInput = document.getElementById('client-email');
        const phoneInput = document.getElementById('client-phone');
        
        if (nameInput && nameInput.value.trim() === '') {
            showError(nameInput, 'Por favor, ingresa tu nombre');
            isValid = false;
        } else if (nameInput) {
            removeError(nameInput);
        }
        
        if (emailInput) {
            if (emailInput.value.trim() === '') {
                showError(emailInput, 'Por favor, ingresa tu correo electrónico');
                isValid = false;
            } else if (!isValidEmail(emailInput.value.trim())) {
                showError(emailInput, 'Por favor, ingresa un correo electrónico válido');
                isValid = false;
            } else {
                removeError(emailInput);
            }
        }
        
        if (phoneInput) {
            if (phoneInput.value.trim() === '') {
                showError(phoneInput, 'Por favor, ingresa tu número de teléfono');
                isValid = false;
            } else if (!isValidPhone(phoneInput.value.trim())) {
                showError(phoneInput, 'Por favor, ingresa un número de teléfono válido');
                isValid = false;
            } else {
                removeError(phoneInput);
            }
        }
        
        return isValid;
    }
    
    // Función para mostrar errores de validación
    function showError(inputElement, message) {
        const formGroup = inputElement.parentElement;
        const errorElement = formGroup.querySelector('.invalid-feedback') || document.createElement('div');
        
        if (!formGroup.querySelector('.invalid-feedback')) {
            errorElement.className = 'invalid-feedback';
            formGroup.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        inputElement.classList.add('is-invalid');
    }
    
    // Función para eliminar errores de validación
    function removeError(inputElement) {
        inputElement.classList.remove('is-invalid');
    }
    
    // Inicializar la página con cualquier parámetro de URL
    function initializeFromUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const serviceId = urlParams.get('service');
        
        if (serviceId && serviceSelect) {
            serviceSelect.value = serviceId;
            serviceSelect.dispatchEvent(new Event('change'));
        }
    }
    
    initializeFromUrlParams();
});
