import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import StatusBadge from '../components/StatusBadge';
import { apiGet, apiRequest } from '../api/client';
import useCurrentOperator from '../hooks/useCurrentOperator';
import { ArrowLeft, CheckCircle } from 'lucide-react';
import { toast } from 'react-toastify';

function OrderDetailsPage() {
    const { orderId } = useParams();
    const { authLoading, authError } = useCurrentOperator();
    
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [completeLoading, setCompleteLoading] = useState(false);

    const loadOrderDetails = async () => {
        try {
            const data = await apiGet(`/orders/${orderId}`);
            setOrder(data);
        } catch (err) {
            setError(err.message || 'Nie udało się pobrać szczegółów zamówienia.');
        } finally {
            setLoading(false);
        }
    };

    const handleCompleteOrder = async () => {
        setError('');
        setCompleteLoading(true);

        try {
            await apiRequest(`/orders/${orderId}/complete`, {
                method: "POST",
                headers: {
                    "Idempotency-Key": crypto.randomUUID(),
                },
            });
            
            toast.success("Zamówienie zostało zakończone.");
            await loadOrderDetails();
        } catch (err) {
            setError(err.message);
            toast.error(err.message);
        } finally {
            setCompleteLoading(false);
        }
    };

    useEffect(() => {
        if (!authLoading && !authError) {
            loadOrderDetails();
        }
    }, [authLoading, authError, orderId]);

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
        return null;
    }

    return (
        <div>
            <Navbar />
            <main className="orders-wrapper">
                <Link to="/orders" className="back-link">
                    <ArrowLeft size={18} />
                    Powrót do historii
                </Link>

                {loading && <p>Ładowanie zamówienia...</p>}

                {error && <div className="error-message">{error}</div>}

                {!loading && !error && !order && (
                    <div className="empty-state card">
                        <p>Nie znaleziono takiego zamówienia.</p>
                    </div>
                )}

                {!loading && !error && order && (
                    <div className="order-details-card">
                        <div className="order-header" style={{ marginBottom: '1.5rem' }}>
                            <h2>Zamówienie: {order.order_number}</h2>
                            <StatusBadge status={order.status} />
                        </div>
                        
                        <div className="order-summary">
                            <p>Data złożenia: {new Date(order.created_at).toLocaleString()}</p>
                            <p>Ilość przedmiotów: {order.products_count}</p>
                            <p>Suma do zapłaty: <strong>{order.total_price.toFixed(2)} PLN</strong></p>
                        </div>

                        <h3>Produkty</h3>
                        {order.items && order.items.length > 0 ? (
                            <div className="order-items-list">
                                {order.items.map((item) => (
                                    <div key={item.id} className="order-item-row">
                                        <div className="item-name">{item.product_name}</div>
                                        <div className="item-qty">{item.quantity} szt.</div>
                                        <div className="item-price">{(item.price).toFixed(2)} PLN</div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p>Brak przedmiotów zamówienia.</p>
                        )}

                        <div className="order-actions-bar" style={{ marginTop: '2rem', borderTop: '1px solid #333', paddingTop: '1.5rem' }}>
                            {order.status === "PENDING" ? (
                                <button
                                    className="btn"
                                    onClick={handleCompleteOrder}
                                    disabled={completeLoading}
                                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', backgroundColor: '#4caf50', color: '#fff' }}
                                >
                                    <CheckCircle size={20} />
                                    {completeLoading ? "Kończenie zamówienia..." : "Zakończ zamówienie"}
                                </button>
                            ) : (
                                <div className="info-box" style={{ padding: '1rem', backgroundColor: '#2c2c2c', borderRadius: '8px', color: '#aaa', textAlign: 'center' }}>
                                    <p style={{ margin: 0 }}>
                                        To zamówienie ma status <strong>{order.status}</strong> i nie może zostać ponownie zakończone.
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default OrderDetailsPage;