window.onload = function () {
    // Realizar la solicitud para obtener los productos
    axios.get('http://127.0.0.1:8000/perros')
        .then(function (response) {
            // Obtener el elemento de la tabla por ID
            const tabla = document.getElementById('tabla');
            
            // Limpiar el contenido previo (en caso de que haya)
            tabla.innerHTML = '';

            // Iterar sobre los productos y agregarlos a la tabla
            response.data.forEach(producto => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${producto.id}</td>
                    <td>${producto.nombre}</td>
                    <td>${producto.descripcion}</td>
                    <td>${producto.precio}</td>
                    <td>${producto.cantidad}</td> 
                    <td>
                        <button onclick="editarFila(this)">Editar</button>
                        <button class="btn-eliminar" onclick="confirmarEliminar(${producto.id})">Eliminar</button>
                    </td>
                `;
                tabla.appendChild(row); // Asegúrate de que esto esté fuera del template literal
            });
        })
        .catch(function (error) {
            console.error('Error al obtener productos:', error);
        });
}

function buscar() {
    const input = document.querySelector('.search-input');
    const filter = input.value.toLowerCase();
    const tabla = document.getElementById('tablaProductos');
    const filas = tabla.getElementsByTagName('tr');

    for (let i = 1; i < filas.length; i++) {
        let mostrarFila = false;
        const celdas = filas[i].getElementsByTagName('td');

        for (let j = 0; j < celdas.length - 1; j++) {
            const textoCelda = celdas[j].textContent || celdas[j].innerText;
            if (textoCelda.toLowerCase().indexOf(filter) > -1) {
                mostrarFila = true;
                break;
            }
        }

        filas[i].style.display = mostrarFila ? '' : 'none';
    }
}

function buscarProducto() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const tabla = document.getElementById('tabla');
    const filas = tabla.getElementsByTagName('tr');

    // Recorre todas las filas de la tabla
    for (let i = 1; i < filas.length; i++) { // Empieza en 1 para saltar el encabezado
        let mostrarFila = false;
        const celdas = filas[i].getElementsByTagName('td');

        // Revisa todas las celdas de la fila
        for (let j = 0; j < celdas.length; j++) {
            const textoCelda = celdas[j].textContent || celdas[j].innerText;
            if (textoCelda.toLowerCase().indexOf(filter) > -1) {
                mostrarFila = true;
                break;
            }
        }

        // Muestra u oculta la fila según el resultado
        filas[i].style.display = mostrarFila ? '' : 'none';
    }
}

// Evento de búsqueda
document.getElementById('searchInput').addEventListener('keyup', buscarProducto); 

function mostrarModalAgregar() {
    document.getElementById('modalTitle').textContent = 'Agregar Producto';
    document.getElementById('productoForm').reset();
    document.getElementById('productoModal').style.display = 'block';
}

function cerrarModal2() {
    document.getElementById('productoModal').style.display = 'none';
}

function editarFila(boton) {
    const fila = boton.closest('tr');
    const celdas = fila.cells;
    const modal = document.getElementById('modalEdicion');
    
    document.getElementById('editId').value = celdas[0].textContent;
    document.getElementById('editNombre').value = celdas[1].textContent;
    document.getElementById('editDescripcion').value = celdas[2].textContent;
    document.getElementById('editPrecio').value = celdas[3].textContent;
    document.getElementById('editCantidad').value = celdas[4].textContent;
    
    modal.style.display = 'block';
}

function guardarCambios() {
    const id = document.getElementById('editId').value;
    const nombre = document.getElementById('editNombre').value;
    const descripcion = document.getElementById('editDescripcion').value;
    const precio = parseFloat(document.getElementById('editPrecio').value);
    const cantidad = parseInt(document.getElementById('editCantidad').value);

    // Llamada al backend para actualizar
    axios.put(`http://127.0.0.1:8000/perros/${id}`, {
        nombre: nombre,
        descripcion: descripcion,
        precio: precio,
        cantidad: cantidad
    })
    .then(response => {
        // Actualizar la fila en la tabla si el backend respondió correctamente
        const fila = document.querySelector(`tr[data-id="${id}"]`);
        if (fila) {
            fila.cells[1].textContent = nombre;
            fila.cells[2].textContent = descripcion;
            fila.cells[3].textContent = precio;
            fila.cells[4].textContent = cantidad;
        }
        cerrarModal();
    })
    .catch(error => {
        console.error("Error al guardar cambios:", error);
        alert("Ocurrió un error al guardar los cambios.");
    });
}

function agregarProducto() {
    const nombre = document.getElementById('nombre').value;
    const descripcion = document.getElementById('descripcion').value;
    const precio = parseFloat(document.getElementById('precio').value);
    const cantidad = parseInt(document.getElementById('cantidad').value);

    // Llamada al backend para actualizar
    axios.post('http://127.0.0.1:8000/perros', {
        nombre: nombre,
        descripcion: descripcion,
        precio: precio,
        cantidad: cantidad
    })
    .then(response => {
        const producto = response.data;
        const tabla = document.getElementById('tabla');
        const nuevaFila = tabla.insertRow();

        nuevaFila.setAttribute('data-id', producto.id);
        nuevaFila.innerHTML = `
            <td>${producto.id}</td>
            <td>${producto.nombre}</td>
            <td>${producto.descripcion}</td>
            <td>${producto.precio}</td>
            <td>${producto.cantidad}</td>
            <td>
                <button onclick="editarFila(this)">Editar</button>
                <button onclick="confirmarEliminar(${producto.id})">Eliminar</button>
            </td>
        `;
        cerrarModal2();
    })
    .catch(error => {
        console.error("Error al agregar producto:", error);
        alert("Ocurrió un error al agregar el producto.");
    });
}

function cerrarModal() {
    document.getElementById('modalEdicion').style.display = 'none';
}
function cerrarModal2() {
    document.getElementById('productoModal').style.display = 'none';
}

////////////////////////////////////////////////////////////////////////////////
// Manejar envío del formulario para agregar o actualizar
document.getElementById('productoForm').addEventListener('submit', async function(e) {e.preventDefault();

// Capturar datos del formulario
const productoData = {
    nombre: document.getElementById('nombre').value.trim(),
    descripcion: document.getElementById('descripcion').value.trim(),
    precio: parseFloat(document.getElementById('precio').value),
    cantidad: parseInt(document.getElementById('cantidad').value, 11),
};

// Validar datos antes de enviar
if (isNaN(productoData.precio) || isNaN(productoData.cantidad)) {
    alert("Por favor, ingrese un precio y cantidad válidos.");
    return;
}

const id = document.getElementById('productoId').value;

try {
    if (id) {
        // Actualizar producto si existe un ID
        const response = await axios.put(`http://127.0.0.1:8000/perros/${id}`, productoData);

        // Actualizar fila en la tabla
        const fila = document.querySelector(`tr[data-id="${id}"]`);
        if (fila) {
            fila.cells[1].textContent = productoData.nombre;
            fila.cells[2].textContent = productoData.descripcion;
            fila.cells[3].textContent = `$${productoData.precio.toFixed(2)}`;
            fila.cells[4].textContent = productoData.cantidad;
        }
    } else {
        // Agregar producto si no hay ID
        const response = await axios.post('http://127.0.0.1:8000/perros', productoData);

        // Agregar nueva fila a la tabla
        const producto = response.data;
        const tabla = document.getElementById('tablaProductos');
        const nuevaFila = tabla.insertRow();

        nuevaFila.setAttribute('data-id', producto.id);
        nuevaFila.innerHTML = `
            <td>${producto.id}</td>
            <td>${producto.nombre}</td>
            <td>${producto.descripcion}</td>
            <td>$${producto.precio.toFixed(2)}</td>
            <td>${producto.cantidad}</td>
            <td>
                <button onclick="editarFila(this)">Editar</button>
                <button onclick="eliminarProducto(${producto.id})">Eliminar</button>
            </td>
        `;
    }

    // Limpiar formulario y cerrar modal
    cerrarModal();
} catch (error) {
    console.error("Error al procesar el formulario:", error);
    alert("Ocurrió un error al procesar el formulario.");
}
});

function confirmarEliminar(id) {
// Muestra el modal de confirmación
document.getElementById('modalConfirmDelete').style.display = 'block';

// Asigna el ID del producto al campo oculto
document.getElementById('deleteId').value = id;
}

function eliminarProducto() {
const id = document.getElementById('deleteId').value;

// Llamada al backend para eliminar el producto
axios.delete(`http://127.0.0.1:8000/perros/${id}`)
    .then(() => {
        // Eliminar la fila de la tabla correspondiente al producto
        const fila = document.querySelector(`tr[data-id="${id}"]`);
        if (fila) {
            fila.remove();
        }

        // Cerrar el modal de confirmación
        cerrarModalConfirm();
    })
    .catch(error => {
        console.error("Error al eliminar el producto:", error);
        alert("Ocurrió un error al intentar eliminar el producto.");
    });
}

function cerrarModal() {
// Cierra el modal de edición
document.getElementById('modalEdicion').style.display = 'none';
}

function cerrarModalConfirm() {
// Cierra el modal de confirmación
document.getElementById('modalConfirmDelete').style.display = 'none';
}