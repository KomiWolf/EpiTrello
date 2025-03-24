// Officials React import
import { Navigate } from 'react-router-dom';

// Our import
import { useAuth } from '../components/Pages/Auth/AuthContext';

const ProtectedRoute = ({ element }) => {
    const { isAuthenticated } = useAuth();

    return isAuthenticated ? element : <Navigate to="/auth" replace />;
};

export default ProtectedRoute;
