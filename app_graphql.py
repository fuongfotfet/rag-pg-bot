from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry

from services.text_qa import generate_answer

# Data Models
# @strawberry.type
# class Document:
#     text: str


@strawberry.type
class Answer:
    answer: str
    # document_info: Document

# Helper function to fetch vehicle data


def fetch_answer(query: str) -> Answer:
    try:
        index_name = "text_embeddings"
        user_query: str = query

        if not user_query:
            raise ValueError("user_query is required")

        answer: str = generate_answer(user_query, k=3, index_name=index_name)

        return Answer(
            answer=answer,
            # document_info=Document(text=user_query)
        )

    except Exception as e:
        raise ValueError(str(e))

# GraphQL Schema


@strawberry.type
class Query:
    @strawberry.field
    def question(self, query) -> Answer:
        return fetch_answer(query)


schema = strawberry.Schema(query=Query)

# FastAPI app setup
app = FastAPI()
graphql_app = GraphQLRouter(schema)

# Mount GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")

# Run FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
