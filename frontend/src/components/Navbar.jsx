import { NavLink, useNavigate } from "react-router-dom";
import { apiPost } from "../api/client";
import { Package, ShoppingCart, LogOut, FileText, LayoutDashboard } from "lucide-react";

function Navbar() {
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await apiPost("/auth/logout", {});
    } catch (err) {
      console.error(err);
    } finally {
      navigate("/login");
    }
  }

  return (
    <nav className="navbar">
      <div className="navbar-links">
        <NavLink 
          to="/dashboard" 
          className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
        >
          <LayoutDashboard size={20} />
          Dashboard
        </NavLink>
        <NavLink 
          to="/products" 
          className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
        >
          <Package size={20} />
          Produkty
        </NavLink>
        <NavLink 
          to="/cart" 
          className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
        >
          <ShoppingCart size={20} />
          Koszyk
        </NavLink>
        <NavLink 
          to="/orders" 
          className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
        >
          <FileText size={20} />
          Historia Zamówień
        </NavLink>
      </div>

      <button onClick={handleLogout} className="btn-logout">
        <LogOut size={18} />
        Wyloguj
      </button>
    </nav>
  );
}

export default Navbar;