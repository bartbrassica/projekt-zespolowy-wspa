import { useNavigate } from 'react-router-dom';
import { useAuth } from '../store/auth';

export const useLayoutActions = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return {
    handleLogout
  };
};