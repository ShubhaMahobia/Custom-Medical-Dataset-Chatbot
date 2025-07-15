from langchain.prompts import PromptTemplate

system_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are an assistant for question-answering task. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that "
        "you don't know the answer. Use three sentences maximum and keep the answer concise.\n\n"
        "Context: {context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
)