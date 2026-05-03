import os
import sys
from query_engine import QueryEngine

def main():
    # Database path in the current directory
    db_path = os.path.join(os.path.dirname(__file__), "customer_db.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Error: Database file '{db_path}' not found.")
        return

    print("\n" + "="*50)
    print("🤖 AI CUSTOMER DATABASE CHATBOT")
    print("="*50)
    
    try:
        engine = QueryEngine(db_path)
    except Exception as e:
        print(f"❌ Failed to initialize AI Engine: {e}")
        return

    print("👋 Welcome! Ask me anything about your customer data.")
    print("💡 Examples: 'How many customers are in the UK?', 'Show me the latest subscribers'")
    print("🚪 Type 'exit' or 'quit' to end the session.")
    print("-" * 50)

    while True:
        try:
            # Get user query
            user_input = input("\n👤 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                print("\n👋 Goodbye! Have a great day!")
                break
                
            # Handle empty input
            if not user_input:
                continue

            # Process and stream response
            print("🤖 AI: ", end="", flush=True)
            
            # Iterate through the generator yielded by ask_stream
            for word in engine.ask_stream(user_input):
                print(word, end="", flush=True)
            
            print() # Final newline
            
        except KeyboardInterrupt:
            print("\n\n👋 Session ended by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n\n❌ An error occurred: {e}")
            print("Please try rephrasing your question.")

if __name__ == "__main__":
    main()