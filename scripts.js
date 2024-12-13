const apiBaseUrl = 'http://127.0.0.1:8000';

async function fetchProducts(page = 1) {
    try {
        const response = await fetch(`${apiBaseUrl}/product/list?page=${page}`);
        const products = await response.json();
        displayProducts(products);
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

function displayProducts(products) {
    const productTable = document.getElementById('product-table');
    productTable.innerHTML = '';

    products.forEach(product => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${product.product_id}</td>
            <td>${product.name}</td>
            <td>${product.category}</td>
            <td>${product.description || 'N/A'}</td>
            <td>${product.sku}</td>
            <td>${product.unit_of_measure}</td>
            <td>${product.lead_time}</td>
            <td><button onclick="viewProduct(${product.product_id})">View</button></td>
        `;

        productTable.appendChild(row);
    });
}

async function viewProduct(productId) {
    try {
        const response = await fetch(`${apiBaseUrl}/product/${productId}/info`);
        const product = await response.json();
        alert(JSON.stringify(product, null, 2));
    } catch (error) {
        console.error('Error fetching product info:', error);
    }
}

async function addProduct() {
    const product = {
        name: document.getElementById('name').value,
        category: document.getElementById('category').value,
        description: document.getElementById('description').value,
        product_image: document.getElementById('product_image').value,
        sku: document.getElementById('sku').value,
        unit_of_measure: document.getElementById('unit_of_measure').value,
        lead_time: parseInt(document.getElementById('lead_time').value, 10),
    };

    try {
        const response = await fetch(`${apiBaseUrl}/product/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(product),
        });

        if (response.ok) {
            alert('Product added successfully!');
            fetchProducts();
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error adding product:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => fetchProducts());
