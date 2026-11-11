import ProductsPage from './pages/ProductsPage.jsx';
import { Routes, Route, Link } from 'react-router';
import BrowsePage from './pages/BrowsePage.jsx';
import ProductDetailPage from './pages/ProductDetailPage.jsx';
function App() {
    return (
        <>
            <nav>
                <Link to="/">All Products</Link> | <Link to="browse"> browse</Link>
            </nav>

            <Routes>
                <Route path="/" element={<ProductsPage />} />
                <Route path="*" element={<h1>404 Not Found</h1>} />
                <Route path="/browse" element={<BrowsePage />} />
                <Route path="/products/:id" element={<ProductDetailPage />} />
            </Routes>
        </>
    );
}

export default App;