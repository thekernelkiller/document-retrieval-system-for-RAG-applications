# Document Retrieval System for LLM-RAG Applications Using MongoDB, Redis, Flask and ChromaDB. 

This is a Retrieval Augmented Generation (RAG)-like document retrieval system for LLM applications using MongoDB, Redis, Flask, ChromaDB, Sentence Transformers, and other python packages. Minimal LangChain usage (only `langchain_groq` API inference). 

> 1. All packages used are specified in the `requirements.txt` file. 
> 2. Detailed logs (roff), regarding project activity, can be accessed in `logs/` directory. 
> 3. Clear `commit messages` have also been written for project history. 

### Project Architecture

<img width="961" alt="Screenshot 2024-09-15 at 18 30 33" src="https://github.com/user-attachments/assets/30bcdcc4-7bfb-48c6-975d-03c62e5700a5">


### Features & Though Process

1. Functional `/search` POST endpoint that takes input in the following format example:
```json
{

"user_id": "test_user_7",
"text": "Maui wildfire that killed 102 despite warnings",
"top_k": 5,
"threshold": 0.5

}
```
and returns the following results:
```json
{

"debug_info": {
	"cached": true,
	"query": "Maui wildfire that killed 102 despite warnings",
	"query_length": 7,
	"results_count": 1,
	"threshold": 0.5,
	"top_k": 5,
	"total_documents": 20
},
"results": [
	{
	"_id": "66e680cae0b864e6cafacc18",
	"bm25_score": 3.2628875747295774,
	"similarity": 0.6147502461741958,
	"text": "Report finds ‘no evidence’ Hawaii officials prepared for Maui wildfire that killed 102 despite warnings - CNN\nInvestigators reviewing the emergency response to last year’s wildfire that killed 102 people on Maui said in a report released Friday they found “no evidence” Hawaii officials made preparations for it, despite days of warnings that critical fire weather was …\nHonolulu (AP) Investigators reviewing the emergency response to last years wildfire that killed 102 people on Maui said in a report released Friday they found no evidence Hawaii officials made prepar… [+6814 chars]",
	"url": "https://www.cnn.com/2024/09/14/us/hawaii-maui-wildfire-report/index.html"
	}
	]
}
```

2. `/health` GET endpoint returns a simple `200: OK`:
```json
{
	"status": "healthy"
}
```

3. `apscheduler` process runs in the background and starts immediately when the application starts. It uses the `NEWS_API` key and periodically scrapes news articles and adds to a `mongodb` collection.

4. Using `sentence-transformer` encoding model and `chromadb`, a vector index is created from the documents. Both mongodb and the chromadb are in sync to ensure there are no inconsistencies. 

5. I have a `redis` in-memory database to cache frequent requests. This is to enable faster retrievals. 

6. I've implemented hybrid search in `search_service` to enable search for words, as I observed that by regular similarity search methods, I had to type an entire sentence to get grounded results from the chatbot. 

7. `rate limiting` is enabled at user-level and refreshes every 1 hour. 

8. `re-ranking` is implemented using BM25 algorithm to improve search indexing. 

9. the application is dockerisable with separate containers for `backend` and `streamlit` layers. 

### Setup
1. create new conda virtual environment: `conda create --name <venv-name>`
2. activate environment: `conda activate <venv-name>`
3. go to root-level and run: `pip install -r requirements.txt`
4. go to `app/config.py` and place URLs and API KEYS
5. next, to run backend, run: `python -m app.main`
6. to run streamlit app: run: `streamlit run app/streamlit_app.py`
7. for docker, run: `docker-compose up -d --build`

> NOTE: replace line 8 in `app/streamlit_app.py` from `BACKEND_URL = "http://127.0.0.1:5000"` to `BACKEND_URL = "http://backend:5000"` before dockerising. 
