import os
import streamlit as st
import langid
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import os
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
# Initialize OpenAI client and embeddings
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedding = OpenAIEmbeddings(model="text-embedding-3-small")

# Load URLs from a text file
def load_urls_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

# Process PDF URLs to load and split pages
def process_pdfs(urls):
    pages = []
    for url in urls:
        loader = PyMuPDFLoader(url)
        pages += loader.load()
        
        # Filter out empty pages
        non_empty_pages = [page for page in pages if page.page_content.strip()]

        
    return non_empty_pages






# Create vector store with specific embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create FAISS vector store from documents
def create_vectorstore(pages):
    # Split the text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    data = text_splitter.split_documents(pages)
    return FAISS.from_documents(documents=data, embedding=embeddings)

# Load and process laws in German
laws_in_german = "Scraper\sample_german.txt"
german_urls = load_urls_from_file(laws_in_german)
german_pages = process_pdfs(german_urls)
german_vectorstore = create_vectorstore(german_pages)
german_vectorstore.save_local("English_faiss_index")

german_prompt = PromptTemplate(
                template= """
                                ###ANWEISUNGEN: 
                                Sie sind ein höflicher und professioneller KI-Assistent, der Fragen beantwortet. Sie müssen dem Benutzer eine hilfreiche Antwort geben. 

                                In Ihrer Antwort, BITTE IMMER:
                                (0) Seien Sie ein detailorientierter Leser: Lesen Sie die Frage und den Kontext und verstehen Sie beides, bevor Sie antworten
                                (1) Beginnen Sie Ihre Antwort mit einem freundlichen Ton und wiederholen Sie die Frage, damit der Nutzer sicher ist, dass Sie sie verstanden haben.
                                (2) Wenn der Kontext es Ihnen ermöglicht, die Frage zu beantworten, schreiben Sie eine detaillierte, hilfreiche und leicht verständliche Antwort mit Quellenangaben in der Zeile. WENN NICHT: Sie die Antwort nicht finden können, antworten Sie mit einer Erklärung, beginnend mit: „Ich konnte die Informationen in den mir zugänglichen Gesetzen nicht finden“. 
                                (3) Unter der Antwort geben Sie bitte alle Quellen an, auf die Sie sich beziehen (d.h. rechtliche Paragraphen, die Ihre Behauptungen untermauern).
                                (4) Jetzt haben Sie Ihre Antwort, das ist toll - überprüfen Sie Ihre Antwort, um sicherzustellen, dass sie die Frage beantwortet, hilfreich und professionell ist und so formatiert wurde, dass sie leicht zu lesen ist.
                                
                                Denken Sie Schritt für Schritt. 
                                ###
                                Beantworten Sie die folgende Frage anhand des vorgegebenen Kontexts.
                                ### Frage: {question} ###

                                ### Kontext: {context} ###
                                
                                ### Hilfreiche Antwort mit Quellenangaben:
                            """,
                input_variables=["question", "context"]

)

# Load and process laws in English
laws_in_english = "Scraper\sample_english.txt"
english_urls = load_urls_from_file(laws_in_english)
english_pages = process_pdfs(english_urls)
english_vectorstore = create_vectorstore(english_pages)
english_vectorstore.save_local("English_faiss_index")


english_prompt = PromptTemplate(
                                    template= """
                                        ###INSTRUCTIONS: 
                                        You are polite and professional question-answering AI assistant. You must provide a helpful response to the user. 
                                        
                                        In your response, PLEASE ALWAYS:
                                        (0) Be a detail-oriented reader: read the question and context and understand both before answering
                                        (1) Start your answer with a friendly tone, and reiterate the question so the user is sure you understood it
                                        (2) If the context enables you to answer the question, write a detailed, helpful, and easily understandable answer with sources referenced inline. IF NOT: you can't find the answer, respond with an explanation, starting with: "I couldn't find the information in the laws I have access to". 
                                        (3) Below the answer, please list out all the referenced sources (i.e. legal paragraphs backing up your claims)
                                        (4) Now you have your answer, that's amazing - review your answer to make sure it answers the question, is helpful and professional and formatted to be easily readable.
                                        
                                        Think step by step. 
                                        ###
                                        
                                    Answer the following question using the context provided.
                                        ### Question: {question} ###

                                        ### Context: {context} ###

                                        

                                        ### Helpful Answer with Sources:

                                    """,
                                    input_variables=["question", "context"]
)

# Setup memory and conversation chains
english_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
german_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

english_conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=english_vectorstore.as_retriever(),
    memory=english_memory,
    combine_docs_chain_kwargs={"prompt": english_prompt}
)

german_conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=german_vectorstore.as_retriever(),
    memory=german_memory,
    combine_docs_chain_kwargs={"prompt": german_prompt}
)

# Handle conversations based on detected language
def handle_conversation(input_data):
    question = input_data["question"]  # Extract the question from the input dictionary
    language, _ = langid.classify(question)  # Classify the language of the question
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []  # Initialize chat history if not already done

    if language == 'en':
        response = english_conversation_chain({"question": question, "chat_history": input_data["chat_history"]})
        st.session_state.conversation_history.append({"question": question, "answer": response["answer"]})
        return response["answer"]

    elif language == 'de':
        response = german_conversation_chain({"question": question, "chat_history": input_data["chat_history"]})
        st.session_state.conversation_history.append({"question": question, "answer": response["answer"]})
        return response["answer"]

    else:
        return "Please ask questions in either English or German."



# Manage unanswered questions
unanswered_questions_file = "unanswered_questions.txt"

if "unanswered_questions" not in st.session_state:
    st.session_state.unanswered_questions = []
    if os.path.exists(unanswered_questions_file):
        with open(unanswered_questions_file, "r") as file:
            st.session_state.unanswered_questions = [line.strip() for line in file]


st.write("Welcome!")
st.title("Agentic Chatbot for German Laws")
st.write("Ask your legal questions in English or German.")

# Ensure the conversation memory is initialized with required keys
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []  # Initialize chat history

# Input for user question
question = st.text_input("Your Question:")
if question.strip():  # Ensure the question is not empty
    try:
        # Provide the conversation history to the RAG chain
        answer = handle_conversation({"question": question, "chat_history": st.session_state["conversation_history"]})
        
        # Update the conversation history
        st.session_state["conversation_history"].append({"question": question, "answer": answer})

        # Display the question and answer
        st.markdown(f"**Your Question:** {question}")
        st.markdown(f"**Answer:** {answer}")

    except ValueError as e:
        st.error(f"Error processing your query: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
