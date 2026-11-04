from langchain_community.vectorstores import FAISS

def create_vector_db(folder_path, embedding):
    return FAISS.load_local(
        folder_path,
        embedding,
        allow_dangerous_deserialization=True
    )

load_vector_db = create_vector_db