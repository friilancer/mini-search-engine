import tantivy
import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()

INDEX_PATH = os.getenv("INDEX_PATH")

# Create the Tantivy index schema
def create_index():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    index_path = os.path.join(base_dir, '..', INDEX_PATH)
    try: 
        if not os.path.exists(index_path):
            print(f"Creating folder for index at: {index_path}")
            os.makedirs(index_path, exist_ok=True)
        print(f"Index found at {index_path}. Loading existing index...")
        index = tantivy.Index.open(index_path)
        return index
    except Exception as e:
        print(f"Failed to load index at {index_path}. Creating new index... {e}")
        schema_builder = tantivy.SchemaBuilder()
        schema_builder.add_text_field("title", stored=True)
        schema_builder.add_text_field("snippet", stored=True, tokenizer_name='en_stem')
        schema_builder.add_text_field("url", stored=True)
        schema = schema_builder.build()
        index = tantivy.Index(schema, path=index_path)
        return index
    
    
# index data from the db
def index_data(index, db_path="crawler/crawled_data.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, snippet FROM pages")
    rows = cursor.fetchall()

    writer = index.writer()
    for row in rows:
        writer.add_document(
            tantivy.Document(
                title=row[1],
                snippet=row[2],
                url=row[0],
            )
        )
    
    writer.commit()
    conn.close()
    print(f"Indexed {len(rows)} documents.")

if __name__ == "__main__":
    #create the index
    index = create_index()
    #index the crawled data
    index_data(index)

    print("Indexing complete")