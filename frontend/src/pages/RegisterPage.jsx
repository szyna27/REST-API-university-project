import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiPost } from '../api/client';

function RegisterPage() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirm_password: '',
        first_name: '',
        last_name: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        if (formData.password !== formData.confirm_password) {
            setError('Hasła nie są identyczne.');
            return;
        }

        setLoading(true);
        try {
            await apiPost('/auth/register', formData);
            navigate('/login');
        } catch (err) {
            setError(err.message || 'Wystąpił błąd podczas rejestracji.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="page">
            <section className="card">
                <h2>Rejestracja</h2>
                {error && <div className="error-message">{error}</div>}
                
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            className="form-control"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    
                    <div className="form-group">
                        <label htmlFor="first_name">Imię</label>
                        <input
                            type="text"
                            id="first_name"
                            name="first_name"
                            className="form-control"
                            value={formData.first_name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="last_name">Nazwisko</label>
                        <input
                            type="text"
                            id="last_name"
                            name="last_name"
                            className="form-control"
                            value={formData.last_name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Hasło</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            className="form-control"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirm_password">Potwierdź hasło</label>
                        <input
                            type="password"
                            id="confirm_password"
                            name="confirm_password"
                            className="form-control"
                            value={formData.confirm_password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button type="submit" className="btn" disabled={loading}>
                        {loading ? 'Przetwarzanie...' : 'Zarejestruj się'}
                    </button>
                </form>

                <p style={{ marginTop: '1rem', textAlign: 'center' }}>
                    Masz już konto? <Link to="/login">Zaloguj się</Link>
                </p>
            </section>
        </main>
    );
}

export default RegisterPage;