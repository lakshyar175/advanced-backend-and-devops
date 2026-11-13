// import Login from "./components/Login.jsx";
// import Register from "./components/Register.jsx"

// function App() {
//     return (
//         <>
//             <Login />
//             <Register />
//         </>
//     );
// }

// export default App;

import Login from "./components/Login.jsx";
import Register from "./components/Register.jsx";
import "./App.css";

function App() {
    return (
        <div className="auth-container">
            <div className="auth-box">
                <Login />
            </div>

            <div className="auth-box">
                <Register />
            </div>
        </div>
    );
}

export default App;