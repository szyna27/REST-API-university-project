import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import StatusBadge from '../components/StatusBadge';
import { apiGet } from '../api/client';
import useCurrentOperator from '../hooks/useCurrentOperator';
import { LayoutDashboard } from 'lucide-react';

function DashboardPage() {
    const { authLoading, authError } = useCurrentOperator();
    const [summary, setSummary] = useState(null);
    const [summaryLoading, setSummaryLoading] = useState(true);
    const [summaryError, setSummaryError] = useState("");

    async function loadSummary() {
        try {
            const data = await apiGet("/orders/dashboard/summary");
            setSummary(data);
        } catch (err) {
            setSummaryError(err.message || 'Nie udało się pobrać podsumowania.');
        } finally {
            setSummaryLoading(false);
        }
    }

    useEffect(() => {
        if (!authLoading && !authError) {
            loadSummary();
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
        return null;
    }

    return (
        <div>
            <Navbar />
            <main className="dashboard-wrapper">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
                    <LayoutDashboard size={32} color="#61dafb" />
                    <h2 style={{ margin: 0 }}>Dashboard</h2>
                </div>

                {summaryLoading && <p>Ładowanie podsumowania...</p>}

                {summaryError && <p className="error-message">{summaryError}</p>}

                {!summaryLoading && !summaryError && summary && (
                    <>
                        <div className="summary-grid">
                            <div className="summary-card">
                                <span>Wszystkie zamówienia</span>
                                <strong>{summary.total_orders}</strong>
                            </div>

                            <div className="summary-card">
                                <span>Oczekujące</span>
                                <strong>{summary.pending_orders}</strong>
                            </div>

                            <div className="summary-card">
                                <span>Zakończone</span>
                                <strong>{summary.completed_orders}</strong>
                            </div>
                        </div>

                        <div className="last-order-section">
                            <h3 style={{ marginTop: '3rem', marginBottom: '1.5rem', color: '#fff' }}>Ostatnie zamówienie</h3>

                            {summary.last_order ? (
                                <div className="order-card" style={{ maxWidth: '600px' }}>
                                    <div className="order-header">
                                        <h3>{summary.last_order.order_number}</h3>
                                        <StatusBadge status={summary.last_order.status} />
                                    </div>
                                    <div className="order-info">
                                        <p>Ilość produktów: <strong>{summary.last_order.products_count}</strong></p>
                                        <p>Suma: <strong>{summary.last_order.total_price.toFixed(2)} PLN</strong></p>
                                        <p>Złożono: {new Date(summary.last_order.created_at).toLocaleString()}</p>
                                    </div>
                                    <div className="order-actions">
                                        <Link to={`/orders/${summary.last_order.id}`} className="btn-details">
                                            Szczegóły
                                        </Link>
                                    </div>
                                </div>
                            ) : (
                                <div className="empty-state card" style={{ maxWidth: '600px' }}>
                                    <p>Brak historii zamówień.</p>
                                    <Link to="/products" className="btn" style={{ display: 'inline-block', textDecoration: 'none' }}>Przejdź do produktów</Link>
                                </div>
                            )}
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}

export default DashboardPage;