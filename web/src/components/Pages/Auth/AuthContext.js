// Official React import
import { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const navigate = useNavigate();
    const navigateRef = useRef(navigate);
    const location = useLocation();
    const locationRef = useRef(location);

    const login = () => {
        setIsAuthenticated(true);
        localStorage.setItem('isAuthenticated', 'true');
        navigate("/menu");
    };

    const logout = () => {
        setIsAuthenticated(false);
        localStorage.setItem('isAuthenticated', 'false');
        navigate('/auth');
    };

    useEffect(() => {
        const storedAuth = localStorage.getItem('isAuthenticated');
        if (storedAuth === 'true') {
            setIsAuthenticated(true);
            if (locationRef.current.pathname !== "/") {
                navigateRef.current(locationRef.current.pathname);
            }
        } else {
            setIsAuthenticated(false);
        }
    }, []);

    return (
        <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
