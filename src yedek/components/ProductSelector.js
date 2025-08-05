import React from 'react';
function ProductSelector({ products, selectedId, onChange }) {
  return (
    <select className="product-selector" value={selectedId} onChange={onChange}>
      {products.map(product => (
        <option key={product.id} value={product.id}>
          {product.name} ({product.id})
        </option>
      ))}
    </select>
  );
}
export default ProductSelector;