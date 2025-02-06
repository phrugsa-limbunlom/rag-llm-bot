from service.ChatbotService import ChatbotService

if __name__ == "__main__":
    service = ChatbotService()
    service.initialize_service()

    service.generate_answer_with_agent("I need a laptop under 1000 pounds")