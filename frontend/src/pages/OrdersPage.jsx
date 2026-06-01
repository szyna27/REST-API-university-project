import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import StatusBadge from '../components/StatusBadge';
import { apiGet } from '../api/client';
import useCurrentOperator from '../hooks/useCurrentOperator';

function OrdersPage() {
    const { authLoading, authError } = useCurrentOperator();
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        async function loadOrders() {
            try {
                const data = await apiGet('/orders');
                setOrders(data);
            } catch (err) {
                setError(err.message || 'Błąd podczas pobierania zamówień.');
            } finally {
                setLoading(false);
            }
        }

        if (!authLoading && !authError) {
            loadOrders();
        }
    }, [authLoading, authError]);

    if (authLoading) {
        return (
            <main className="page">
                <section className="card">
                    <p>Sprawdzanie sesji...</p>
                </section>
            </main>
        );
    }

    if (authError) {
        return null; // Zostanie przekierowane w hooku
    }

    return (
        <div>
            <Navbar />
            <main className="orders-wrapper">
                <h2>Historia Zamówień</h2>

                {loading && <p>Ładowanie zamówień...</p>}

                {error && <div className="error-message">{error}</div>}

                {!loading && !error && orders.length === 0 && (
                    <div className="empty-state card">
                        <p>Brak historii zamówień.</p>
                        <p>Przejdź do produktów, wrzuć coś do koszyka i złóż zamówienie.</p>
                    </div>
                )}

                {!loading && !error && orders.length > 0 && (
                    <div className="orders-list">
                        {orders.map((order) => (
                            <div key={order.id} className="order-card">
                                <div className="order-header">
                                    <h3>{order.order_number}</h3>
                                    <StatusBadge status={order.status} />
                                </div>
                                <div className="order-info">
                                    <p>Ilość produktów: <strong>{order.products_count}</strong></p>
                                    <p>Suma: <strong>{order.total_price.toFixed(2)} PLN</strong></p>
                                    <p>Złożono: {new Date(order.created_at).toLocaleString()}</p>
                                </div>
                                <div className="order-actions">
                                    <Link to={`/orders/${order.id}`} className="btn-details">
                                        Szczegóły
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}

export default OrdersPage;