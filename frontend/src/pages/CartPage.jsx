import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import { apiGet, apiPatch, apiDelete, apiPost } from '../api/client';
import { Trash2, CreditCard } from 'lucide-react';
import { toast } from 'react-toastify';

function CartPage() {
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [actionLoading, setActionLoading] = useState(false);

    const fetchCart = async () => {
        try {
            const data = await apiGet('/cart');
            setCart(data);
        } catch (err) {
            setError(err.message || 'Nie udało się pobrać koszyka.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCart();
    }, []);

    const updateQuantity = async (itemId, newQuantity) => {
        if (newQuantity < 1) return;
        setActionLoading(true);
        try {
            const updatedCart = await apiPatch(`/cart/items/${itemId}`, { quantity: newQuantity });
            setCart(updatedCart);
        } catch (err) {
            toast.error(err.message || 'Błąd aktualizacji ilości.');
        } finally {
            setActionLoading(false);
        }
    };

    const removeItem = async (itemId) => {
        setActionLoading(true);
        try {
            await apiDelete(`/cart/items/${itemId}`);
            toast.success('Produkt usunięty z koszyka.');
            await fetchCart(); // Refresh cart after delete
        } catch (err) {
            toast.error(err.message || 'Błąd usuwania produktu.');
        } finally {
            setActionLoading(false);
        }
    };

    const handleCheckout = async () => {
        setActionLoading(true);
        try {
            await apiPost('/cart/checkout', {});
            toast.success('Zamówienie zostało złożone pomyślnie!');
            await fetchCart(); // Refresh to get empty cart
        } catch (err) {
            toast.error(err.message || 'Błąd podczas składania zamówienia.');
        } finally {
            setActionLoading(false);
        }
    };

    return (
        <div>
            <Navbar />
            <main className="cart-wrapper">
                <h2>Twój Koszyk</h2>

                {error && <div className="error-message">{error}</div>}

                {loading ? (
                    <p>Wczytywanie koszyka...</p>
                ) : !cart || cart.items.length === 0 ? (
                    <p>Twój koszyk jest pusty.</p>
                ) : (
                    <>
                        <div className="cart-items">
                            {cart.items.map((item) => (
                                <div key={item.id} className="cart-item">
                                    <div className="cart-item-info">
                                        <h3>{item.product.name}</h3>
                                        <p>{item.product.price.toFixed(2)} PLN / szt.</p>
                                    </div>

                                    <div className="cart-item-actions">
                                        <button 
                                            className="qty-btn" 
                                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                            disabled={actionLoading || item.quantity <= 1}
                                        >
                                            -
                                        </button>
                                        
                                        <span className="qty-display">{item.quantity}</span>
                                        
                                        <button 
                                            className="qty-btn" 
                                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                            disabled={actionLoading}
                                        >
                                            +
                                        </button>
                                        
                                        <button 
                                            className="remove-btn" 
                                            onClick={() => removeItem(item.id)}
                                            disabled={actionLoading}
                                            title="Usuń"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="cart-summary">
                            <h3>Razem: {cart.total_price.toFixed(2)} PLN</h3>
                            <button 
                                className="checkout-btn" 
                                onClick={handleCheckout}
                                disabled={actionLoading}
                                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                            >
                                <CreditCard size={20} />
                                Złóż zamówienie
                            </button>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}

export default CartPage;