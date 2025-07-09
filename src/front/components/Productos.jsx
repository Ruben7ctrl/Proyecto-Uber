import React, { useEffect, useState } from 'react';

const Productos = () => {
  const [productos, setProductos] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('https://miniature-goggles-x5px65xx9q6w2655-3001.app.github.dev/api/productos')
      .then((res) => {
        if (!res.ok) throw new Error('Error en la respuesta del servidor');
        return res.json();
      })
      .then((data) => {
        setProductos(data);
      })
      .catch((err) => {
        console.error('Error cargando productos:', err);
        setError('No se pudieron cargar los productos');
      });
  }, []);

  return (
    <div>
      <h2>Listado de productos</h2>
      {error && <p>{error}</p>}
      <ul>
        {productos.map((producto, index) => (
          <li key={index}>
            {Object.entries(producto).map(([clave, valor]) => (
              <div key={clave}><strong>{clave}:</strong> {valor?.toString()}</div>
            ))}
            <hr />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Productos;
