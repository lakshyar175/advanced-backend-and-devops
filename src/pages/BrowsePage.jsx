import { useState, useEffect } from 'react';


export default function ProductsPage() {
    const [products, setProducts] = useState([]);
    const [page, setPage] = useState(1);
    useEffect(() => {
        async function loadProducts() {
            const skip = (page - 1) * 10;
            const res = await fetch(`https://dummyjson.com/products?limit=10&skip=${skip}`);
            const data = await res.json();
            
            setProducts(data.products);
        }
        loadProducts();
    }, [page]);
    return (
        <>
        <button disabled={page === 1} onClick={()=> setPage(page -1)}>Previous</button>
        <p>Page {page}</p>
        <button onClick={()=> setPage(page +1)}>Next</button>
        <p>Loaded {products.length} products.</p>
         <ul>
            {products.map((product)=>(
                <li key={product.id} >
                    <img src= {product.thumbnail}></img>
                     <h3> {product.title} </h3>
                     <p> Price: ${product.price} </p>
                     </li>
            ))}
         </ul>
        </>
       
        
    );
}