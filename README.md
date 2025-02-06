# PickSmart

An AI-powered chatbot application that delivers contextual question-answering with personalized product recommendations using a Retrieval-Augmented Generation (RAG) system and intelligent agents.

![image](https://github.com/user-attachments/assets/38b0dfb1-3b4c-478f-a858-7cd56c281cab)

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

## Configuration

Configure API keys in the `.env` file:
   ```env
    GROQ_API_KEY="<API_KEY>"
    TAVILY_API_KEY="<API_KEY>"
   ```
Configure Embedding model and LLM model in `model.yaml` file:

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
## Docker running

```bash
   cd PickSmart
   docker-compose up --build
```
