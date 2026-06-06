import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import StatusBadge from '../components/StatusBadge';
import { apiGet } from '../api/client';
import useCurrentOperator from '../hooks/useCurrentOperator';
import { LayoutDashboard } from 'lucide-react';

import EmptyState from '../components/EmptyState';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

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
                    <LoadingState message="Sprawdzanie sesji..." />
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

                {summaryLoading && <LoadingState message="Ładowanie podsumowania..." />}

                {summaryError && <ErrorState message={summaryError} />}

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

                            <div className="summary-card">
                                <span>Anulowane</span>
                                <strong>{summary.cancelled_orders}</strong>
                            </div>
                        </div>

                        <div className="recent-orders">
                            <h3 style={{ marginTop: '3rem', marginBottom: '1.5rem', color: '#fff' }}>Ostatnie zamówienia</h3>

                            {!summary.recent_orders || summary.recent_orders.length === 0 ? (
                                <EmptyState
                                    title="Brak ostatnich zamówień."
                                    description="Historia ostatnich zamówień pojawi się po złożeniu pierwszego zamówienia."
                                />
                            ) : (
                                <div className="orders-list">
                                    {summary.recent_orders.map((order) => (
                                        <div key={order.id} className="order-card" style={{ maxWidth: '600px', marginBottom: '1rem' }}>
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
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}

export default DashboardPage;