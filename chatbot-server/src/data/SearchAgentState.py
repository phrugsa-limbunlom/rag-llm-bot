from typing import TypedDict, List


class SearchAgentState(TypedDict):
    user_query: str
    revised_query: List[str]
    relevant_products: str
    result: str
    final_result: List[dict]