<h1 align="center"> PickSmart 🛒 </h1>
<br>
<p align="center">
AI-powered chatbot for real-time product search with contextual question-answering and personalized product recommendations empowered by the intelligent search agent and RAG system.
</p>
<br>

![image](https://github.com/user-attachments/assets/01c8e4f4-d6ab-4b3d-b63f-1e692f0cc24c)

## Usage
💬 Ask a question about a product.

🔍 Search multiple marketplaces and rank the results.

⭐ Receive personalized recommendations.

## Features
🧠 User query analysis: Converts user queries into three search-friendly queries.

🛒 Online shop integration: Loads and stores data from online marketplaces in a vector database.

⚡ Real-time online search: Searches and retrieves online stores based on user queries.

🎯 Product filtering: Extracts and ranks the most relevant products.

💬 Contextual response generation: Provides detailed answers with personalized recommendations.

## Demo

https://github.com/user-attachments/assets/04dfc77b-18fb-4dbc-b85c-22152af938ed

## Tech Stack
<img alt="Langchain" src="https://img.shields.io/badge/-langchain-013243?style=flat&logo=langchain&logoColor=white"> <img alt="Langgraph" src="https://img.shields.io/badge/-Langgraph-013243?style=flat&logo=Langgraph&logoColor=white"> <img alt="FastAPI" src="https://img.shields.io/badge/-Fastapi-013243?style=flat&logo=Fastapi&logoColor=white">

⚛️ **Frontend**: React

🚀 **Backend**: FastAPI

🔄 **Streaming**: Kafka

🧠 **RAG System**: LangChain, Chroma (vector store)

🤖 **Agents**: LangGraph, Tavily (search)

📡 **API Client**: Groq API

## Agent Actions
1. **Analyze User Query**: Converts user input into three search-friendly queries.  
2. **Search Vector Store**: Retrieves product from vector database. If no products are relevant, search from online websites.
3. **Search Online Shops**: Retrieves product data from online stores based on the generated queries.  
4. **Find Relevant Products**: Filters and extracts relevant items.  
5. **Rank and Recommend**: Analyzes search results and ranks products for the user.

 ```python
        graph = StateGraph(SearchAgentState)
        graph.add_node("analyze_query", self.analyze_query_node)
        graph.add_node("search_vector_store", self.search_vector_node)
        graph.add_node("search_online_shop", self.search_online_node)
        graph.add_node("analyze_and_rank", self.analyze_rank_node)
        graph.set_entry_point("analyze_query")
        graph.add_edge("analyze_query", "search_vector_store")
        graph.add_conditional_edges(
            "search_vector_store",
            self.should_continue,
            {False: "search_online_shop", True: "analyze_and_rank"}
        )
        graph.add_edge("search_online_shop", "analyze_and_rank")
        graph.set_finish_point("analyze_and_rank")
        self.graph = graph.compile(checkpointer=checkpointer)
 ```

## Configuration

Configure API keys in the `.env` file:
   ```env
    GROQ_API_KEY="<API_KEY>"
    TAVILY_API_KEY="<API_KEY>"
   ```
Configure Embedding model and LLM model in `model.yaml` file:
   ```env
   LLM: <LLM_MODEL>
   EMBEDDING: <EMBEDDING_MODEL>
   ```

## Running with Docker

Skip the installation and setup by running all servers in Docker. The website is hosted on `localhost:3000`.

```bash
cd PickSmart
docker-compose up --build
```


## Installation & Setup
1. Clone the repository:
   ```bash
   git https://github.com/phrugsa-limbunlom/PickSmart.git
   cd PickSmart
   ```

2. Install backend dependencies:
   ```bash
   pip install -r /chatbot-server/requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd chatbot-app
   npm install
   ```

4. Start the Kafka service.


5. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```

6. Run the frontend:
   ```bash
   npm start
   ```
