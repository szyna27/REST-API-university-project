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
    const [fieldErrors, setFieldErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        // Clear field error when user starts typing
        if (fieldErrors[e.target.name]) {
            setFieldErrors({ ...fieldErrors, [e.target.name]: '' });
        }
    };

    const validateForm = () => {
        const errors = {};
        if (!formData.first_name.trim()) {
            errors.first_name = "Imię jest wymagane.";
        }
        if (!formData.last_name.trim()) {
            errors.last_name = "Nazwisko jest wymagane.";
        }
        if (!formData.email.trim()) {
            errors.email = "Email jest wymagany.";
        } else {
            const emailRegex = /\S+@\S+\.\S+/;
            if (!emailRegex.test(formData.email)) {
                errors.email = "Niepoprawny adres email.";
            }
        }
        if (formData.password.length < 8) {
            errors.password = "Hasło musi mieć co najmniej 8 znaków.";
        }
        if (formData.password !== formData.confirm_password) {
            errors.confirm_password = "Hasła nie są identyczne.";
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
                        <label htmlFor="first_name">Imię</label>
                        <input
                            type="text"
                            id="first_name"
                            name="first_name"
                            className={`form-control ${fieldErrors.first_name ? 'input-error' : ''}`}
                            value={formData.first_name}
                            onChange={handleChange}
                            required
                        />
                        {fieldErrors.first_name && <div className="field-error-message" style={{color: '#f44336', fontSize: '0.85rem', marginTop: '0.25rem'}}>{fieldErrors.first_name}</div>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="last_name">Nazwisko</label>
                        <input
                            type="text"
                            id="last_name"
                            name="last_name"
                            className={`form-control ${fieldErrors.last_name ? 'input-error' : ''}`}
                            value={formData.last_name}
                            onChange={handleChange}
                            required
                        />
                        {fieldErrors.last_name && <div className="field-error-message" style={{color: '#f44336', fontSize: '0.85rem', marginTop: '0.25rem'}}>{fieldErrors.last_name}</div>}
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

                    <div className="form-group">
                        <label htmlFor="confirm_password">Potwierdź hasło</label>
                        <input
                            type="password"
                            id="confirm_password"
                            name="confirm_password"
                            className={`form-control ${fieldErrors.confirm_password ? 'input-error' : ''}`}
                            value={formData.confirm_password}
                            onChange={handleChange}
                            required
                        />
                        {fieldErrors.confirm_password && <div className="field-error-message" style={{color: '#f44336', fontSize: '0.85rem', marginTop: '0.25rem'}}>{fieldErrors.confirm_password}</div>}
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