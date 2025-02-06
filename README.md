# PickSmart

An AI-powered chatbot application that delivers contextual question-answering with personalized product recommendations using a Retrieval-Augmented Generation (RAG) system and intelligent agents.

<video src="https://github.com/user-attachments/assets/cc4a49d2-066e-48be-bb07-338ee3767c0c" width="200" controls>
</video>

## Usage
- Ask a question about a product.
- The system will search multiple marketplaces and rank the results.
- Receive personalized recommendations.

## Features
- **User query analysis**: Converts user queries into three search-friendly queries.
- **Online shop integration**: Loads and stores data from online marketplaces in a vector database.
- **Real-time online search** Searches and retrieves online stores based on users queries
- **Product filtering**: Extracts and ranks the most relevant products.
- **Contextual response Generation**: Provides detailed answers with personalized recommendations.

## Tech Stack
<img alt="Langchain" src="https://img.shields.io/badge/-langchain-013243?style=flat&logo=langchain&logoColor=white"> <img alt="Langgraph" src="https://img.shields.io/badge/-Langgraph-013243?style=flat&logo=Langgraph&logoColor=white"> <img alt="FastAPI" src="https://img.shields.io/badge/-Fastapi-013243?style=flat&logo=Fastapi&logoColor=white">
- **Frontend**: React  
- **Backend**: FastAPI  
- **Streaming**: Kafka  
- **RAG system**: LangChain, Chroma (vector store)
- **Agents**: LangGraph, Tavily (search)  
- **API client**: Groq API

## Agent Actions
1. **Analyze User Query**: Converts user input into three search-friendly queries.  
2. **Search Vector Store**: Retrieves product from vector database. If no products relevant, search from online websites.
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
