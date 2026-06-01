import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import { apiGet, apiPost } from '../api/client';
import { ShoppingCart } from 'lucide-react';
import { toast } from 'react-toastify';

function ProductsPage() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        async function fetchProducts() {
            try {
                const data = await apiGet('/products');
                setProducts(data);
            } catch (err) {
                setError(err.message || 'Nie udało się pobrać produktów.');
            } finally {
                setLoading(false);
            }
        }
        fetchProducts();
    }, []);

    const handleAddToCart = async (productId) => {
        try {
            await apiPost('/cart/items', {
                product_id: productId,
                quantity: 1
            });
            toast.success('Dodano do koszyka!');
        } catch (err) {
            toast.error(err.message || 'Nie udało się dodać do koszyka.');
        }
    };

    return (
        <div>
            <Navbar />
            <main className="products-wrapper">
                <h2>Lista Produktów</h2>
                
                {error && <div className="error-message">{error}</div>}
                
                {loading ? (
                    <p>Ładowanie produktów...</p>
                ) : (
                    <div className="products-grid">
                        {products.length === 0 ? (
                            <p>Brak produktów w bazie.</p>
                        ) : (
                            products.map((product) => (
                                <article key={product.id} className="product-card">
                                    <h3>{product.name}</h3>
                                    <p className="product-desc">{product.description}</p>
                                    <div className="product-price">{product.price.toFixed(2)} PLN</div>
                                    <button 
                                        className="btn" 
                                        onClick={() => handleAddToCart(product.id)}
                                        style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                                    >
                                        <ShoppingCart size={18} />
                                        Do koszyka
                                    </button>
                                </article>
                            ))
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}

export default ProductsPage;