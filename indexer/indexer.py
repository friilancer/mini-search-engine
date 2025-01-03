import tantivy
import sqlite3
import os


INDEX_PATH = "indexer/search_index/"

# Create the Tantivy index schema
def create_index():
    try: 
        print(f"Index found at {INDEX_PATH}. Loading existing index...")
        index = tantivy.Index.open(INDEX_PATH)
        return index
    except Exception as e:
        print(f"Failed to load index at {INDEX_PATH}. Loading existing index...")
        schema_builder = tantivy.SchemaBuilder()
        schema_builder.add_text_field("title", stored=True)
        schema_builder.add_text_field("snippet", stored=True)
        schema_builder.add_text_field("url", stored=True)
        schema_builder.add_text_field("content", stored=False)
        schema = schema_builder.build()
        index = tantivy.Index(schema, path=INDEX_PATH)
        return index
    
    
# index data from the db
def index_data(index, db_path="crawler/crawled_data.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, snippet FROM Pages")
    rows = cursor.fetchall()

    writer = index.writer()
    for row in rows:
        writer.add_document(
            tantivy.Document(
                title=row[1],
                snippet=row[2],
                url=row[0],
                content=row[2] # Index snippet as content for searching
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