from turtle import mode
import streamlit as st
import requests
import httpx


class App:

    BASE_URL = "http://localhost:8000/api/v1"

    def __init__(self):
        self.page = st.sidebar.selectbox(
            "Select page",
            ["Chatbot", "Game Awards QA", "Create Blog", "Convert to JSON", "Novel Agent", "Take note", "Multi-domain Search", "RAG"]
        )
    def run(self):
        if self.page == "Chatbot":
            self.chatbot_component()
        elif self.page == "Game Awards QA":
            self.game_awards_qa_component()
        elif self.page == "Create Blog":
            self.create_blog_component()
        elif self.page == "Convert to JSON":
            self.convert_video_description_to_json_component()
        elif self.page == "Novel Agent":
            self.novel_agent_component()
        elif self.page == "Take note":
            self.take_note_component()
        elif self.page == "Multi-domain Search":
            self.multi_domain_search_component()
        elif self.page == "RAG":
            self.rag_component()

    def chatbot_component(self):

        st.header("Hello from Chatbot")

        if st.button("check", type="primary"):

            url = f"{self.BASE_URL}/bai_tap/chat"
            with st.spinner("loading..."):
                try:
                    response = self.api_stream_service(url, {})
                    st.write_stream(response)
                except Exception as e:
                    st.error(f"Error: {e}")

    def game_awards_qa_component(self):
        
        st.header("🎮 Game Awards QA 2026")
        
        question = st.text_input("Ask about Game Awards:")
        
        if st.button("Ask", type="primary"):
            try:
                url = f"{self.BASE_URL}/bai_tap/game_awards_QA"
                
                payload = {
                    "question": question
                }
                
                with st.spinner("Getting answer..."):
                    response = self.api_stream_service(url, payload)
                    st.write_stream(response)
                    
            except Exception as e:
                st.error(f"Error: {e}")

    def create_blog_component(self):
        
        st.header("✍️ Create Blog with AI")
        
        title = st.text_input("Blog title:")
        
        if st.button("Generate Blog", type="primary"):
            try:
                url = f"{self.BASE_URL}/bai_tap/create_blog_with_ai"
                
                payload = {
                    "title": title,
                }
                
                with st.spinner("Generating blog..."):
                    response = self.api_stream_service(url, payload)
                    st.success("Generate successfully!")
                    st.write_stream(response)
                    
            except Exception as e:
                st.error(f"Error: {e}")

    def convert_video_description_to_json_component(self):
        st.header("🎬 Format Video Description to JSON")
        
        channel_name = st.text_input("Channel Name:")
        video_title = st.text_input("Video Title:")
        views = st.number_input("Views:", min_value=0, value=0)
        upload_date = st.date_input("Upload Date:")
        tags = st.text_input("Tags (comma separated):")
        is_short = st.checkbox("Is YouTube Shorts?")
        description = f"""
        Channel Name: {channel_name}
        Video Title: {video_title}
        Views: {views}
        Upload Date: {upload_date}
        Tags: {tags}
        Is YouTube Shorts: {is_short}
        """.strip()
        
        if st.button("Format to JSON", type="primary"):
            try:
                url = f"{self.BASE_URL}/bai_tap/format_video"
                
                payload = {
                    "description": description
                }
                
                with st.spinner("Formatting to JSON..."):
                    response = self.api_service(url, payload)
                    st.success("Formatted successfully!")
                    st.json(response)
                    
            except Exception as e:
                st.error(f"Error: {e}")

    def take_note_component(self):
        st.header("📝 Take Note")
        
        # Mode selection
        mode = st.radio("Mode", ["📝 Note", "❓ Ask"], horizontal=True)

        button_text = ""
        query = ""
        spinner_text = ""

        if mode == "📝 Note":
            user_input = st.text_area(
                "Note content:", 
                height=200, 
                placeholder="<nội dung ghi chú>"
            )
            query = f"[GHI CHÚ]: {user_input}" 

            button_text = "Save Note"
            spinner_text = "Saving note..."
            
        elif mode == "❓ Ask":
            user_question = st.text_input("Question:", placeholder="<câu hỏi>")
            query = f"[HỎI]: {user_question}"
            button_text = "Ask"
            spinner_text = "Getting answer..."
        
        session_id = st.text_input("Session ID:", value="user_1")
        
        if st.button(button_text, type="primary"):
            try:
                url = f"{self.BASE_URL}/bai_tap/take_note"
                
                payload = {
                    "query": query,
                    "session_id": session_id
                }
                
                with st.spinner(spinner_text):
                    response = self.api_stream_service(url, payload)
                    st.write_stream(response)
                    
            except Exception as e:
                st.error(f"Error: {e}")

    def novel_agent_component(self):
        st.header("📖 Novel Agent")
        
        # Input fields
        title = st.text_input("Novel title:")
        genre = st.selectbox("Genre", ["Fantasy", "Romance", "Sci-Fi", "Mystery", "Horror"])
        style = st.selectbox("Writing Style", ["Classic", "Modern", "Poetic", "Simple"])
        
        if st.button("Generate Novel", type="primary"):
            try:
                params = {
                    "title": title,
                    "genre": genre,
                    "style": style
                }
                
                url = f"{self.BASE_URL}/bai_tap/novel_agent"
                
                payload = {
                    "description": f"Tiêu đề: {title}, Thể loại: {genre}, Phong cách: {style}",
                }  
                
                with st.spinner("Writing novel..."):
                    response = self.api_stream_service(url, payload)
                    st.write_stream(response)
                    
            except Exception as e:
                st.error(f"Error: {e}")

    def multi_domain_search_component(self):
        st.header("🔍 Tìm kiếm đa lĩnh vực")
        query = st.text_input("Nhập câu hỏi (Oscar, Anime, Ballon d'Or):", placeholder="Ví dụ: Ai thắng Oscar 2026?")
        if st.button("Search", type="primary"):
            try:
                url = f"{self.BASE_URL}/bai_tap/search_multi_domain"
                payload = {"query": query}
                with st.spinner("Searching..."):
                    response = self.api_stream_service(url, payload)
                    st.write_stream(response)
            except Exception as e:
                st.error(f"Error: {e}")

    #
    # RAG COMPONENT
    #
    def get_chat_history_from_api(self, session_id):
        """Lấy lịch sử chat từ API"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/langchain/chat_history/{session_id}",
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    return data['data']
                return []
            else:
                st.error(f"Error loading chat history: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return []

    def session_management_component(self):
        """Simple session management - KISS principle"""
        st.subheader("🔑 Session Management")
        session_id = st.text_input(
            "Session ID",
            value="test",
            placeholder="Enter session ID (e.g., user_1, session_abc)",
            help="Session ID persists your chat history"
        )
        if session_id:
            st.success(f"✅ Active Session: `{session_id}`")
            return session_id
        else:
            st.warning("⚠️ Please enter a session ID")
            return None

    def chat_history_component(self, session_id, pending_query=None):
        """Hiển thị lịch sử chat và xử lý streaming response"""
        if not session_id:
            st.info("⚠️ No session ID. Start a conversation to see history.")
            return
        
        # Load existing chat history
        with st.spinner("Loading chat history..."):
            messages = self.get_chat_history_from_api(session_id)
        
        # Show message count or empty state
        if not messages and not pending_query:
            st.info("📭 No chat history yet. Start a conversation!")
            return
        
        if messages:
            st.subheader(f"💬 Chat History ({len(messages)} messages)")
        
        # Add custom CSS for scrollable container with smooth scrolling
        st.markdown("""
        <style>
        .stContainer {
            overflow-y: auto !important;
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
        }
        .stContainer::-webkit-scrollbar {
            width: 8px;
        }
        .stContainer::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        .stContainer::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        .stContainer::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        </style>
        """, unsafe_allow_html=True)
        
        chat_container = st.container(height=400)
        with chat_container:
            # Display existing messages
            for msg in messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', '')
                if role == 'user':
                    with st.chat_message("user"):
                        st.write(content)
                        if timestamp:
                            st.caption(f"🕐 {timestamp}")
                elif role == 'assistant':
                    with st.chat_message("assistant"):
                        st.write(content)
                        if timestamp:
                            st.caption(f"🕐 {timestamp}")
            
            # Handle pending query - show user message and stream AI response
            if pending_query:
                # Show user message immediately
                with st.chat_message("user"):
                    st.write(pending_query)
                
                # Stream AI response within chat history
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    try:
                        with st.spinner("AI is thinking..."):
                            response = self.api_stream_service(
                                f"{self.BASE_URL}/langchain/retrieve_document",
                                {"query": pending_query, "session_id": session_id}
                            )
                            for chunk in response:
                                if chunk:
                                    full_response += chunk
                                    message_placeholder.write(full_response)
                        # st.success("✅ Response generated successfully!")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        message_placeholder.write("Sorry, I encountered an error. Please try again.")

    def rag_chat_component(self):
        """RAG chat component với session management and history"""
        st.header("💬 RAG Chat with Document Context")
        session_id = self.session_management_component()
        if not session_id:
            st.warning("⚠️ Please create or enter a session ID to start chatting")
            return
        
        st.divider()
        
        pending_query = st.session_state.get("rag_pending_query", None)
        
        self.chat_history_component(session_id, pending_query=pending_query)
        
        if pending_query:
            del st.session_state.rag_pending_query
        
        # Chat input - luôn nằm dưới cùng
        query = st.chat_input(
            "Ask a question about your uploaded documents...",
            key="rag_chat_input"
        )
        
        if query:
            st.session_state.rag_pending_query = query
            st.rerun()

    def rag_component(self):
        """Enhanced RAG component với chat interface and document management"""
        st.header("RAG - Retrieval Augmented Generation")
        tab1, tab2 = st.tabs(["📁 Documents", "💬 Chat"])
        with tab1:
            with st.expander("📤 Upload PDF Documents", expanded=True):
                self.pdf_upload_component()
            st.divider()
            self.pdf_file_list_component()
        with tab2:
            self.rag_chat_component()

    def pdf_upload_component(self):
        st.subheader("📤 Upload PDF Documents")

        # Use dynamic key to reset file uploader after upload
        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0

        with st.form("upload_form"):
            files = st.file_uploader(
                "Chọn PDF files để upload",
                type=["pdf"],
                accept_multiple_files=True,
                key=f"pdf_uploader_{st.session_state.uploader_key}"
            )
            submitted = st.form_submit_button("📤 Upload PDF Files")

        if submitted:
            if not files:
                st.warning("⚠️ Vui lòng chọn file PDF trước khi upload")
                return
            with st.spinner("Đang upload PDF..."):
                self.upload_pdf_files(files)
                st.session_state.uploader_key += 1

    def upload_pdf_files(self, files):
        """Upload PDF files với progress tracking"""
        total_files = len(files)
        uploaded_files = []
        failed_files = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, file in enumerate(files):
            status_text.text(f"Đang upload: {file.name}...")
            progress_bar.progress((i + 1) / total_files)

            try:
                if file.type != "application/pdf":
                    failed_files.append(f"{file.name}: Not a PDF")
                    continue

                files_data = [
                    ("files", (file.name, file.getvalue(), file.type))
                ]

                response = requests.post(
                    f"{self.BASE_URL}/storage/files/upload",
                    files=files_data,
                    timeout=600
                )

                if response.status_code == 200:
                    uploaded_files.append(file.name)
                else:
                    failed_files.append(f"{file.name}: {response.text}")

            except Exception as e:
                failed_files.append(f"{file.name}: {str(e)}")

        status_text.text("✅ Upload hoàn tất!")
        self.show_pdf_upload_results(uploaded_files, failed_files)


    def show_pdf_upload_results(self, uploaded, failed):
        """Hiển thị kết quả upload"""
        col1, col2 = st.columns(2)

        with col1:
            st.metric("✅ Thành công", len(uploaded))

        with col2:
            st.metric("❌ Thất bại", len(failed))

        if uploaded:
            # st.success("Upload thành công:")
            for f in uploaded:
                st.write(f"📕 {f}")

        if failed:
            st.error("Upload thất bại:")
            for f in failed:
                st.write(f"❌ {f}")

        if uploaded:
            st.cache_data.clear()
            st.toast(f"✅ Upload {len(uploaded)} file thành công")
            st.rerun()


    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"


    @staticmethod
    @st.cache_data(ttl=60, show_spinner=False)
    def _fetch_pdf_files_cached(base_url, page, page_size):
        """Cached static method to fetch PDF files"""
        try:
            response = requests.get(
                f"{base_url}/storage/files",
                params={"page": page, "page_size": page_size},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("data") and isinstance(data["data"], dict):
                    all_files = data["data"].get("content", [])
                    pdf_files = [
                        f for f in all_files
                        if f.get("file_name", "").lower().endswith(".pdf")
                    ]

                    return {
                        "files": pdf_files,
                        "total": len(pdf_files),
                        "page": page,
                        "page_size": page_size
                    }

                return {"files": [], "total": 0}
            else:
                return None
        except Exception:
            return None

    def get_pdf_files_from_api(self, page=1, page_size=20):
        """Lấy danh sách PDF files từ API (with caching)"""
        return self._fetch_pdf_files_cached(self.BASE_URL, page, page_size)


    def pdf_file_list_component(self):
        """Hiển thị danh sách PDF files đơn giản"""
        st.subheader("📁 Danh sách PDF Files")

        page_size = st.selectbox("PDFs/page", [10, 20, 50], index=1, key="page_size_select")
        current_page = st.number_input("Page", min_value=1, value=1, step=1, key="page_input")

        files_data = self.get_pdf_files_from_api(int(current_page), int(page_size))
        has_files = files_data and files_data.get("files") and len(files_data.get("files", [])) > 0

        total_files = files_data.get("total", 0) if files_data else 0
        total_pages = max(1, (total_files + page_size - 1) // page_size)

        if has_files:
            files = files_data.get("files", [])

            col1, col2 = st.columns(2)
            with col1:
                st.metric("📕 Total PDFs", total_files)
            with col2:
                st.metric("📄 This Page", len(files))

            st.divider()

            for i, file in enumerate(files):
                with st.container():
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.write(f"**{file.get('file_name', 'Unknown')}**")
                        st.caption(
                            f"ID: {file.get('id', 'N/A')} | Created: {file.get('created_at', 'N/A')}"
                        )

                    with col2:
                        if st.button("Delete", key=f"delete_{file.get('id', i)}", help="Delete this file"):
                            self.delete_pdf_file(file.get("id"), file.get("file_name"))

                    st.divider()
        else:
            st.info("No PDF files found. Upload some PDF files to get started!")

        if total_pages > 1:
            st.write(f"**Page {int(current_page)} of {total_pages}**")

        action_cols = st.columns([1, 1])
        with action_cols[0]:
            if st.button("🔄 Refresh", use_container_width=True, key="refresh_btn"):
                st.rerun()

        with action_cols[1]:
            st.caption("Upload form is always visible")

    def delete_pdf_file(self, file_id, file_name):
        """Delete PDF file"""
        try:
            response = requests.delete(
                f"{self.BASE_URL}/storage/files/{file_id}",
                timeout=30
            )

            if response.status_code == 200:
                st.toast(f"✅ Deleted: {file_name}")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"❌ Delete failed: {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"❌ Delete error: {str(e)}")

    def download_pdf_file(self, file_id, file_name):
        """Download PDF file đơn giản"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/storage/files/{file_id}/{file_name}",
                stream=True,
                timeout=60
            )

            if response.status_code == 200:
                st.download_button(
                    label=f"📥 Download {file_name}",
                    data=response.content,
                    file_name=file_name,
                    mime="application/pdf"
                )
            else:
                st.error(f"PDF download failed: {response.status_code}")
        except Exception as e:
            st.error(f"PDF download error: {str(e)}")

    def api_service(self, url, payload):
        res = requests.post(
            url,
            json=payload,
            timeout=60
        )

        if res.status_code != 200:
            raise Exception(f"API error {res.status_code}")

        return res.json()

    def api_stream_service(self, url, payload):

        with httpx.stream(
            "POST",
            url,
            json=payload,
            timeout=75.0
        ) as r:

            for chunk in r.iter_raw():
                yield chunk.decode()

if __name__ == "__main__":
    App().run()