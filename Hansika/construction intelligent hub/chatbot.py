def chatbot(question):

    q = question.lower()

    if "cost" in q:
        return "Cost depends on area and materials."

    elif "delay" in q:
        return "Rain and labor shortage may cause delay."

    elif "time" in q:
        return "Completion time depends on project size."

    return "Please ask construction related questions."