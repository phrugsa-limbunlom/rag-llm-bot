import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

const ChatBot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    const endpoint = '/api/chat';
    const url = `${backendUrl}${endpoint}`;

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

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
            const botMessage = { text: res.data.value, sender: "bot" };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (err) {
            console.error(err)
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
        <div className="min-h-screen bg-gray-900 text-gray-200 flex flex-col font-sans">
            <header className="bg-gray-800 text-white p-4 shadow-lg flex items-center justify-center border-b border-gray-700">
                <h1 className="text-3xl font-bold">PickSmart: AI-Powered Product Search</h1>
            </header>
            <div className="flex-grow flex flex-col p-6 max-w-2xl mx-auto">
                <div className="flex-grow overflow-y-auto mb-4 space-y-4 p-4 bg-gray-800 rounded-lg shadow-lg">
                    {messages.map((message, index) => (
                        <div key={index} className={`p-3 rounded-lg max-w-sm text-sm font-medium shadow-md transition-all duration-300 ${
                            message.sender === 'user' ? 'bg-blue-600 text-white ml-auto' :
                            message.sender === 'bot' ? 'bg-gray-700 text-gray-200' : 'bg-red-600 text-white'
                        }`}>
                            {message.text}
                        </div>
                    ))}
                    {loading && (
                        <div className="bg-gray-700 p-3 rounded-lg max-w-xs">
                            <div className="flex space-x-1">
                                <div className="bg-gray-500 rounded-full w-2 h-2 animate-bounce"></div>
                                <div className="bg-gray-500 rounded-full w-2 h-2 animate-bounce delay-100"></div>
                                <div className="bg-gray-500 rounded-full w-2 h-2 animate-bounce delay-200"></div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
                <form onSubmit={handleSubmit} className="flex items-center border border-gray-600 rounded-lg overflow-hidden">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        disabled={loading}
                        className="flex-grow p-3 bg-gray-800 border-none text-white placeholder-gray-500 focus:outline-none"
                    />
                    <button 
                        type="submit" 
                        disabled={loading}
                        className="bg-blue-600 text-white px-6 py-3 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300 disabled:bg-blue-400"
                    >
                        Send
                    </button>
                </form>
            </div>
        </div>
    );
}

export default ChatBot;