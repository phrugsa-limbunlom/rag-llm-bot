import React, {useState, useRef, useEffect} from "react";
import axios from "axios";
import "./App.css";

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({behavior: "smooth"});
    };

    useEffect(scrollToBottom, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = {text: input, sender: "user"};
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setInput("");
        setLoading(true);

        try {
            const res = await axios.post("http://localhost:8000/api/chat", {
                user: "user",
                message: input,
            });
            const botMessage = {text: res.data.response, sender: "bot"};
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (err) {
            const errorMessage = {
                text: err.response?.data?.error || "An error occurred.",
                sender: "error",
            };
            setMessages((prevMessages) => [...prevMessages, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>PickSmart: AI-Powered Product Search</h1>
            </header>
            <div className="chat-container">
                <div className="messages">
                    {messages.map((message, index) => (
                        <div key={index} className={`message ${message.sender}`}>
                            {message.text}
                        </div>
                    ))}
                    {loading && (
                        <div className="message bot">
                            <div className="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef}/>
                </div>
                <form onSubmit={handleSubmit} className="input-form">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        disabled={loading}
                    />
                    <button type="submit" disabled={loading}>
                        Send
                    </button>
                </form>
            </div>
        </div>
    );
}

export default App;