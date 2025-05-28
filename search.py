import requests
import time
import logging
from typing import List, Dict, Any, Optional

# Base URL for the Semantic Scholar API
BASE_URL = "https://api.semanticscholar.org/graph/v1"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_request_with_retry(url: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None, 
                           method: str = "GET", max_retries: int = 5, base_delay: float = 1.0) -> Dict[str, Any]:
    """
    Make HTTP request with retry logic for 429 rate limit errors.
    
    Args:
        url: The URL to make the request to
        params: Query parameters for GET requests
        json_data: JSON data for POST requests
        method: HTTP method (GET or POST)
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds, will be exponentially increased
    
    Returns:
        JSON response as dictionary
    
    Raises:
        Exception: If all retries are exhausted or other errors occur
    """
    
    for attempt in range(max_retries + 1):
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, params=params, json=json_data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check if request was successful
            if response.status_code == 200:
                return response.json()
            
            # Handle rate limiting (429 Too Many Requests)
            elif response.status_code == 429:
                if attempt < max_retries:
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit (429). Retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"Rate limit exceeded. Max retries ({max_retries}) exhausted.")
            
            # Handle other HTTP errors
            else:
                response.raise_for_status()
                
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Request timeout. Retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries + 1})")
                time.sleep(delay)
                continue
            else:
                raise Exception("Request timeout. Max retries exhausted.")
        
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Request failed: {e}. Retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries + 1})")
                time.sleep(delay)
                continue
            else:
                raise Exception(f"Request failed after {max_retries} retries: {e}")
    
    raise Exception("Unexpected error in request retry logic")

def search_papers(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for papers using a query string."""
    url = f"{BASE_URL}/paper/search"
    params = {
        "query": query,
        "limit": min(limit, 100),  # API limit is 100
        "fields": "paperId,title,abstract,year,authors,url,venue,publicationTypes,citationCount"
    }
    
    try:
        response_data = make_request_with_retry(url, params=params)
        papers = response_data.get("data", [])
        
        return [
            {
                "paperId": paper.get("paperId"),
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
                "year": paper.get("year"),
                "authors": [{"name": author.get("name"), "authorId": author.get("authorId")} 
                           for author in paper.get("authors", [])],
                "url": paper.get("url"),
                "venue": paper.get("venue"),
                "publicationTypes": paper.get("publicationTypes"),
                "citationCount": paper.get("citationCount")
            } for paper in papers
        ]
    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        return []

def get_paper_details(paper_id: str) -> Dict[str, Any]:
    """Get details of a specific paper."""
    url = f"{BASE_URL}/paper/{paper_id}"
    params = {
        "fields": "paperId,title,abstract,year,authors,url,venue,publicationTypes,citationCount,referenceCount,influentialCitationCount,fieldsOfStudy,publicationDate"
    }
    
    try:
        response_data = make_request_with_retry(url, params=params)
        return {
            "paperId": response_data.get("paperId"),
            "title": response_data.get("title"),
            "abstract": response_data.get("abstract"),
            "year": response_data.get("year"),
            "authors": [{"name": author.get("name"), "authorId": author.get("authorId")} 
                       for author in response_data.get("authors", [])],
            "url": response_data.get("url"),
            "venue": response_data.get("venue"),
            "publicationTypes": response_data.get("publicationTypes"),
            "citationCount": response_data.get("citationCount"),
            "referenceCount": response_data.get("referenceCount"),
            "influentialCitationCount": response_data.get("influentialCitationCount"),
            "fieldsOfStudy": response_data.get("fieldsOfStudy"),
            "publicationDate": response_data.get("publicationDate")
        }
    except Exception as e:
        logger.error(f"Error getting paper details for {paper_id}: {e}")
        return {"error": f"Failed to get paper details: {e}"}

def get_author_details(author_id: str) -> Dict[str, Any]:
    """Get details of a specific author."""
    url = f"{BASE_URL}/author/{author_id}"
    params = {
        "fields": "authorId,name,url,affiliations,paperCount,citationCount,hIndex"
    }
    
    try:
        response_data = make_request_with_retry(url, params=params)
        return {
            "authorId": response_data.get("authorId"),
            "name": response_data.get("name"),
            "url": response_data.get("url"),
            "affiliations": response_data.get("affiliations"),
            "paperCount": response_data.get("paperCount"),
            "citationCount": response_data.get("citationCount"),
            "hIndex": response_data.get("hIndex")
        }
    except Exception as e:
        logger.error(f"Error getting author details for {author_id}: {e}")
        return {"error": f"Failed to get author details: {e}"}

def get_paper_citations(paper_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get citations for a specific paper."""
    url = f"{BASE_URL}/paper/{paper_id}/citations"
    params = {
        "limit": min(limit, 100),  # API limit is 100
        "fields": "contexts,isInfluential,title,authors,year,venue"
    }
    
    try:
        response_data = make_request_with_retry(url, params=params)
        citations = response_data.get("data", [])
        
        return [
            {
                "contexts": citation.get("contexts", []),
                "isInfluential": citation.get("isInfluential"),
                "citingPaper": {
                    "paperId": citation.get("citingPaper", {}).get("paperId"),
                    "title": citation.get("citingPaper", {}).get("title"),
                    "authors": [{"name": author.get("name"), "authorId": author.get("authorId")} 
                               for author in citation.get("citingPaper", {}).get("authors", [])],
                    "year": citation.get("citingPaper", {}).get("year"),
                    "venue": citation.get("citingPaper", {}).get("venue")
                }
            } for citation in citations
        ]
    except Exception as e:
        logger.error(f"Error getting citations for {paper_id}: {e}")
        return []

def get_paper_references(paper_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get references for a specific paper."""
    url = f"{BASE_URL}/paper/{paper_id}/references"
    params = {
        "limit": min(limit, 100),  # API limit is 100
        "fields": "contexts,isInfluential,title,authors,year,venue"
    }
    
    try:
        response_data = make_request_with_retry(url, params=params)
        references = response_data.get("data", [])
        
        return [
            {
                "contexts": reference.get("contexts", []),
                "isInfluential": reference.get("isInfluential"),
                "citedPaper": {
                    "paperId": reference.get("citedPaper", {}).get("paperId"),
                    "title": reference.get("citedPaper", {}).get("title"),
                    "authors": [{"name": author.get("name"), "authorId": author.get("authorId")} 
                               for author in reference.get("citedPaper", {}).get("authors", [])],
                    "year": reference.get("citedPaper", {}).get("year"),
                    "venue": reference.get("citedPaper", {}).get("venue")
                }
            } for reference in references
        ]
    except Exception as e:
        logger.error(f"Error getting references for {paper_id}: {e}")
        return []

def get_citations_and_references(paper_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """Get citations and references for a paper using paper ID."""
    citations = get_paper_citations(paper_id)
    references = get_paper_references(paper_id)
    
    return {
        "citations": citations,
        "references": references
    }

def search_authors(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for authors using a query string."""
    url = f"{BASE_URL}/author/search"
    params = {
        "query": query,
        "limit": min(limit, 100),  # API limit is 100
        "fields": "authorId,name,url,affiliations,paperCount,citationCount,hIndex"
    }
    
    try:
        response_data = make_request_with_retry(url, params=params)
        authors = response_data.get("data", [])
        
        return [
            {
                "authorId": author.get("authorId"),
                "name": author.get("name"),
                "url": author.get("url"),
                "affiliations": author.get("affiliations"),
                "paperCount": author.get("paperCount"),
                "citationCount": author.get("citationCount"),
                "hIndex": author.get("hIndex")
            } for author in authors
        ]
    except Exception as e:
        logger.error(f"Error searching authors: {e}")
        return []

def search_paper_match(query: str) -> Dict[str, Any]:
    """Find the best matching paper using title-based search."""
    url = f"{BASE_URL}/paper/search/match"
    params = {
        "query": query,
        "fields": "paperId,title,abstract,year,authors,url,venue,publicationTypes,citationCount"
    }
    
    try:
        response_data = make_request_with_retry(url, params=params)
        if response_data.get("data"):
            paper = response_data["data"][0]  # Returns single best match
            return {
                "matchScore": paper.get("matchScore"),
                "paperId": paper.get("paperId"),
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
                "year": paper.get("year"),
                "authors": [{"name": author.get("name"), "authorId": author.get("authorId")} 
                           for author in paper.get("authors", [])],
                "url": paper.get("url"),
                "venue": paper.get("venue"),
                "publicationTypes": paper.get("publicationTypes"),
                "citationCount": paper.get("citationCount")
            }
        else:
            return {"error": "No matching paper found"}
    except Exception as e:
        logger.error(f"Error finding paper match: {e}")
        return {"error": f"Failed to find paper match: {e}"}

def get_paper_autocomplete(query: str) -> List[Dict[str, Any]]:
    """Get paper title autocompletion suggestions."""
    url = f"{BASE_URL}/paper/autocomplete"
    params = {
        "query": query[:100]  # API truncates to 100 characters
    }
    
    try:
        response_data = make_request_with_retry(url, params=params)
        matches = response_data.get("matches", [])
        
        return [
            {
                "id": match.get("id"),
                "title": match.get("title"),
                "authorsYear": match.get("authorsYear")
            } for match in matches
        ]
    except Exception as e:
        logger.error(f"Error getting autocomplete: {e}")
        return []

def get_papers_batch(paper_ids: List[str]) -> List[Dict[str, Any]]:
    """Get details for multiple papers using batch API."""
    url = f"{BASE_URL}/paper/batch"
    
    # API limit is 500 papers at a time
    if len(paper_ids) > 500:
        paper_ids = paper_ids[:500]
        logger.warning(f"Paper IDs list truncated to 500 items (API limit)")
    
    params = {
        "fields": "paperId,title,abstract,year,authors,url,venue,publicationTypes,citationCount,referenceCount,influentialCitationCount,fieldsOfStudy,publicationDate"
    }
    
    json_data = {"ids": paper_ids}
    
    try:
        response_data = make_request_with_retry(url, params=params, json_data=json_data, method="POST")
        if isinstance(response_data, list):
            return [
                {
                    "paperId": paper.get("paperId"),
                    "title": paper.get("title"),
                    "abstract": paper.get("abstract"),
                    "year": paper.get("year"),
                    "authors": [{"name": author.get("name"), "authorId": author.get("authorId")} 
                               for author in paper.get("authors", [])],
                    "url": paper.get("url"),
                    "venue": paper.get("venue"),
                    "publicationTypes": paper.get("publicationTypes"),
                    "citationCount": paper.get("citationCount"),
                    "referenceCount": paper.get("referenceCount"),
                    "influentialCitationCount": paper.get("influentialCitationCount"),
                    "fieldsOfStudy": paper.get("fieldsOfStudy"),
                    "publicationDate": paper.get("publicationDate")
                } for paper in response_data if paper  # Filter out None entries
            ]
        else:
            return []
    except Exception as e:
        logger.error(f"Error getting papers batch: {e}")
        return []

def get_authors_batch(author_ids: List[str]) -> List[Dict[str, Any]]:
    """Get details for multiple authors using batch API."""
    url = f"{BASE_URL}/author/batch"
    
    # API limit is 1000 authors at a time
    if len(author_ids) > 1000:
        author_ids = author_ids[:1000]
        logger.warning(f"Author IDs list truncated to 1000 items (API limit)")
    
    params = {
        "fields": "authorId,name,url,affiliations,paperCount,citationCount,hIndex"
    }
    
    json_data = {"ids": author_ids}
    
    try:
        response_data = make_request_with_retry(url, params=params, json_data=json_data, method="POST")
        if isinstance(response_data, list):
            return [
                {
                    "authorId": author.get("authorId"),
                    "name": author.get("name"),
                    "url": author.get("url"),
                    "affiliations": author.get("affiliations"),
                    "paperCount": author.get("paperCount"),
                    "citationCount": author.get("citationCount"),
                    "hIndex": author.get("hIndex")
                } for author in response_data if author  # Filter out None entries
            ]
        else:
            return []
    except Exception as e:
        logger.error(f"Error getting authors batch: {e}")
        return []

def search_snippets(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for text snippets from papers."""
    url = f"{BASE_URL}/snippet/search"
    params = {
        "query": query,
        "limit": min(limit, 1000),  # API limit is 1000
        "fields": "snippet.text,snippet.snippetKind,snippet.section,snippet.snippetOffset"
    }
    
    try:
        response_data = make_request_with_retry(url, params=params)
        data = response_data.get("data", [])
        
        return [
            {
                "score": item.get("score"),
                "snippet": {
                    "text": item.get("snippet", {}).get("text"),
                    "snippetKind": item.get("snippet", {}).get("snippetKind"),
                    "section": item.get("snippet", {}).get("section"),
                    "snippetOffset": item.get("snippet", {}).get("snippetOffset")
                },
                "paper": {
                    "corpusId": item.get("paper", {}).get("corpusId"),
                    "title": item.get("paper", {}).get("title"),
                    "authors": item.get("paper", {}).get("authors", [])
                }
            } for item in data
        ]
    except Exception as e:
        logger.error(f"Error searching snippets: {e}")
        return []

def main():
    """Test function for the API client."""
    try:
        # Search for papers
        search_results = search_papers("machine learning", limit=2)
        print(f"Search results: {search_results}")

        # Get paper details
        if search_results:
            paper_id = search_results[0]['paperId']
            if paper_id:
                paper_details = get_paper_details(paper_id)
                print(f"Paper details: {paper_details}")

                # Get citations and references
                citations_refs = get_citations_and_references(paper_id)
                print(f"Citations count: {len(citations_refs['citations'])}")
                print(f"References count: {len(citations_refs['references'])}")

        # Get author details
        author_id = "1741101"  # Example author ID
        author_details = get_author_details(author_id)
        print(f"Author details: {author_details}")

        # Search for authors
        author_search_results = search_authors("john", limit=2)
        print(f"Author search results: {author_search_results}")

        # Find paper match
        if search_results:
            paper_title = search_results[0]['title']
            paper_match = search_paper_match(paper_title)
            print(f"Paper match: {paper_match}")

        # Get paper autocomplete
        if search_results:
            paper_query = search_results[0]['title'][:10]  # First 10 characters
            autocomplete_results = get_paper_autocomplete(paper_query)
            print(f"Autocomplete results: {autocomplete_results}")

        # Get papers batch
        if search_results:
            paper_ids = [paper['paperId'] for paper in search_results]
            papers_batch = get_papers_batch(paper_ids)
            print(f"Papers batch: {papers_batch}")

        # Get authors batch
        if author_search_results:
            author_ids = [author['authorId'] for author in author_search_results]
            authors_batch = get_authors_batch(author_ids)
            print(f"Authors batch: {authors_batch}")

        # Search snippets
        if search_results:
            snippet_query = search_results[0]['title']
            snippets = search_snippets(snippet_query, limit=2)
            print(f"Snippets: {snippets}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
