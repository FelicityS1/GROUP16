// newsfeed.js - Updated with bug fixes and optimized logic
document.addEventListener("DOMContentLoaded", function() {
    console.log("Initializing newsfeed.js");
    
    // DOM references
    const postTextarea = document.querySelector('.create-post textarea');
    const postButton = document.querySelector('.create-post button.btn-primary');
    const fileInput = document.getElementById('image-upload');
    const imagePreview = document.getElementById('image-preview');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const removeImageBtn = document.getElementById('remove-image');
    const logoutLink = document.getElementById('logout-link');
    const addPhotoButton = document.querySelector('.create-post .btn-outline-primary');
    
    // Global variables
    let selectedImage = null;
    window.currentUser = {
        username: "Loading...",
        id: null
    };
    
    // Utility functions
    window.getCookie = function(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    };
    
    window.getTimeAgo = function(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        
        let interval = Math.floor(seconds / 31536000);
        if (interval > 1) return interval + ' years ago';
        if (interval === 1) return '1 year ago';
        
        interval = Math.floor(seconds / 2592000);
        if (interval > 1) return interval + ' months ago';
        if (interval === 1) return '1 month ago';
        
        interval = Math.floor(seconds / 86400);
        if (interval > 1) return interval + ' days ago';
        if (interval === 1) return '1 day ago';
        
        interval = Math.floor(seconds / 3600);
        if (interval > 1) return interval + ' hours ago';
        if (interval === 1) return '1 hour ago';
        
        interval = Math.floor(seconds / 60);
        if (interval > 1) return interval + ' minutes ago';
        if (interval === 1) return '1 minute ago';
        
        if (seconds < 10) return 'just now';
        
        return Math.floor(seconds) + ' seconds ago';
    };
    
    window.fixImageUrl = function(imgElement, originalSrc) {
        console.log('Fixing image URL:', originalSrc);
        
        if (!originalSrc) return;
        
        // Try different URL formats
        if (originalSrc.startsWith('/media/')) {
            // Already has /media/ prefix
            imgElement.src = originalSrc;
        } else if (originalSrc.includes('post_images/')) {
            // Has post_images/ but missing /media/
            imgElement.src = `/media/${originalSrc}`;
        } else {
            // Try a completely different approach - use as-is
            imgElement.src = originalSrc;
        }
        
        // If still fails after attempt, show a placeholder
        imgElement.onerror = function() {
            console.log('Image still failed to load after fix attempt');
            this.onerror = null;
            this.src = 'https://via.placeholder.com/300x200?text=Image+Not+Available';
        };
    };
    
    // Fetch user data
    async function fetchCurrentUser() {
        try {
            const response = await fetch('/posts/current_user/');
            if (response.ok) {
                const userData = await response.json();
                window.currentUser = userData;
                document.querySelectorAll('.sidebar h5').forEach(el => {
                    el.textContent = window.currentUser.username;
                });
            }
        } catch (error) {
            console.error('Error fetching user data:', error);
        }
    }
    
    // Fetch posts
    async function fetchPosts() {
        try {
            const response = await fetch('/posts/api/posts/');
            if (response.ok) {
                const data = await response.json();
                console.log("Fetched posts:", data.posts);
                renderPosts(data.posts);
            }
        } catch (error) {
            console.error('Error fetching posts:', error);
        }
    }
    
    // Render posts
    function renderPosts(posts) {
        const container = document.querySelector('.newsfeed');
        
        // Remove all existing posts except the create-post div
        document.querySelectorAll('.post-card').forEach(post => post.remove());
        
        // If no posts, show a message
        if (!posts || posts.length === 0) {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'post-card';
            emptyMessage.innerHTML = `
                <p class="text-center text-muted my-5">No posts yet. Be the first to post something!</p>
            `;
            document.querySelector('.create-post').insertAdjacentElement('afterend', emptyMessage);
            return;
        }
        
        // Add each post to the newsfeed
        posts.forEach(post => {
            const postElement = createPostElement(post);
            document.querySelector('.create-post').insertAdjacentElement('afterend', postElement);
        });
    }
    
    // Create HTML for a post
    function createPostElement(post) {
        const postCard = document.createElement('div');
        postCard.className = 'post-card';
        postCard.dataset.postId = post.id;
        
        // Format the date
        const postDate = new Date(post.created_at);
        const timeAgo = window.getTimeAgo(postDate);
        
        // Get first letter of username for avatar
        const firstLetter = post.author.charAt(0).toUpperCase();
        
        // Check if the current user is the author of this post
        const isAuthor = window.currentUser.username === post.author;
        
        // Create the post HTML
        postCard.innerHTML = `
            <div class="d-flex align-items-center mb-2">
                <div class="me-2 bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">${firstLetter}</div>
                <div class="flex-grow-1">
                    <strong>${post.author}</strong> <br>
                    <small class="text-muted">${timeAgo}</small>
                </div>
                ${isAuthor ? `
                <div class="dropdown">
                    <button class="btn btn-sm btn-light" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                        ⋮
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item delete-post-btn" href="#" data-post-id="${post.id}">Delete</a></li>
                    </ul>
                </div>` : ''}
            </div>
            <p>${post.content}</p>
            ${post.post_type === 'image' && post.image_url ? `
            <div class="post-image-container mb-3">
                <img src="${post.image_url}" alt="Post image" class="img-fluid rounded post-image" onerror="this.onerror=null; window.fixImageUrl(this, '${post.image_url}');">
            </div>` : ''}
            <div class="d-flex justify-content-between mt-2">
                <button class="btn ${post.user_has_liked ? 'btn-primary' : 'btn-light'} btn-sm like-button" data-post-id="${post.id}">
                    👍 Like${post.like_count > 0 ? ` (${post.like_count})` : ''}
                </button>
                <button class="btn btn-light btn-sm comment-button" data-post-id="${post.id}">
                    💬 Comment${post.comment_count > 0 ? ` (${post.comment_count})` : ''}
                </button>
            </div>
            <div class="comments-section mt-3" style="display: none;">
                <div class="comments-container">
                    <p class="text-muted">No comments yet.</p>
                </div>
                <div class="mt-2">
                    <div class="input-group">
                        <input type="text" class="form-control comment-input" placeholder="Write a comment...">
                        <button class="btn btn-primary post-comment-btn" data-post-id="${post.id}">Post</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        addPostEventListeners(postCard, post.id);
        
        return postCard;
    }
    
    // Add event listeners to post elements
    function addPostEventListeners(postCard, postId) {
        // Like button
        const likeBtn = postCard.querySelector('.like-button');
        if (likeBtn) {
            likeBtn.addEventListener('click', function() {
                likePost(postId);
            });
        }
        
        // Comment button
        const commentBtn = postCard.querySelector('.comment-button');
        if (commentBtn) {
            commentBtn.addEventListener('click', function() {
                toggleComments(postId);
            });
        }
        
        // Post comment button
        const postCommentBtn = postCard.querySelector('.post-comment-btn');
        const commentInput = postCard.querySelector('.comment-input');
        
        // Allow posting comment with Enter key
        if (commentInput) {
            commentInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && this.value.trim()) {
                    postComment(postId, this.value.trim());
                }
            });
        }
        
        if (postCommentBtn) {
            postCommentBtn.addEventListener('click', function() {
                const input = this.closest('.input-group').querySelector('.comment-input');
                if (input && input.value.trim()) {
                    postComment(postId, input.value.trim());
                }
            });
        }
        
        // Delete post button
        const deleteBtn = postCard.querySelector('.delete-post-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('Are you sure you want to delete this post?')) {
                    deletePost(postId);
                }
            });
        }
    }
    
    // Create a new post
    async function createPost(content, image = null) {
        try {
            // Show loading state
            postButton.disabled = true;
            postButton.textContent = 'Posting...';
            
            // Prepare form data for file upload
            const formData = new FormData();
            formData.append('content', content);
            formData.append('post_type', image ? 'image' : 'text');
            
            if (image) {
                formData.append('image', image);
            }
            
            const csrfToken = getCookie('csrftoken');
            
            const response = await fetch('/posts/create_post/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });
            
            console.log("Create post response:", response.status);
            
            if (response.ok) {
                // Clear the form
                postTextarea.value = '';
                if (selectedImage) {
                    selectedImage = null;
                    imagePreview.src = '';
                    imagePreviewContainer.style.display = 'none';
                    fileInput.value = '';
                }
                
                // Fetch updated posts
                fetchPosts();
                return true;
            } else {
                const errorText = await response.text();
                console.error('Failed to create post:', errorText);
                alert('Failed to create post. Please try again.');
                return false;
            }
        } catch (error) {
            console.error('Error creating post:', error);
            alert('Error creating post: ' + error.message);
            return false;
        } finally {
            postButton.disabled = false;
            postButton.textContent = 'Post';
        }
    }
    
    // Like a post
    async function likePost(postId) {
        try {
            const button = document.querySelector(`.like-button[data-post-id="${postId}"]`);
            if (!button) return;
            
            // Show loading state
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '👍 Liking...';
            
            const csrfToken = window.getCookie('csrftoken');
            const response = await fetch(`/posts/${postId}/like/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });
            
            // Reset button appearance
            button.disabled = false;
            
            if (response.ok) {
                const data = await response.json();
                
                // Update button appearance and like count
                if (data.liked) {
                    button.classList.remove('btn-light');
                    button.classList.add('btn-primary');
                } else {
                    button.classList.remove('btn-primary');
                    button.classList.add('btn-light');
                }
                
                // Update the like count
                const likeCount = data.like_count || 0;
                button.innerHTML = likeCount > 0 ? `👍 Like (${likeCount})` : '👍 Like';
            } else {
                button.innerHTML = originalText;
                console.error('Failed to like post:', await response.text());
            }
        } catch (error) {
            console.error('Error liking post:', error);
        }
    }
    
    // Updated fetchComments function with comprehensive endpoint testing
    async function fetchComments(postId) {
        try {
            const commentsContainer = document.querySelector(`.post-card[data-post-id="${postId}"] .comments-container`);
            if (!commentsContainer) return;
            
            // Show loading message
            commentsContainer.innerHTML = '<p class="text-muted">Loading comments...</p>';
            
            console.log("Attempting to fetch comments for post:", postId);
            
            // Try all possible API endpoints for comments
            let response;
            let endpoints = [
                `/api/${postId}/comments/`,
                `/posts/api/${postId}/comments/`,
                `/posts/${postId}/comments/`
            ];
            
            let successEndpoint = null;
            
            for (let endpoint of endpoints) {
                console.log(`Trying endpoint: ${endpoint}`);
                try {
                    response = await fetch(endpoint);
                    if (response.ok) {
                        successEndpoint = endpoint;
                        console.log(`Success with endpoint: ${endpoint}`);
                        break;
                    } else {
                        console.log(`Failed with endpoint: ${endpoint}, status: ${response.status}`);
                    }
                } catch (err) {
                    console.log(`Error with endpoint: ${endpoint}`, err);
                }
            }
            
            if (successEndpoint) {
                const data = await response.json();
                console.log("Comments data received:", data);
                
                // Handle different response formats
                let comments = [];
                
                if (data.comments && Array.isArray(data.comments)) {
                    comments = data.comments;
                } else if (data.success && data.comments && Array.isArray(data.comments)) {
                    comments = data.comments;
                } else if (Array.isArray(data)) {
                    comments = data;
                }
                
                renderComments(postId, comments);
            } else {
                // If we still don't have a working endpoint, try a direct API endpoint
                try {
                    console.log("Attempting one more endpoint for comments");
                    response = await fetch(`/api/${postId.replace(/-/g, '')}/comments/`);
                    
                    if (response.ok) {
                        const data = await response.json();
                        console.log("Comments retrieved with final attempt:", data);
                        
                        // Handle different response formats
                        let comments = [];
                        
                        if (data.comments && Array.isArray(data.comments)) {
                            comments = data.comments;
                        } else if (data.success && data.comments && Array.isArray(data.comments)) {
                            comments = data.comments;
                        } else if (Array.isArray(data)) {
                            comments = data;
                        }
                        
                        renderComments(postId, comments);
                        return;
                    }
                } catch (err) {
                    console.log("Final attempt failed:", err);
                }
                
                // Get the comment count from the button
                const commentBtn = document.querySelector(`.post-card[data-post-id="${postId}"] .comment-button`);
                if (commentBtn) {
                    const countMatch = commentBtn.textContent.match(/\((\d+)\)/);
                    const count = countMatch ? parseInt(countMatch[1], 10) : 0;
                    
                    if (count > 0) {
                        // We have comments but can't retrieve them, show placeholder
                        commentsContainer.innerHTML = `
                            <div class="comment p-2 mb-2 bg-light rounded">
                                <p class="mb-0 text-center">There are ${count} comments on this post.</p>
                                <small class="text-muted text-center d-block">Comments are saved but can't be displayed right now.</small>
                            </div>
                        `;
                    } else {
                        commentsContainer.innerHTML = '<p class="text-muted">No comments yet.</p>';
                    }
                } else {
                    commentsContainer.innerHTML = '<p class="text-muted">Failed to load comments.</p>';
                }
            }
        } catch (error) {
            console.error('Error fetching comments:', error);
            const commentsContainer = document.querySelector(`.post-card[data-post-id="${postId}"] .comments-container`);
            if (commentsContainer) {
                commentsContainer.innerHTML = '<p class="text-muted">Error loading comments.</p>';
            }
        }
    }
    
    // Render comments for a post
    function renderComments(postId, comments) {
        const commentsContainer = document.querySelector(`.post-card[data-post-id="${postId}"] .comments-container`);
        if (!commentsContainer) return;
        
        // Clear any existing comments
        commentsContainer.innerHTML = '';
        
        // Check if comments is empty or not an array
        if (!comments || !Array.isArray(comments) || comments.length === 0) {
            commentsContainer.innerHTML = '<p class="text-muted">No comments yet.</p>';
            return;
        }
        
        console.log(`Rendering ${comments.length} comments for post ${postId}`);
        
        // Add each comment
        comments.forEach((comment, index) => {
            // Skip empty comments
            if (!comment) {
                console.warn(`Skipping empty comment at index ${index}`);
                return;
            }
            
            const commentElement = document.createElement('div');
            commentElement.className = 'comment p-2 mb-2 bg-light rounded';
            
            // Format the date if it exists
            let timeAgo = '';
            if (comment.created_at) {
                const commentDate = new Date(comment.created_at);
                timeAgo = window.getTimeAgo ? window.getTimeAgo(commentDate) : 'recently';
            }
            
            // Handle different comment data structures
            const username = comment.user__username || comment.username || "Anonymous";
            const content = comment.content || "";
            const firstLetter = username.charAt(0).toUpperCase();
            
            commentElement.innerHTML = `
                <div class="d-flex">
                    <div class="me-2 bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 30px; height: 30px;">${firstLetter}</div>
                    <div>
                        <strong>${username}</strong> ${timeAgo ? `<small class="text-muted">${timeAgo}</small>` : ''}
                        <p class="mb-0">${content}</p>
                    </div>
                </div>
            `;
            
            commentsContainer.appendChild(commentElement);
        });
    }
    
    // Post a comment
    async function postComment(postId, content) {
        const postCard = document.querySelector(`.post-card[data-post-id="${postId}"]`);
        const commentInput = postCard?.querySelector('.comment-input');
        const postCommentBtn = postCard?.querySelector('.post-comment-btn');
        
        if (!commentInput || !postCommentBtn || !content) return;
        
        // Show loading state
        const originalText = postCommentBtn.textContent;
        postCommentBtn.disabled = true;
        postCommentBtn.textContent = 'Posting...';
        
        try {
            const csrfToken = window.getCookie('csrftoken');
            
            // Try multiple endpoints for comment posting
            let endpoints = [
                { url: `/api/${postId}/comment/`, method: 'POST' },
                { url: `/posts/${postId}/comment/`, method: 'POST' },
                { url: `/posts/api/${postId}/comment/`, method: 'POST' }
            ];
            
            let response;
            let successEndpoint = null;
            
            for (let endpoint of endpoints) {
                console.log(`Trying to post comment to: ${endpoint.url}`);
                try {
                    response = await fetch(endpoint.url, {
                        method: endpoint.method,
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ content })
                    });
                    
                    if (response.ok) {
                        successEndpoint = endpoint.url;
                        console.log(`Successfully posted comment to: ${endpoint.url}`);
                        break;
                    } else {
                        console.log(`Failed to post comment to ${endpoint.url}: ${response.status}`);
                    }
                } catch (err) {
                    console.log(`Error posting comment to ${endpoint.url}:`, err);
                }
            }
            
            if (successEndpoint) {
                // Success, clear the input
                const data = await response.json();
                console.log("Comment posted successfully:", data);
                
                commentInput.value = '';
                
                // Add new comment to UI immediately
                const commentsContainer = postCard.querySelector('.comments-container');
                const noCommentsMsg = commentsContainer.querySelector('.text-muted');
                
                if (noCommentsMsg) {
                    commentsContainer.innerHTML = '';
                }
                
                const commentElement = document.createElement('div');
                commentElement.className = 'comment p-2 mb-2 bg-light rounded';
                
                const username = window.currentUser.username;
                const firstLetter = username.charAt(0).toUpperCase();
                
                commentElement.innerHTML = `
                    <div class="d-flex">
                        <div class="me-2 bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 30px; height: 30px;">${firstLetter}</div>
                        <div>
                            <strong>${username}</strong> <small class="text-muted">just now</small>
                            <p class="mb-0">${content}</p>
                        </div>
                    </div>
                `;
                
                commentsContainer.appendChild(commentElement);
                
                // Update comment count
                const commentBtn = postCard.querySelector('.comment-button');
                if (commentBtn) {
                    // Get new comment count from response or increment current
                    let count = data.comment_count;
                    if (!count) {
                        // Extract current count
                        const currentText = commentBtn.textContent.trim();
                        const matches = currentText.match(/\((\d+)\)/);
                        count = matches ? parseInt(matches[1], 10) + 1 : 1;
                    }
                    
                    // Update text with new count
                    commentBtn.textContent = `💬 Comment (${count})`;
                }
            } else {
                console.error('All comment posting endpoints failed');
                alert('Failed to post comment. Please try again.');
            }
        } catch (error) {
            console.error('Error posting comment:', error);
            alert('Error posting comment. Please try again.');
        } finally {
            // Reset button state
            postCommentBtn.disabled = false;
            postCommentBtn.textContent = originalText;
        }
    }
    
    // Toggle comments section
    function toggleComments(postId) {
        console.log("Toggling comments for post:", postId);
        const postCard = document.querySelector(`.post-card[data-post-id="${postId}"]`);
        if (!postCard) {
            console.error("Post card not found for ID:", postId);
            return;
        }
        
        const commentsSection = postCard.querySelector('.comments-section');
        if (!commentsSection) {
            console.error("Comments section not found in post card");
            return;
        }
        
        // Toggle display
        if (commentsSection.style.display === 'none') {
            console.log("Opening comments section");
            commentsSection.style.display = 'block';
            fetchComments(postId);
        } else {
            console.log("Closing comments section");
            commentsSection.style.display = 'none';
        }
    }
    
    // Delete a post
    async function deletePost(postId) {
        try {
            const csrfToken = window.getCookie('csrftoken');
            const response = await fetch(`/posts/${postId}/delete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });
            
            if (response.ok) {
                // Remove the post from UI
                const postElement = document.querySelector(`.post-card[data-post-id="${postId}"]`);
                if (postElement) {
                    postElement.remove();
                }
                
                // If no posts left, show a message
                if (!document.querySelector('.post-card')) {
                    const emptyMessage = document.createElement('div');
                    emptyMessage.className = 'post-card';
                    emptyMessage.innerHTML = `
                        <p class="text-center text-muted my-5">No posts yet. Be the first to post something!</p>
                    `;
                    document.querySelector('.create-post').insertAdjacentElement('afterend', emptyMessage);
                }
            } else {
                console.error('Failed to delete post:', await response.text());
                alert('Failed to delete post. Please try again.');
            }
        } catch (error) {
            console.error('Error deleting post:', error);
            alert('Error deleting post. Please try again.');
        }
    }
    
    // Setup image handlers
    function setupImageHandlers() {
        // Handle file selection
        if (fileInput) {
            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    selectedImage = file;
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        imagePreview.src = e.target.result;
                        imagePreviewContainer.style.display = 'block';
                    };
                    
                    reader.readAsDataURL(file);
                }
            });
        }
        
        // Handle "Add Photo" button click
        if (addPhotoButton) {
            addPhotoButton.addEventListener('click', function() {
                // Trigger file input click
                fileInput.click();
            });
        }
        
        // Handle remove image button
        if (removeImageBtn) {
            removeImageBtn.addEventListener('click', function() {
                selectedImage = null;
                imagePreview.src = '';
                imagePreviewContainer.style.display = 'none';
                if (fileInput) fileInput.value = '';
            });
        }
    }
    
    // Event listener for post button
    if (postButton) {
        postButton.addEventListener('click', function() {
            const content = postTextarea.value.trim();
            if (content || selectedImage) {
                createPost(content, selectedImage);
            }
        });
    }
    
    // Event listener for logout
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
    
    // Logout function
    async function logout() {
        try {
            const csrfToken = getCookie('csrftoken');
            
            const response = await fetch('/accounts/logout/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });
            
            if (response.ok || response.redirected) {
                window.location.href = '/login/';
            } else {
                console.error('Logout failed');
            }
        } catch (error) {
            console.error('Error during logout:', error);
        }
    }
    
    // Initialize
    setupImageHandlers();
    fetchCurrentUser();
    fetchPosts();
    
    // Make functions available globally
    window.likePost = likePost;
    window.postComment = postComment;
    window.toggleComments = toggleComments;
    window.fetchComments = fetchComments;
    window.deletePost = deletePost;
    window.createPost = createPost;
    window.fetchPosts = fetchPosts;
});