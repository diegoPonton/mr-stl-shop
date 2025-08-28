document.addEventListener("DOMContentLoaded", () => {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    const tbody = document.getElementById("carrito-body");
    const totalSpan = document.getElementById("total-pagar");
    const pedidoInput = document.getElementById("pedido-json");
    const envioSelect = document.getElementById("envio");
    const formulario = document.getElementById("formulario-pedido");

    function calcularTotal() {
        let total = 0;
        carrito.forEach(producto => {
            total += producto.precio * producto.cantidad;
        });

        // Agregar costo de envío si se seleccionó "si"
        if (envioSelect && envioSelect.value === "si") {
            total += 6;
        }

        totalSpan.textContent = `$${total.toFixed(2)}`;
    }

    function renderCarrito() {
        tbody.innerHTML = ""; // limpiar tabla

        carrito.forEach((producto, index) => {
            producto.cantidad = producto.cantidad || 1;
            const subtotal = (producto.precio * producto.cantidad).toFixed(2);

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><img src="/static/img/${producto.imagen}" alt="${producto.nombre}"></td>
                <td>${producto.nombre}</td>
                <td>$${producto.precio.toFixed(2)}</td>
                <td><input type="number" value="${producto.cantidad}" min="1" data-index="${index}" class="cantidad-input"></td>
                <td class="subtotal">$${subtotal}</td>
                <td><button class="btn-eliminar" data-index="${index}">X</button></td>
            `;
            tbody.appendChild(tr);
        });

        // Cambiar cantidad
        document.querySelectorAll(".cantidad-input").forEach(input => {
            input.addEventListener("change", e => {
                const index = e.target.getAttribute("data-index");
                const nuevaCantidad = parseInt(e.target.value);
                if (nuevaCantidad > 0) {
                    carrito[index].cantidad = nuevaCantidad;
                    localStorage.setItem("carrito", JSON.stringify(carrito));
                    renderCarrito();
                }
            });
        });

        // Eliminar producto
        document.querySelectorAll(".btn-eliminar").forEach(btn => {
            btn.addEventListener("click", e => {
                const index = e.target.getAttribute("data-index");
                carrito.splice(index, 1);
                localStorage.setItem("carrito", JSON.stringify(carrito));
                renderCarrito();
            });
        });

        calcularTotal();

        // Actualizar JSON del pedido
        if (pedidoInput) {
            pedidoInput.value = JSON.stringify(carrito);
        }
    }

    // Escuchar cambios en el select de envío
    if (envioSelect) {
        envioSelect.addEventListener("change", calcularTotal);
    }

    // Asegurar que se actualice el resumen del pedido justo antes de enviarlo
    if (formulario) {
        formulario.addEventListener("submit", () => {
            pedidoInput.value = JSON.stringify(carrito);
        });
    }

    renderCarrito();
});