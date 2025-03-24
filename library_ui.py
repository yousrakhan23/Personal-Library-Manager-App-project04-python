import streamlit as st # type: ignore
import json
from datetime import datetime
import pandas as pd # type: ignore

class BookCollection:
    """A class to manage a collection of books with Streamlit UI"""
    
    def __init__(self):
        self.storage_file = "books_data.json"
        self.book_list = self.read_from_file()
        
    def read_from_file(self):
        """Load books from JSON file"""
        try:
            with open(self.storage_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_to_file(self):
        """Save books to JSON file"""
        with open(self.storage_file, "w") as file:
            json.dump(self.book_list, file, indent=4)
    
    def add_book(self, title, author, year, genre, read):
        """Add a new book to the collection"""
        new_book = {
            "title": title,
            "author": author,
            "year": year,
            "genre": genre,
            "read": read,
            "added_date": datetime.now().strftime("%Y-%m-%d")
        }
        self.book_list.append(new_book)
        self.save_to_file()
        st.success("Book added successfully!")
    
    def delete_book(self, title):
        """Remove a book from the collection"""
        self.book_list = [book for book in self.book_list if book["title"].lower() != title.lower()]
        self.save_to_file()
        st.success("Book removed successfully!")
    
    def update_book(self, original_title, updated_data):
        """Update book details"""
        for book in self.book_list:
            if book["title"].lower() == original_title.lower():
                book.update(updated_data)
                self.save_to_file()
                st.success("Book updated successfully!")
                return True
        return False
    
    def search_books(self, search_term=""):
        """Search books by title or author"""
        if not search_term:
            return self.book_list
        return [
            book for book in self.book_list
            if search_term.lower() in book["title"].lower() or 
               search_term.lower() in book["author"].lower()
        ]
    
    def get_reading_stats(self):
        """Calculate reading statistics"""
        total = len(self.book_list)
        read = sum(1 for book in self.book_list if book["read"])
        unread = total - read
        return {
            "total": total,
            "read": read,
            "unread": unread,
            "completion_rate": (read / total * 100) if total > 0 else 0
        }
    
    def get_genre_distribution(self):
        """Get genre distribution"""
        genres = {}
        for book in self.book_list:
            genre = book["genre"]
            genres[genre] = genres.get(genre, 0) + 1
        return genres

# Streamlit UI
def main():
    st.set_page_config(
        page_title="📚 Personal Library Manager",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for styling
    st.markdown("""
    <style>
        .main { background-color: #f5f5f5; }
        .sidebar .sidebar-content { background-color: #e8f4f8; }
        h1 { color: #2c3e50; }
        h2 { color: #3498db; }
        .book-card { 
            padding: 15px; 
            border-radius: 10px; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
            margin-bottom: 15px; 
            background-color: white;
        }
        .stats-card { 
            padding: 15px; 
            border-radius: 10px; 
            background-color: #e3f2fd; 
            margin-bottom: 15px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    book_manager = BookCollection()
    
    st.title("📚 Personal Library Manager")
    st.markdown("---")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        menu_option = st.radio("Choose an option:", [
            "🏠 Home",
            "➕ Add Book",
            "🔍 Search Books",
            "✏️ Edit Book",
            "🗑️ Delete Book",
            "📊 Statistics"
        ])
        
        st.markdown("---")
        st.header("Quick Stats")
        stats = book_manager.get_reading_stats()
        st.metric("Total Books", stats["total"])
        st.metric("Books Read", stats["read"])
        st.metric("Completion Rate", f"{stats['completion_rate']:.1f}%")
    
    # Home Page
    if menu_option == "🏠 Home":
        st.header("Your Book Collection")
        
        if not book_manager.book_list:
            st.info("Your library is empty. Add some books to get started!")
        else:
            cols = st.columns([3, 1, 1, 1, 1])
            cols[0].subheader("Title")
            cols[1].subheader("Author")
            cols[2].subheader("Year")
            cols[3].subheader("Genre")
            cols[4].subheader("Status")
            
            for book in book_manager.book_list:
                cols = st.columns([3, 1, 1, 1, 1])
                cols[0].write(book["title"])
                cols[1].write(book["author"])
                cols[2].write(book["year"])
                cols[3].write(book["genre"])
                status = "✅ Read" if book["read"] else "📖 Unread"
                cols[4].write(status)
                
                # Divider
                st.markdown("---")
    
    # Add Book Page
    elif menu_option == "➕ Add Book":
        st.header("Add a New Book")
        
        with st.form("add_book_form"):
            col1, col2 = st.columns(2)
            title = col1.text_input("Title*", placeholder="Book title")
            author = col2.text_input("Author*", placeholder="Author name")
            
            col1, col2 = st.columns(2)
            year = col1.text_input("Publication Year", placeholder="YYYY")
            genre = col2.text_input("Genre", placeholder="Fiction, Science, etc.")
            
            read_status = st.checkbox("I have read this book")
            
            if st.form_submit_button("Add Book"):
                if title and author:
                    book_manager.add_book(title, author, year, genre, read_status)
                else:
                    st.error("Title and Author are required fields")
    
    # Search Books Page
    elif menu_option == "🔍 Search Books":
        st.header("Search Your Library")
        
        search_term = st.text_input("Search by title or author", "")
        
        if search_term:
            results = book_manager.search_books(search_term)
            if results:
                st.success(f"Found {len(results)} matching books:")
                
                for book in results:
                    with st.expander(f"{book['title']} by {book['author']}"):
                        col1, col2 = st.columns(2)
                        col1.write(f"**Year:** {book['year']}")
                        col1.write(f"**Genre:** {book['genre']}")
                        col2.write(f"**Status:** {'Read' if book['read'] else 'Unread'}")
            else:
                st.warning("No matching books found")
        else:
            st.info("Enter a search term to find books in your library")
    
    # Edit Book Page
    elif menu_option == "✏️ Edit Book":
        st.header("Edit Book Details")
        
        if not book_manager.book_list:
            st.info("Your library is empty. Add some books first!")
        else:
            book_titles = [book["title"] for book in book_manager.book_list]
            selected_title = st.selectbox("Select a book to edit", book_titles)
            
            selected_book = next(book for book in book_manager.book_list if book["title"] == selected_title)
            
            with st.form("edit_book_form"):
                new_title = st.text_input("Title", value=selected_book["title"])
                new_author = st.text_input("Author", value=selected_book["author"])
                
                col1, col2 = st.columns(2)
                new_year = col1.text_input("Publication Year", value=selected_book["year"])
                new_genre = col2.text_input("Genre", value=selected_book["genre"])
                
                new_read_status = st.checkbox("I have read this book", value=selected_book["read"])
                
                if st.form_submit_button("Update Book"):
                    updated_data = {
                        "title": new_title,
                        "author": new_author,
                        "year": new_year,
                        "genre": new_genre,
                        "read": new_read_status
                    }
                    book_manager.update_book(selected_title, updated_data)
    
    # Delete Book Page
    elif menu_option == "🗑️ Delete Book":
        st.header("Delete a Book")
        
        if not book_manager.book_list:
            st.info("Your library is empty. There are no books to delete!")
        else:
            book_titles = [book["title"] for book in book_manager.book_list]
            selected_title = st.selectbox("Select a book to delete", book_titles)
            
            if st.button("Delete Book", type="primary"):
                book_manager.delete_book(selected_title)
                st.experimental_rerun()
    
    # Statistics Page
    elif menu_option == "📊 Statistics":
        st.header("Library Statistics")
        
        stats = book_manager.get_reading_stats()
        genre_dist = book_manager.get_genre_distribution()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Books", stats["total"])
        col2.metric("Books Read", stats["read"])
        col3.metric("Completion Rate", f"{stats['completion_rate']:.1f}%")
        
        st.markdown("---")
        
        # Reading Progress Chart (using Streamlit native)
        st.subheader("Reading Progress")
        progress_data = pd.DataFrame({
            "Status": ["Read", "Unread"],
            "Count": [stats["read"], stats["unread"]]
        })
        st.bar_chart(progress_data.set_index("Status"))
        
        # Genre Distribution Chart (using Streamlit native)
        if genre_dist:
            st.subheader("Genre Distribution")
            genre_df = pd.DataFrame({
                "Genre": list(genre_dist.keys()),
                "Count": list(genre_dist.values())
            })
            st.bar_chart(genre_df.set_index("Genre"))

if __name__ == "__main__":
    main()