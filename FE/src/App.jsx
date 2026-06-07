import { useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import ChatsPage from "./pages/ChatsPage";

export default function App() {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        return <LoginPage />;
    }

    return <ChatsPage />;
}
