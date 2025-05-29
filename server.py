from typing import Any, List, Dict
import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from search import search_papers, get_paper_details, get_author_details, get_citations_and_references

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize FastMCP server
mcp = FastMCP("semanticscholar")

@mcp.tool()
async def search_semantic_scholar(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    logging.info(f"Searching for papers with query: {query}, num_results: {num_results}")
    """
    Search for papers on Semantic Scholar using a query string.

    Args:
        query: Search query string
        num_results: Number of results to return (default: 10)

    Returns:
        List of dictionaries containing paper information
    """
    try:
        results = await asyncio.to_thread(search_papers, query, num_results)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while searching: {str(e)}"}]

@mcp.tool()
async def get_semantic_scholar_paper_details(paper_id: str) -> Dict[str, Any]:
    logging.info(f"Fetching paper details for paper ID: {paper_id}")
    """
    Get details of a specific paper on Semantic Scholar.

    Args:
        paper_id: ID of the paper

    Returns:
        Dictionary containing paper details
    """
    try:
        paper = await asyncio.to_thread(get_paper_details, paper_id)
        return paper
    except Exception as e:
        return {"error": f"An error occurred while fetching paper details: {str(e)}"}

@mcp.tool()
async def get_semantic_scholar_author_details(author_id: str) -> Dict[str, Any]:
    logging.info(f"Fetching author details for author ID: {author_id}")
    """
    Get details of a specific author on Semantic Scholar.

    Args:
        author_id: ID of the author

    Returns:
        Dictionary containing author details
    """
    try:
        author = await asyncio.to_thread(get_author_details, author_id)
        return author
    except Exception as e:
        return {"error": f"An error occurred while fetching author details: {str(e)}"}

@mcp.tool()
async def get_semantic_scholar_citations_and_references(paper_id: str) -> Dict[str, List[Dict[str, Any]]]:
    logging.info(f"Fetching citations and references for paper ID: {paper_id}")
    """
    Get citations and references for a specific paper on Semantic Scholar.

    Args:
        paper_id: ID of the paper

    Returns:
        Dictionary containing lists of citations and references
    """
    try:
        citations_refs = await asyncio.to_thread(get_citations_and_references, paper_id)
        return citations_refs
    except Exception as e:
        return {"error": f"An error occurred while fetching citations and references: {str(e)}"}

@mcp.tool()
async def search_semantic_scholar_authors(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    logging.info(f"Searching for authors with query: {query}, limit: {limit}")
    """
    Search for authors on Semantic Scholar using a query string.

    Args:
        query: Search query string for author names
        limit: Number of results to return (default: 10, max: 100)

    Returns:
        List of dictionaries containing author information
    """
    try:
        from search import search_authors
        results = await asyncio.to_thread(search_authors, query, limit)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while searching authors: {str(e)}"}]

@mcp.tool()
async def get_semantic_scholar_paper_match(query: str) -> Dict[str, Any]:
    logging.info(f"Finding paper match for query: {query}")
    """
    Find the best matching paper on Semantic Scholar using title-based search.

    Args:
        query: Paper title or partial title to match

    Returns:
        Dictionary containing the best matching paper with match score
    """
    try:
        from search import search_paper_match
        result = await asyncio.to_thread(search_paper_match, query)
        return result
    except Exception as e:
        return {"error": f"An error occurred while finding paper match: {str(e)}"}

@mcp.tool()
async def get_semantic_scholar_paper_autocomplete(query: str) -> List[Dict[str, Any]]:
    logging.info(f"Getting paper autocomplete for query: {query}")
    """
    Get paper title autocompletion suggestions for a partial query.

    Args:
        query: Partial paper title query (will be truncated to 100 characters)

    Returns:
        List of dictionaries containing autocomplete suggestions
    """
    try:
        from search import get_paper_autocomplete
        results = await asyncio.to_thread(get_paper_autocomplete, query)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while getting autocomplete suggestions: {str(e)}"}]

@mcp.tool()
async def get_semantic_scholar_papers_batch(paper_ids: List[str]) -> List[Dict[str, Any]]:
    logging.info(f"Fetching batch paper details for {len(paper_ids)} papers")
    """
    Get details for multiple papers at once using batch API.

    Args:
        paper_ids: List of paper IDs (max 500)

    Returns:
        List of dictionaries containing paper details
    """
    try:
        from search import get_papers_batch
        results = await asyncio.to_thread(get_papers_batch, paper_ids)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while fetching batch paper details: {str(e)}"}]

@mcp.tool()
async def get_semantic_scholar_authors_batch(author_ids: List[str]) -> List[Dict[str, Any]]:
    logging.info(f"Fetching batch author details for {len(author_ids)} authors")
    """
    Get details for multiple authors at once using batch API.

    Args:
        author_ids: List of author IDs (max 1000)

    Returns:
        List of dictionaries containing author details
    """
    try:
        from search import get_authors_batch
        results = await asyncio.to_thread(get_authors_batch, author_ids)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while fetching batch author details: {str(e)}"}]

@mcp.tool()
async def search_semantic_scholar_snippets(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    logging.info(f"Searching for text snippets with query: {query}, limit: {limit}")
    """
    Search for text snippets from papers that match the query.

    Args:
        query: Plain-text search query
        limit: Number of results to return (default: 10, max: 1000)

    Returns:
        List of dictionaries containing snippet matches with paper info
    """
    try:
        from search import search_snippets
        results = await asyncio.to_thread(search_snippets, query, limit)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while searching snippets: {str(e)}"}]

@mcp.tool()
async def get_semantic_scholar_paper_recommendations_from_lists(
    positive_paper_ids: List[str], 
    negative_paper_ids: List[str] = None, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    logging.info(f"Getting paper recommendations from lists: {len(positive_paper_ids)} positive, {len(negative_paper_ids) if negative_paper_ids else 0} negative, limit: {limit}")
    """
    Get recommended papers based on lists of positive and negative example papers.

    Args:
        positive_paper_ids: List of paper IDs that represent positive examples (papers you like/want similar to)
        negative_paper_ids: Optional list of paper IDs that represent negative examples (papers you don't want similar to)
        limit: Number of recommendations to return (default: 10, max: 500)

    Returns:
        List of dictionaries containing recommended papers with relevance scores
    """
    try:
        from search import get_paper_recommendations_from_lists
        results = await asyncio.to_thread(get_paper_recommendations_from_lists, positive_paper_ids, negative_paper_ids, limit)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while getting paper recommendations from lists: {str(e)}"}]

@mcp.tool()
async def get_semantic_scholar_paper_recommendations(paper_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    logging.info(f"Getting paper recommendations for single paper: {paper_id}, limit: {limit}")
    """
    Get recommended papers for a single positive example paper.

    Args:
        paper_id: ID of the paper to get recommendations for (positive example)
        limit: Number of recommendations to return (default: 10, max: 500)

    Returns:
        List of dictionaries containing recommended papers similar to the input paper
    """
    try:
        from search import get_paper_recommendations
        results = await asyncio.to_thread(get_paper_recommendations, paper_id, limit)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while getting paper recommendations for single paper: {str(e)}"}]

if __name__ == "__main__":
    logging.info("Starting Semantic Scholar MCP server")
    # Initialize and run the server
    mcp.run(transport='stdio')
