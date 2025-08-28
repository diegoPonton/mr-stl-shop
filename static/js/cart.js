window.agregarAlCarrito = function(producto) {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];

    // Verifica si ya está en el carrito
    const index = carrito.findIndex(p => p.id === producto.id);
    if (index >= 0) {
        carrito[index].cantidad += 1;
    } else {
        producto.cantidad = 1;
        carrito.push(producto);
    }

    localStorage.setItem("carrito", JSON.stringify(carrito));
    alert(`${producto.nombre} añadido al carrito`);
};