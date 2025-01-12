import React, {useState} from "react";
import axios from "axios";
import "./App.css";

function App() {
    const [query, setQuery] = useState("");
    const [response, setResponse] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setResponse("");

        try {
            const res = await axios.post("http://127.0.0.1:5000/chat", {
                query,
            });
            setResponse(res.data.response);
        } catch (err) {
            setError(err.response?.data?.error || "An error occurred.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>AI Chatbot</h1>
                {response && (
                    <div>
                        <h3>Bot Response:</h3>
                        <p>{response}</p>
                    </div>
                )}
                {error && (
                    <div style={{color: "red"}}>
                        <h3>Error:</h3>
                        <p>{error}</p>
                    </div>
                )}
                <form onSubmit={handleSubmit} style={{marginBottom: "20px"}}>
          <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your query here..."
              rows="4"
              cols="50"
              required
          />
                    <br/>
                    <button type="submit" disabled={loading}>
                        {loading ? "Loading..." : "Send"}
                    </button>
                </form>
            </header>
        </div>
    );
}

export default App;