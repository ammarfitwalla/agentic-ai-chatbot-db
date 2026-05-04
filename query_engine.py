"""
Query Engine
============
LangGraph agent that converts natural language to SQL queries.

Uses create_react_agent with llama3.1:8b which natively decides whether
to call SQL tools or respond directly — no manual intent routing needed.

Memory:
Conversation history managed manually via _history (rolling window).
Injected as context prefix on each invocation via _build_context().
"""

from langchain_community.utilities      import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages            import HumanMessage
from langgraph.prebuilt                 import create_react_agent

from ai_config import AIConfig

# ── Domain knowledge ───────────────────────────────────────────────────────────

CUSTOMER_DATA_GLOSSARY = """
CUSTOMER DATABASE DOMAIN KNOWLEDGE:
====================================

PRIMARY TABLE: customers
(This is the main table — query this for all customer information)

COLUMNS:
- customer_index    : internal sequence number
- customer_id       : unique customer identifier (e.g. 'dE0143891c9a88B')
- first_name        : customer's first name
- last_name         : customer's last name
- company           : company the customer works for
- city              : city of residence
- country           : country of residence
- phone1            : primary phone number
- phone2            : secondary phone number
- email             : primary email address
- subscription_date : date the customer subscribed (YYYY-MM-DD)
- website           : customer's or company's website

COMMON QUERY PATTERNS:
- "count by country"      → SELECT country, COUNT(*) FROM customers GROUP BY country
- "latest subscribers"    → SELECT * FROM customers ORDER BY subscription_date DESC LIMIT 10
- "customers in a city"   → WHERE city = 'New York'
- "find by company"       → WHERE company LIKE '%Global%'
- "search by name"        → WHERE first_name = 'John' AND last_name = 'Doe'
"""

SYSTEM_PROMPT = f"""
You are an AI assistant for a customer database application.
You help users query their customer data using natural language.

WHAT YOU CAN DO:
- Answer questions about customer data in plain English
- Query the database and explain results in business terms
- Segment customers by country, city, or company
- Calculate counts and identify trends in subscriptions
- Find specific customers by name, email, or ID
- Explain customer data fields (subscription_date, customer_id, etc.)

WHAT YOU CANNOT DO:
- Access data outside this application's database
- Modify, insert, or delete any data
- Connect to the internet or external sources

{CUSTOMER_DATA_GLOSSARY}

RULES:
1. Only generate SELECT queries — never INSERT, UPDATE, DELETE or DROP
2. Always LIMIT results to {AIConfig.MAX_RESULTS} rows unless user specifies otherwise
3. If a SQL query fails, explain the error in simple terms and suggest rephrasing
4. If a query is ambiguous, make a reasonable assumption and state it clearly
5. Always explain results in plain business terms — never show raw SQL to the user
6. If no results are found, explain why and suggest alternatives
7. Do not hallucinate data — only report what you retrieve from the database
8. Always execute the query using tools and report the actual results
9. For trends or segments, calculate them from the data you retrieve
10. Always verify that columns you need exist before writing the query
"""

# ── Engine ─────────────────────────────────────────────────────────────────────

class QueryEngine:
    """
    Wraps LangGraph create_react_agent with manual conversation memory.

    The model natively decides whether to call SQL tools or respond directly
    — no manual intent routing needed.

    Memory:
        _history: rolling list of (question, answer) tuples.
        Injected as context prefix via _build_context() on every call.
        Pruned to last MEMORY_WINDOW entries after each exchange.
    """

    def __init__(self, db_path: str):
        self.db_path  = db_path
        self._agent   = None
        self._history = []
        self._setup()

    # ── Setup ──────────────────────────────────────────────────────────────────

    def _setup(self):
        try:
            print("🔧 Setting up AI Query Engine...")

            llm = AIConfig.get_llm()
            print(f"   LLM   : {AIConfig.PROVIDER} / {AIConfig.OLLAMA_MODEL}")

            # DB — read-only, only customers exposed
            uri = f"sqlite:///file:{self.db_path}?mode=ro&uri=true"
            db  = SQLDatabase.from_uri(
                uri,
                sample_rows_in_table_info = 0,
                include_tables            = ['customers']
            )
            print(f"   DB    : {len(db.get_usable_table_names())} table(s) loaded")

            # Tools — sql_db_query, sql_db_schema, sql_db_list_tables, sql_db_query_checker
            toolkit = SQLDatabaseToolkit(db=db, llm=llm)
            tools   = toolkit.get_tools()
            print(f"   Tools : {[t.name for t in tools]}")

            # Agent — native tool calling, model decides when to query DB
            self._agent = create_react_agent(
                model  = llm,
                tools  = tools,
                prompt = SYSTEM_PROMPT,
            )

            print("✅ Query Engine ready\n")

        except Exception as e:
            print(f"❌ Query Engine setup failed: {e}")
            raise

    # ── Public API ─────────────────────────────────────────────────────────────

    def ask_stream(self, question: str):
        """
        Process question and yield answer word by word.

        The agent internally decides whether to call SQL tools or respond
        directly — greetings, concept questions, and data queries all handled
        by the model without any pre-filtering.
        """
        try:
            context  = self._build_context(question)
            response = self._agent.invoke({
                "messages": [("human", context)]
            })
            answer = response["messages"][-1].content

            # print(f"✅ Answer: {answer[:200]}")

            # Store in rolling history window
            self._history.append((question, answer))
            if len(self._history) > AIConfig.MEMORY_WINDOW:
                self._history = self._history[-AIConfig.MEMORY_WINDOW:]

            # Yield word by word to simulate streaming in UI
            for word in answer.split(" "):
                yield word + " "

        except Exception as e:
            print(f"❌ Query failed: {e}")
            yield f"\n\n❌ Error: {str(e)}"

    def reset_memory(self):
        """Clear all conversation history."""
        self._history = []
        print("🔄 Conversation memory cleared")

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _build_context(self, question: str) -> str:
        """Prepend recent conversation history for follow-up question support."""
        if not self._history:
            return question
        history_text = "\n".join(
            f"User: {q}\nAssistant: {a}"
            for q, a in self._history
        )
        return f"Previous conversation:\n{history_text}\n\nCurrent question: {question}"

