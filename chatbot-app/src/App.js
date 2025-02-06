import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { FaRobot } from "react-icons/fa";
import { Send } from "lucide-react";
import "./App.css";

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    const endpoint = "/api/chat";
    const url = `${backendUrl}${endpoint}`;

    const scrollToBottom = () => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    };

    useEffect(() => {
        if (messagesEndRef.current) {
            scrollToBottom();
        }
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { text: input, sender: "user" };
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setInput("");
        setLoading(true);

        try {
            const res = await axios.post(url, {
                user: "user",
                message: input,
            });

            const data = res.data;
            const structuredMessages = [];

            const response = JSON.parse(data.value);

            console.log(response);

            // Default Message
            if (response.default) {
                structuredMessages.push({ text: response.default, sender: "bot" });
            }

            // Initial Message
            if (response.initial) {
                structuredMessages.push({ text: response.initial.message, sender: "bot" });
            }

            console.log(response.products);
            // Product Cards
            if (response.products) {
                structuredMessages.push(
                    ...response.products.map((product) => ({
                        title: product.title,
                        description: product.description,
                        sender: "products",
                    }))
                );
            }

            // Final Message
            if (response.final) {
                structuredMessages.push({ text: response.final.message, sender: "bot" });
            }

            setMessages((prevMessages) => [...prevMessages, ...structuredMessages]);
        } catch (err) {
            console.error(err);
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
                    {messages.map((message, index) =>
                        message.sender === "products" ? (
                            <div key={index} className={`message ${message.sender}`}>
                                <h5>{message.title}</h5>
                                <p>{message.description}</p>
                            </div>
                        ) : (
                            <div key={index} className={`message ${message.sender}`}>
                                {message.sender === "bot" && <FaRobot className="bot-icon" />}
                                {message.text}
                            </div>
                        )
                    )}
                    {loading && (
                        <div className="message bot">
                            <div className="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
                <form onSubmit={handleSubmit} className="input-form">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="p-2 rounded-full bg-blue-500 text-white disabled:opacity-50"
                    >
                        <Send size={20} />
                    </button>
                </form>
            </div>
        </div>
    );
}

export default App;