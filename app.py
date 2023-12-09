import streamlit as st
from dotenv import load_dotenv
from utils import *
import uuid

#Creating Unique ID
if 'unique_id' not in st.session_state:
    st.session_state['unique_id'] = ''
    

def main():
    load_dotenv()
    st.set_page_config(page_title="Digital Assistant with AI Capability")
    st.title("J.A.R.V.I.S: Master - Welcome back ...💁 ")
    st.subheader("J.A.R.V.I.S: Master, please go through steps before processing your input knowledge")
    
    with st.form("J.A.R.V.I.S: Master, please input Client PASSWORD"):
        st.session_state['unique_id'] = st.text_input("unique_id", value="", type="password")
        if st.form_submit_button("Submit"):
            st.session_state.prompt_history = []
            st.session_state.df = None
            st.success('J.A.R.V.I.S: Saved Authenticated Client identity in me')    
    enquiry = st.text_area("J.A.R.V.I.S: Please post the issues rasied by the client here...",key="1")
    document_count = st.text_input("J.A.R.V.I.S: Master, how many numbers of 'REFERENCE' you expect me to find to tackle the issue",key="2")
    
    # Upload the Resumes (pdf files)
    pdf = st.file_uploader("J.A.R.V.I.S: Master, please upload knowledge material here, only PDF files allowed", type=["pdf"],accept_multiple_files=True)

    submit=st.button("J.A.R.V.I.S, please help me with the professional analysis")

    if submit:
        with st.spinner('Wait for it...'):
            st.write("Client Unique ID")
            
            # Creating a unique ID, so that we can use to query and get only the user uploaded documents from vector store
            #st.session_state['unique_id']=uuid.uuid4().hex
            st.write(st.session_state['unique_id'])            
            
            # Create a documents list out of all the user uploaded pdf files
            final_docs_list=create_docs(pdf,st.session_state['unique_id'])

            docs = split_docs(final_docs_list)
            
            # Displaying the count of resumes that have been uploaded
            st.write("*Resumes uploaded* :"+str(len(docs)))
            
            # Create embeddings instance
            embeddings=create_embeddings_load_data()

            # Push data to Vector Store
            db=push_to_store(embeddings,docs)

            # Fectch relevant documents from Vector Store
            relevant_docs=get_similar_docs(enquiry,document_count,db, embeddings,st.session_state['unique_id'])

            #st.write(relevant_docs)

            # Introducing a line separator
            st.write(":heavy_minus_sign:" * 30)

            # For each item in relevant docs - we are displaying some info of it on the UI
            for item in range(len(relevant_docs)):
                
                st.subheader("👉 "+str(item+1))

                # Displaying Filepath
                st.write("**File** : "+relevant_docs[item].metadata['name'])

                # Introducing Expander feature
                with st.expander('Show me 👀'): 
                    # Gets the summary of the current item using 'get_summary' function that we have created which uses LLM & Langchain chain
                    summary = get_summary(relevant_docs[item])
                    st.write("**Summary** : "+summary)

            # Get the answer
            combined_text = combined_doc(relevant_docs)          
            answer = question_answer(combined_text, enquiry)
            st.write(answer)
            st.success("J.A.R.V.I.S: Hope I am able to help you in respond to your client effectively ❤️ ")


# Invoking main function
if __name__ == '__main__':
    main()
