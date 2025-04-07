document.addEventListener('DOMContentLoaded', function() {
    // User authentication and role management
    const userRole = localStorage.getItem('userRole') || 'user';
    const userNameElement = document.getElementById('userName');
    const postForm = document.getElementById('postForm');
    const postContainer = document.getElementById('postContainer');
    const adminPanel = document.getElementById('adminPanel');
    const moderationPanel = document.getElementById('moderationPanel');
    const paginationContainer = document.getElementById('paginationContainer');

    // Pagination state
    let currentPage = 1;
    const pageSize = 10; // Number of posts per page

    // Function to show/hide elements based on user role
    function configureAccessByRole() {
        // Fetch current user details
        fetch('/current_user/')
            .then(response => response.json())
            .then(userData => {
                // Update username display
                if (userNameElement) {
                    userNameElement.textContent = userData.username;
                }

                // Configure access based on role
                const role = userData.role.toLowerCase();

                // Admin specific elements
                if (adminPanel) {
                    adminPanel.style.display = (role === 'admin') ? 'block' : 'none';
                }

                // Moderation specific elements
                if (moderationPanel) {
                    moderationPanel.style.display = (role === 'admin' || role === 'moderator') ? 'block' : 'none';
                }

                // Post creation form
                if (postForm) {
                    // Guests might be restricted from posting
                    postForm.style.display = (role === 'guest') ? 'none' : 'block';
                }

                // Load appropriate content
                loadPosts(role, currentPage);
            })
            .catch(error => {
                console.error('Error fetching user details:', error);
                // Fallback to default user view
                loadPosts(userRole, currentPage);
            });
    }

    // Function to load posts with pagination
    function loadPosts(role, page = 1) {
        fetch(`/get_posts/?page=${page}&page_size=${pageSize}`)
            .then(response => response.json())
            .then(data => {
                // Clear existing posts
                if (postContainer) {
                    postContainer.innerHTML = '';

                    // Render posts with role-specific visibility
                    data.posts.forEach(post => {
                        const postElement = createPostElement(post, role);
                        if (postElement) {
                            postContainer.appendChild(postElement);
                        }
                    });

                    // Render pagination controls
                    renderPagination(data.pagination, role);
                }
            })
            .catch(error => {
                console.error('Error loading posts:', error);
                if (postContainer) {
                    postContainer.innerHTML = '<p>Unable to load posts. Please try again later.</p>';
                }
            });
    }

    // Render pagination controls
    function renderPagination(paginationData, role) {
        if (paginationContainer) {
            paginationContainer.innerHTML = `
                <button id="prevPage" ${!paginationData.has_previous ? 'disabled' : ''}>
                    Previous
                </button>
                <span>Page ${paginationData.current_page} of ${paginationData.total_pages}</span>
                <button id="nextPage" ${!paginationData.has_next ? 'disabled' : ''}>
                    Next
                </button>
            `;

            // Previous page button
            const prevButton = document.getElementById('prevPage');
            if (prevButton) {
                prevButton.addEventListener('click', () => {
                    if (paginationData.has_previous) {
                        currentPage--;
                        loadPosts(role, currentPage);
                    }
                });
            }

            // Next page button
            const nextButton = document.getElementById('nextPage');
            if (nextButton) {
                nextButton.addEventListener('click', () => {
                    if (paginationData.has_next) {
                        currentPage++;
                        loadPosts(role, currentPage);
                    }
                });
            }
        }
    }

    // Function to create post element with role-based interactions
    function createPostElement(post, userRole) {
        const postDiv = document.createElement('div');
        postDiv.classList.add('post');

        // Basic post content
        postDiv.innerHTML = `
            <div class="post-header">
                <span class="post-author">${post.author}</span>
                <span class="post-date">${new Date(post.created_at).toLocaleString()}</span>
                ${post.privacy ? `<span class="post-privacy">${post.privacy}</span>` : ''}
            </div>
            <div class="post-content">
                ${post.post_type === 'image' && post.image_url 
                    ? `<img src="${post.image_url}" alt="Post image" class="post-image">` 
                    : ''}
                <p>${post.content}</p>
            </div>
            <div class="post-interactions">
                <button class="like-btn ${post.user_has_liked ? 'liked' : ''}">
                    Like (${post.like_count})
                </button>
                <button class="comment-btn">
                    Comment (${post.comment_count})
                </button>
            </div>
        `;

        // Role-specific post interactions
        const likeBtn = postDiv.querySelector('.like-btn');
        const commentBtn = postDiv.querySelector('.comment-btn');

        // Like functionality
        if (likeBtn) {
            likeBtn.addEventListener('click', () => {
                if (userRole === 'guest') {
                    alert('Guests cannot like posts. Please sign up for full access.');
                    return;
                }
                
                fetch(`/like_post/${post.id}/`, {
                    method: 'POST',
                    credentials: 'include'
                })
                .then(response => response.json())
                .then(data => {
                    // Update like count and style
                    likeBtn.classList.toggle('liked');
                    likeBtn.textContent = `Like (${data.like_count || post.like_count})`;
                })
                .catch(error => {
                    console.error('Error liking post:', error);
                });
            });
        }

        // Comment functionality
        if (commentBtn) {
            commentBtn.addEventListener('click', () => {
                if (userRole === 'guest') {
                    alert('Guests cannot comment. Please sign up for full access.');
                    return;
                }
                
                // TODO: Implement comment modal or inline comment section
                console.log('Comment functionality to be implemented');
            });
        }

        // Moderation and admin actions
        if (userRole === 'admin' || userRole === 'moderator') {
            const modActionDiv = document.createElement('div');
            modActionDiv.classList.add('mod-actions');
            modActionDiv.innerHTML = `
                <button class="delete-post-btn">Delete Post</button>
                <button class="hide-post-btn">Hide Post</button>
            `;

            // Delete post functionality
            const deleteBtn = modActionDiv.querySelector('.delete-post-btn');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', () => {
                    fetch(`/delete_post/${post.id}/`, {
                        method: 'POST',
                        credentials: 'include'
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Remove post from DOM
                        postDiv.remove();
                        // Reload current page to maintain pagination
                        loadPosts(userRole, currentPage);
                    })
                    .catch(error => {
                        console.error('Error deleting post:', error);
                    });
                });
            }

            postDiv.appendChild(modActionDiv);
        }

        return postDiv;
    }

    // Post creation handling
    if (postForm) {
        postForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Prevent guests from posting
            if (userRole === 'guest') {
                alert('Guests cannot create posts. Please sign up for full access.');
                return;
            }

            const formData = new FormData(postForm);

            fetch('/create_post/', {
                method: 'POST',
                credentials: 'include',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.post_id) {
                    // Refresh posts or add new post to feed
                    // Reset to first page after creating a post
                    currentPage = 1;
                    loadPosts(userRole, currentPage);
                    postForm.reset();
                } else {
                    console.error('Post creation failed');
                }
            })
            .catch(error => {
                console.error('Error creating post:', error);
            });
        });
    }

    // Admin panel interactions
    if (adminPanel) {
        const userManagementBtn = document.getElementById('userManagementBtn');
        const statisticsBtn = document.getElementById('statisticsBtn');
        const adminContentArea = document.getElementById('adminContentArea');

        if (userManagementBtn) {
            userManagementBtn.addEventListener('click', () => {
                fetch('/admin/get_users/')
                    .then(response => response.json())
                    .then(data => {
                        // Render user management table
                        const userTable = document.createElement('table');
                        userTable.innerHTML = `
                            <thead>
                                <tr>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.users.map(user => `
                                    <tr>
                                        <td>${user.username}</td>
                                        <td>${user.email}</td>
                                        <td>${user.role}</td>
                                        <td>
                                            <select class="role-select" data-user-id="${user.id}">
                                                <option value="user">User</option>
                                                <option value="admin">Admin</option>
                                                <option value="moderator">Moderator</option>
                                                <option value="guest">Guest</option>
                                            </select>
                                            <button class="update-role-btn" data-user-id="${user.id}">Update</button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        `;

                        // Add event listeners for role updates
                        userTable.querySelectorAll('.update-role-btn').forEach(btn => {
                            btn.addEventListener('click', function() {
                                const userId = this.dataset.userId;
                                const roleSelect = userTable.querySelector(`.role-select[data-user-id="${userId}"]`);
                                const newRole = roleSelect.value;

                                fetch(`/admin/update_user_role/${userId}/`, {
                                    method: 'POST',
                                    credentials: 'include',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ role: newRole })
                                })
                                .then(response => response.json())
                                .then(data => {
                                    alert(data.message || 'Role updated successfully');
                                })
                                .catch(error => {
                                    console.error('Error updating role:', error);
                                });
                            });
                        });

                        if (adminContentArea) {
                            adminContentArea.innerHTML = '';
                            adminContentArea.appendChild(userTable);
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching users:', error);
                    });
            });
        }

        if (statisticsBtn) {
            statisticsBtn.addEventListener('click', () => {
                fetch('/admin/get_statistics/')
                    .then(response => response.json())
                    .then(data => {
                        const statsHTML = `
                            <div class="site-statistics">
                                <h3>Site Statistics</h3>
                                <ul>
                                    <li>Total Users: ${data.user_count}</li>
                                    <li>Total Posts: ${data.post_count}</li>
                                    <li>Total Comments: ${data.comment_count}</li>
                                    <li>Total Likes: ${data.like_count}</li>
                                    <li>Public Posts: ${data.public_posts}</li>
                                    <li>Private Posts: ${data.private_posts}</li>
                                    <li>Friends-only Posts: ${data.friends_posts}</li>
                                </ul>
                            </div>
                        `;

                        if (adminContentArea) {
                            adminContentArea.innerHTML = statsHTML;
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching statistics:', error);
                    });
            });
        }
    }

    // Initial setup
    configureAccessByRole();
});