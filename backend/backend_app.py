from flask import Flask, jsonify, request
from flask_cors import CORS

"""
A simple Flask-based blog API that supports CRUD operations and search functionality.

Endpoints:
- GET /api/posts: Retrieve all posts, optionally sorted by title or content.
- POST /api/posts: Create a new post.
- DELETE /api/posts/<id>: Delete a post by ID.
- PUT /api/posts/<id>: Update a post by ID.
- GET /api/posts/search: Search posts by title and/or content.

Sorting:
- Accepts query parameters 'sort' (title/content) and 'direction' (asc/desc).
Searching:
- Accepts query parameters 'title' and 'content' for case-insensitive search.
"""

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all blog posts.

    Optional query parameters:
    - sort (str): Field to sort by ('title' or 'content').
    - direction (str): Sort order ('asc' or 'desc'). Defaults to 'asc'.

    Returns:
        JSON list of blog posts, sorted if parameters are provided.
        If parameters are invalid, returns a 400 error.
    """
    sort_field = request.args.get("sort", "").lower()
    direction = request.args.get("direction", "asc").lower()

    if not sort_field:
        return jsonify(POSTS)

    if sort_field not in ["title", "content"]:
        return jsonify({"error": "Invalid sort field. Must be 'title' or 'content'"}), 400
    if direction not in ["asc", "desc"]:
        return jsonify({"error": "Invalid direction. Must be 'asc' or 'desc'"}), 400

    reverse = direction == "desc"
    sorted_posts = sorted(POSTS, key=lambda post: post[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts)


@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Create a new blog post.

    Expected JSON body:
    {
        "title": "<post title>",
        "content": "<post content>"
    }

    Returns:
        JSON object of the created post with a new unique ID and status 201.
        If required fields are missing, returns a 400 error.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request must be JSON"}), 400

    title = data.get("title")
    content = data.get("content")

    missing_fields = []
    if not title:
        missing_fields.append("title")
    if not content:
        missing_fields.append("content")

    if missing_fields:
        return jsonify({
            "error": f"Missing required field(s): {', '.join(missing_fields)}"
        }), 400

    new_id = max([post["id"] for post in POSTS], default=0) + 1
    new_post = {"id": new_id, "title": title, "content": content}
    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete a blog post by ID.

    Args:
        post_id (int): The ID of the post to delete.

    Returns:
        JSON message confirming deletion with status 200.
        If post not found, returns a 404 error.
    """
    global POSTS
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)

    if not post_to_delete:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    POSTS = [post for post in POSTS if post["id"] != post_id]

    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."})


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update an existing blog post by ID.

    Args:
        post_id (int): The ID of the post to update.

    Expected JSON body (both fields optional):
    {
        "title": "<new title>",
        "content": "<new content>"
    }

    Returns:
        JSON object of the updated post with status 200.
        If post not found, returns a 404 error.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request must be JSON"}), 400

    post_to_update = next((post for post in POSTS if post["id"] == post_id), None)

    if not post_to_update:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    title = data.get("title", post_to_update["title"])
    content = data.get("content", post_to_update["content"])

    post_to_update["title"] = title
    post_to_update["content"] = content

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search blog posts by title and/or content.

    Query parameters:
    - title (str, optional): Search term for post titles.
    - content (str, optional): Search term for post content.

    Returns:
        JSON list of posts matching the search terms.
        If no matches, returns an empty list.
    """
    title_query = request.args.get("title", "").lower()
    content_query = request.args.get("content", "").lower()

    results = []
    for post in POSTS:
        title_match = title_query in post["title"].lower() if title_query else False
        content_match = content_query in post["content"].lower() if content_query else False

        if title_match or content_match:
            results.append(post)

    return jsonify(results)


if __name__ == '__main__':
    """
    Starts the Flask application on host 0.0.0.0 and port 5002.
    """
    app.run(host="0.0.0.0", port=5002, debug=True)