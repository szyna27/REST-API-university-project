import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiPost } from '../api/client';

function LoginPage() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [error, setError] = useState('');
    const [fieldErrors, setFieldErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        if (fieldErrors[e.target.name]) {
            setFieldErrors({ ...fieldErrors, [e.target.name]: '' });
        }
    };

    const validateForm = () => {
        const errors = {};
        if (!formData.email.trim()) {
            errors.email = "Email jest wymagany.";
        } else {
            const emailRegex = /\S+@\S+\.\S+/;
            if (!emailRegex.test(formData.email)) {
                errors.email = "Niepoprawny adres email.";
            }
        }
        if (!formData.password.trim()) {
            errors.password = "Hasło jest wymagane.";
        }
        
        setFieldErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            await apiPost('/auth/login', formData);
            // Po udanym logowaniu klient otrzyma ciastko, przekierowujemy na chronioną stronę
            navigate('/products');
        } catch (err) {
            setError(err.message || 'Nieprawidłowy email lub hasło.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="page">
            <section className="card">
                <h2>Logowanie</h2>
                {error && <div className="error-message">{error}</div>}
                
                <form onSubmit={handleSubmit} noValidate>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            className={`form-control ${fieldErrors.email ? 'input-error' : ''}`}
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                        {fieldErrors.email && <div className="field-error-message" style={{color: '#f44336', fontSize: '0.85rem', marginTop: '0.25rem'}}>{fieldErrors.email}</div>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Hasło</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            className={`form-control ${fieldErrors.password ? 'input-error' : ''}`}
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                        {fieldErrors.password && <div className="field-error-message" style={{color: '#f44336', fontSize: '0.85rem', marginTop: '0.25rem'}}>{fieldErrors.password}</div>}
                    </div>

                    <button type="submit" className="btn" disabled={loading}>
                        {loading ? 'Logowanie...' : 'Zaloguj się'}
                    </button>
                </form>

                <p style={{ marginTop: '1rem', textAlign: 'center' }}>
                    Nie masz konta? <Link to="/register">Zarejestruj się</Link>
                </p>
            </section>
        </main>
    );
}

export default LoginPage;