import json
import logging

import requests
from data.SearchAgentState import SearchAgentState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
from playwright.sync_api import sync_playwright
from service.VectorStoreService import VectorStoreService
from text.PromptMessage import PromptMessage
from text.WebURLs import WebURLs

logger = logging.getLogger(__name__)


class SearchAgent:

    def __init__(self, llm_model, embedding_model, tool, client, checkpointer=None):
        self.model = llm_model
        self.embedding_model = embedding_model
        self.tool = tool
        self.client = client
        graph = StateGraph(SearchAgentState)
        graph.add_node("analyze_query", self.analyze_query_node)
        graph.add_node("search_vector_store", self.search_vector_node)
        graph.add_node("search_online_shop", self.search_online_node)
        graph.add_node("analyze_and_rank", self.analyze_rank_node)
        graph.add_node("find_product_source", self.find_source_node)
        graph.set_entry_point("analyze_query")
        graph.add_edge("analyze_query", "search_vector_store")
        graph.add_conditional_edges(
            "search_vector_store",
            self.should_continue,
            {False: "search_online_shop", True: "analyze_and_rank"}
        )
        graph.add_edge("search_online_shop", "analyze_and_rank")
        # graph.add_edge("analyze_and_rank", "find_product_source")
        graph.set_finish_point("analyze_and_rank")
        # self.graph = graph.compile(checkpointer=checkpointer)
        self.graph = graph.compile()

    def call_client(self, prompt: str):
        try:
            if not isinstance(prompt, str):
                raise ValueError(f"Prompt must be a string, but got {type(prompt)}")

            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.5,
                max_tokens=1024,
                stop=None,
                stream=False,
            )
            return response.choices[0].message.content
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")

    def analyze_query_node(self, state: SearchAgentState):

        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=PromptMessage.ANALYZE_QUERY_PROMPT),
                HumanMessage(content=state['user_query'])
            ]
        )

        response = self.call_client(prompt.invoke({}).to_string())

        queries = []
        for query in response.split("|"):
            queries.append(query)

        return {"revised_query": queries}

    def search_vector_node(self, state: SearchAgentState):
        urls = [WebURLs.Amazon, WebURLs.Ebay]

        vector_retrievers = VectorStoreService(self.embedding_model).load_vector_store(urls)

        vector_retriever_amazon = vector_retrievers["amazon"]
        vector_retriever_ebay = vector_retrievers["ebay"]

        products = ""
        for query in state["revised_query"]:
            amazon_products = vector_retriever_amazon.invoke(query)
            ebay_products = vector_retriever_ebay.invoke(query)

            products = " ".join([doc.page_content for doc in amazon_products])
            products = products.join([doc.page_content for doc in ebay_products])

        return {"relevant_products": products}

    def search_online_node(self, state: SearchAgentState):

        products = state['relevant_products'] or []

        for query in state['revised_query']:

            query = f"find the specific product title from this product requirement: {query}"
            response = self.tool.search(query=query, max_results=1)

            for r in response['results']:
                products.append(r['content'])

        products = " ".join([product for product in products])

        return {"relevant_products": products}

    def analyze_rank_node(self, state: SearchAgentState):
        prompt = ChatPromptTemplate.from_messages([
            PromptMessage.ANALYZE_RANK_PROMPT,
            PromptMessage.ANALYZE_RANK_HUMAN_PROMPT
        ]).invoke({"products": state["relevant_products"], "requirements": state["user_query"]}).to_string()

        return {"result": self.call_client(prompt=prompt)}

    def find_source_node(self, state: SearchAgentState):

        results = json.loads(state['result'])

        for result in results["products"]:
            for k, v in list(result.items()):
                query = f"find source url for this product {v} from online shopping website"
                response = self.tool.search(query=query, max_results=6)
                result.update({"Source": response['results'][0]['url']})

        return {"final_result": results}

    def find_source_node(self, state: SearchAgentState):
        with sync_playwright() as p:
            results = json.loads(state['result'])

            browser = p.chromium.launch(headless=False,
                                        slow_mo=100,
                                        args=[
                                            '--disable-features=ImprovedCookieControls'
                                        ])
            context = browser.new_context(ignore_https_errors=True)

            context.add_cookies([
                {
                    'name': 'session_id',
                    'value': 'abc123',
                    'domain': 'example.com',
                    'path': '/'
                }
            ])
            page = context.new_page()

            for result in results["products"]:
                for k, v in list(result.items()):

                    page.goto(f"https://www.google.com")
                    page.click('text=Accept')

                    search_box = page.locator("input[name='q']")
                    search_box.fill(v)
                    search_box.press("Enter")

                    page.wait_for_selector("text=Shopping")
                    page.locator("text=Shopping").click()

                    page.wait_for_selector(".sh-dgr__content", timeout=10000)

                    product_cards = page.query_selector_all(".sh-dgr__content")

                    for card in product_cards:
                        try:
                            link_element = card.query_selector("a")
                            image_element = card.query_selector("img")

                            r = {
                                "link": link_element.get_attribute("href"),
                                "image": image_element.get_attribute("src") if image_element else None
                            }
                            result.update(r)
                            break
                        except:
                            continue

            browser.close()

        return {"final_result": results}

    def should_continue(self, state: SearchAgentState):

        if state["relevant_products"] == "":
            logger.info(f"Couldn't find the relevant products from vector store")
            logger.info(f"Start searching products online...")

        return state["relevant_products"] != ""
